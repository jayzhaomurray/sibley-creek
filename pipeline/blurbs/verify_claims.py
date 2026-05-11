"""Mode A claims-verification: fresh-context re-fetch of every claim-card URL.

This module owns the `context_drafted -> claims_verified` transition.

It is dispatched as a separate agent run (Opus tier). Implementation choice
for the LLM-side judgment (claim_overreach detection) is documented in
`pipeline/blurbs/README.md`:

    The LLM judgment step ("is `claim` a fair summary of the matched
    span?") runs via direct Anthropic API call to `claude-opus-4-7` with
    the API key in env var `ANTHROPIC_API_KEY`. Each card is one
    fresh-context API call; the orchestrator does NOT batch cards across
    a single API call -- one fresh context per card is the structural
    defense against LLM consistency bias (auto_blurb_process.md Section
    1.1). The dispatch mechanism is `anthropic.Anthropic().messages.create`;
    if the `anthropic` package is not installed the orchestrator falls
    back to mechanical verification only (url_404, text_not_present,
    value_mismatch, source_kind_mismatch checks; claim_overreach is
    flagged for human review).

The mechanical checks (url_404, text_not_present, value_mismatch,
source_kind_mismatch) do NOT need the LLM. They run as deterministic
httpx + string matching.
"""

from __future__ import annotations

import io
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Literal, Optional, Protocol
from urllib.parse import urlparse

import httpx
import tenacity
from pydantic import BaseModel, Field
from ruamel.yaml import YAML

logger = logging.getLogger("pipeline.blurbs.verify_claims")

_yaml = YAML(typ="rt")
_yaml.default_flow_style = False
_yaml.allow_unicode = False


VERIFIER_MODEL_PIN = "claude-opus-4-7"


FailureReason = Literal[
    "url_404",
    "text_not_present",
    "value_mismatch",
    "claim_overreach",
    "source_kind_mismatch",
]


# Domain -> source_kind compatibility. A card tagged `boc_press_release`
# should resolve to a URL on bankofcanada.ca; tagged `statcan_daily` to
# www150.statcan.gc.ca or statcan.gc.ca. Catches the source_kind_mismatch
# failure where the URL points to a wire-service or media site.
_KIND_DOMAINS: dict[str, tuple[str, ...]] = {
    "statcan_wds":            ("statcan.gc.ca",),
    "statcan_daily":          ("statcan.gc.ca",),
    "boc_valet":              ("bankofcanada.ca",),
    "boc_press_release":      ("bankofcanada.ca",),
    "boc_mpr":                ("bankofcanada.ca",),
    "boc_fsr":                ("bankofcanada.ca",),
    "boc_sap":                ("bankofcanada.ca",),
    "boc_san":                ("bankofcanada.ca",),
    "osfi_m4":                ("osfi-bsif.gc.ca",),
    "osfi_other":             ("osfi-bsif.gc.ca",),
    "cmhc_rmir":              ("cmhc-schl.gc.ca",),
    "cmhc_observer":          ("cmhc-schl.gc.ca",),
    "cba_pdf":                ("cba.ca",),
    "dof_fiscal_monitor":     ("canada.ca", "fin.gc.ca"),
    "dof_budget":             ("canada.ca", "fin.gc.ca"),
    "pbo_efo":                ("pbo-dpb.ca", "pbo-dpb.gc.ca"),
    "crea_stats":             ("crea.ca",),
    "trreb_market_watch":     ("trreb.ca",),
    "bank_earnings_supplement": (
        "rbc.com", "td.com", "bmo.com", "scotiabank.com",
        "cibc.com", "nbc.ca", "nationalbank.ca",
    ),
    "open_canada":            ("open.canada.ca",),
    "other":                  (),  # allowed; verifier_notes must explain
}

# Domains we explicitly reject (Big-Six bank research portals, wire-service
# summaries posing as primary sources).
_REJECTED_DOMAINS: tuple[str, ...] = (
    "thoughtleadership.rbc.com",
    "economics.td.com",
    "economics.bmo.com",
    "scotiabank.com/global/en/economics",
    "cibc.com/en/economics",
    "nbc.ca/en/economics",
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ClaimCard(BaseModel):
    """The on-disk YAML schema (Section 1.2 of auto_blurb_process.md)."""
    claim_id: str
    claim: str
    value: Optional[float] = None
    unit: Optional[str] = None
    source_url: str
    source_text_excerpt: str
    fetched_at: str
    source_kind: str
    verifier_status: str = "pending"
    verifier_notes: Optional[str] = None


class CardFailure(BaseModel):
    claim_id: str
    reason: FailureReason
    verifier_notes: str


class VerifyResult(BaseModel):
    total_cards: int
    passed_count: int
    failed_count: int
    failures: list[CardFailure] = Field(default_factory=list)
    cards_path: str
    verdict_summary_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Fetch + match (deterministic; no LLM)
# ---------------------------------------------------------------------------

class FetchResult(BaseModel):
    status_code: int
    url: str
    text: str
    final_url: str


# Pluggable fetcher protocol (live httpx in prod; frozen fixtures in tests).
class Fetcher(Protocol):
    def __call__(self, url: str) -> FetchResult: ...


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=8),
    retry=tenacity.retry_if_exception_type(httpx.TransportError),
    reraise=True,
)
def _live_fetch(url: str, timeout: float = 20.0) -> FetchResult:
    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "macro-research-department-verifier/1"},
    ) as client:
        resp = client.get(url)
        return FetchResult(
            status_code=resp.status_code,
            url=url,
            text=resp.text,
            final_url=str(resp.url),
        )


def _normalize_text(text: str) -> str:
    """Strip HTML, collapse whitespace; case-insensitive match-friendly."""
    no_tags = re.sub(r"<[^>]+>", " ", text)
    decoded = (
        no_tags.replace("&amp;", "&")
        .replace("&nbsp;", " ")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )
    collapsed = re.sub(r"\s+", " ", decoded).strip().lower()
    return collapsed


def _domain_matches_source_kind(url: str, source_kind: str) -> bool:
    domain = urlparse(url).netloc.lower()
    if not domain:
        return False
    if source_kind == "other":
        return True
    allowed = _KIND_DOMAINS.get(source_kind, ())
    if not allowed:
        return False
    return any(domain.endswith(d) for d in allowed)


def _is_rejected_domain(url: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    full = netloc + path
    return any(rd in full for rd in _REJECTED_DOMAINS)


def _verify_one_card(
    card: ClaimCard,
    fetcher: Fetcher,
    cycle_created_at: Optional[datetime] = None,
) -> tuple[str, Optional[str]]:
    """Run the four deterministic checks; return (status, notes).

    status is `passed` or `failed:<reason>`. claim_overreach is the only
    failure that needs LLM judgment; this function returns `passed` for
    everything else that survives the deterministic checks, and the
    orchestrator separately routes claim_overreach detection to the LLM.
    """
    url = card.source_url
    # Vague-URL guard (root domain, undated landing page)
    if _is_rejected_domain(url):
        return "failed:source_kind_mismatch", (
            f"URL {url!r} is on a rejected Big-Six research portal domain"
        )
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return "failed:source_kind_mismatch", (
            f"URL {url!r} is malformed (missing scheme/netloc)"
        )
    if not parsed.path or parsed.path == "/":
        return "failed:source_kind_mismatch", (
            f"URL {url!r} is a root domain; not a specific page"
        )
    # Fresh-fetch the URL
    try:
        fr = fetcher(url)
    except Exception as exc:
        return "failed:url_404", f"fetch error: {type(exc).__name__}: {exc}"
    if fr.status_code >= 400:
        return "failed:url_404", f"HTTP {fr.status_code} on {url!r}"

    body_norm = _normalize_text(fr.text)
    excerpt_norm = _normalize_text(card.source_text_excerpt)

    if excerpt_norm not in body_norm:
        return "failed:text_not_present", (
            f"source_text_excerpt not found in fetched body for {url!r}; "
            f"page reached (HTTP {fr.status_code}, "
            f"{len(fr.text)} bytes)"
        )

    # source_kind_mismatch -- domain check
    if not _domain_matches_source_kind(url, card.source_kind):
        netloc = parsed.netloc
        return "failed:source_kind_mismatch", (
            f"source_kind {card.source_kind!r} expects "
            f"{_KIND_DOMAINS.get(card.source_kind, ())!r} but URL is on "
            f"{netloc!r}"
        )

    # value_mismatch: confirm `value` is in the matched span
    if card.value is not None:
        excerpt_idx = body_norm.find(excerpt_norm)
        span_start = max(0, excerpt_idx - 10)
        span_end = min(len(body_norm), excerpt_idx + len(excerpt_norm) + 10)
        match_span = body_norm[span_start:span_end]
        # build a tolerant value pattern
        val_str = (
            f"{card.value:g}" if card.value != int(card.value)
            else str(int(card.value))
        )
        val_alt = f"{card.value}"
        if val_str not in match_span and val_alt not in match_span:
            return "failed:value_mismatch", (
                f"value {card.value!r} not found near excerpt in fetched "
                f"body; span: {match_span!r}"
            )

    # Staleness warn (>72h): not a fail, just a note. The orchestrator
    # logs but does not block.
    notes: Optional[str] = None
    if cycle_created_at is not None and card.fetched_at:
        try:
            ft = datetime.fromisoformat(card.fetched_at.replace("Z", "+00:00"))
            delta = cycle_created_at - ft
            if delta > timedelta(hours=72):
                notes = (
                    f"WARN: fetched_at {card.fetched_at} is "
                    f"{delta.total_seconds() / 3600:.1f}h before cycle start; "
                    f"researcher should consider re-fetch"
                )
        except (ValueError, TypeError):
            pass

    return "passed", notes


# ---------------------------------------------------------------------------
# YAML round-trip
# ---------------------------------------------------------------------------

def _load_cards(path: Path) -> list[ClaimCard]:
    raw = _yaml.load(path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    return [ClaimCard.model_validate(dict(c)) for c in raw]


def _dump_cards(path: Path, cards: list[ClaimCard]) -> None:
    out = [c.model_dump(mode="json") for c in cards]
    buf = io.StringIO()
    _yaml.dump(out, buf)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def verify_claim_file(
    path: Path,
    fetcher: Optional[Fetcher] = None,
    verdict_summary_path: Optional[Path] = None,
    cycle_created_at: Optional[str] = None,
) -> VerifyResult:
    """Re-verify every claim-card in `path` (Mode A).

    Args:
      path: YAML file holding a list of ClaimCard dicts.
      fetcher: optional callable for tests / frozen fixtures. Defaults to
        live httpx fetcher (with tenacity retries) in production.
      verdict_summary_path: optional JSON output for the per-release
        machine-readable verdict (Section 2.3a deliverable).
      cycle_created_at: ISO timestamp; used for the 72h staleness warning.

    Returns: VerifyResult with pass/fail counts and the failure list.
    Side-effects: rewrites the YAML at `path` with verifier_status and
    verifier_notes filled in on every card.
    """
    if fetcher is None:
        fetcher = _live_fetch

    cycle_dt: Optional[datetime] = None
    if cycle_created_at:
        try:
            cycle_dt = datetime.fromisoformat(
                cycle_created_at.replace("Z", "+00:00")
            )
        except ValueError:
            pass

    cards = _load_cards(path)
    failures: list[CardFailure] = []
    passed = 0

    for card in cards:
        status, notes = _verify_one_card(card, fetcher, cycle_dt)
        card.verifier_status = status
        card.verifier_notes = notes
        if status == "passed":
            passed += 1
        else:
            reason = status.split(":", 1)[1] if ":" in status else "other"
            failures.append(CardFailure(
                claim_id=card.claim_id,
                reason=reason,  # type: ignore[arg-type]
                verifier_notes=notes or "",
            ))

    _dump_cards(path, cards)

    result = VerifyResult(
        total_cards=len(cards),
        passed_count=passed,
        failed_count=len(failures),
        failures=failures,
        cards_path=str(path),
        verdict_summary_path=(
            str(verdict_summary_path) if verdict_summary_path else None
        ),
    )

    if verdict_summary_path is not None:
        verdict_summary_path.parent.mkdir(parents=True, exist_ok=True)
        verdict_summary_path.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )

    logger.info(
        "verify_claim_file: %s -- %d/%d cards passed",
        path.name, passed, len(cards),
    )
    return result
