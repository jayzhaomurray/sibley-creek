"""Mode B helpers: draft verification (writer used cards correctly).

This module does NOT re-fetch URLs. That is verify_claims.py (Mode A).
Mode B confirms that every numeric token in the writer's draft maps to a
passed claim-card's `value` (within rounding tolerance) and that no
numeric token is missing a backing card.

Public API:
    extract_numeric_tokens(text) -> list[Token]
    verify_token(token, cards, rounding_tolerance) -> Verdict
    factcheck_body(body, cards, surface_kind, char_cap) -> FactCheckResult
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Numeric extraction
# ---------------------------------------------------------------------------

# Matches: 2.3%, -0.4pp, 25 bps, 1.1, 161.5, $1.1 trillion (number + unit)
# `\d+` (not `\d{1,3}`) so 4-digit years like 2024 match as a single span;
# the year-heuristic in extract_numeric_tokens drops them.
_NUM_PATTERN = re.compile(
    r"""
    (?P<sign>[-+]?)
    (?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)
    \s*
    (?P<unit>%|pp|ppt|bps|bp|p\.p\.|pts?|basis\ points?|percentage\ points?)?
    """,
    re.VERBOSE,
)


class Token(BaseModel):
    raw: str
    value: float
    unit: Optional[str]
    span: tuple[int, int]


def extract_numeric_tokens(text: str) -> list[Token]:
    """Return all numeric tokens in `text`, with values normalized to float.

    Skips:
      - 4-digit years (1900-2099 with no unit)
      - bare small integers with no unit (e.g. "1-3%" range yields token "1"
        and token "-3%"; we keep "-3%" and drop "1" as range-low-end noise)
      - integers that are part of a hyphenated range (next char is "-" + digit)
      - integers preceded by hyphen that's preceded by digit (range high-end
        with no unit, e.g. "2024H2" partial). We DO keep the high-end if it
        carries a unit, since "1-3%" should resolve to a card on the BoC
        control band; the writer's prose carries the unit on the high end.
    """
    out: list[Token] = []
    for m in _NUM_PATTERN.finditer(text):
        num_str = m.group("num").replace(",", "")
        sign = m.group("sign") or ""
        try:
            value = float(sign + num_str)
        except ValueError:
            continue
        unit = m.group("unit")
        if unit:
            unit = unit.strip().lower()
        start, end = m.start(), m.end()
        head = text[max(0, start - 16): start]
        tail = text[end: end + 4]

        # Year heuristic. A 4-digit integer 1900-2099 with no unit is a
        # year. We drop it unconditionally; year references are calendar
        # facts, not numerics in need of card-backing.
        if unit is None and "." not in num_str and 1900 <= value <= 2099:
            if len(num_str) == 4:
                continue
            head_low = head.lower()
            if any(k in head_low for k in (" in ", "since ", "from ", "q", "fy", "the ", "of ", "late ", "early ")):
                continue

        # Bare integer with no unit + part of a hyphenated range
        # (e.g. "1-3%": the "1" before "-" is range low-end)
        if unit is None and "." not in num_str and not sign:
            if tail.startswith("-") and len(tail) > 1 and tail[1].isdigit():
                continue
            # Tiny bare integers carry no real anchor for fact-check; the
            # writer's prose-level integers like "the eleventh month" are
            # not backed by a card by design.
            if value < 100:
                continue

        # Negative range high-end ("1-3%": "-3" matched). Keep but
        # normalize: the sign came from the range hyphen, not a true
        # minus. Convert to positive when unit is present and the
        # preceding context is digit-hyphen.
        if sign == "-" and head.endswith(tuple(str(d) for d in range(10))):
            if unit:
                # rewrite as the absolute value
                value = abs(value)
                # but tag in unit-prefixed form
            else:
                # range integer with no unit: skip
                continue

        out.append(Token(
            raw=m.group(0),
            value=value,
            unit=unit,
            span=(start, end),
        ))
    return out


# ---------------------------------------------------------------------------
# Card-card verification
# ---------------------------------------------------------------------------

class ClaimCardLike(BaseModel):
    """Pydantic projection of a verified claim-card.

    We accept the YAML loaded shape directly; only the load-bearing fields
    are required for Mode B.
    """
    claim_id: str
    claim: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    verifier_status: Optional[str] = None


class TokenVerdict(BaseModel):
    token: str
    value: float
    unit: Optional[str]
    backing_claim_id: Optional[str]
    source_value: Optional[float]
    match_status: str  # 'match' | 'no_backing_card' | 'rounding_mismatch'


class FactCheckResult(BaseModel):
    ok: bool
    surface_id: str
    char_cap: int
    body_chars: int
    tk_leakage: bool
    cap_exceeded: bool
    tokens: list[TokenVerdict] = []
    issues: list[str] = []


def _values_match(a: float, b: float, tolerance: float = 0.05) -> bool:
    return abs(a - b) <= tolerance


def verify_token(
    token: Token,
    cards: list[ClaimCardLike],
    rounding_tolerance: float = 0.05,
) -> TokenVerdict:
    """Try to find a passing card whose `value` matches `token.value`.

    rounding_tolerance is in the same units as the token. Default 0.05 is
    appropriate for percentage-point values rounded to one decimal place.
    """
    for card in cards:
        if card.verifier_status != "passed":
            continue
        if card.value is None:
            continue
        if _values_match(token.value, float(card.value), rounding_tolerance):
            return TokenVerdict(
                token=token.raw,
                value=token.value,
                unit=token.unit,
                backing_claim_id=card.claim_id,
                source_value=float(card.value),
                match_status="match",
            )
    # No exact-match card; look for the closest passed card to surface a
    # diagnostic mismatch (helps writer debug).
    closest: Optional[ClaimCardLike] = None
    closest_delta = float("inf")
    for card in cards:
        if card.verifier_status != "passed" or card.value is None:
            continue
        delta = abs(token.value - float(card.value))
        if delta < closest_delta:
            closest_delta = delta
            closest = card
    if closest is not None and closest_delta <= 1.0:
        return TokenVerdict(
            token=token.raw,
            value=token.value,
            unit=token.unit,
            backing_claim_id=closest.claim_id,
            source_value=float(closest.value),
            match_status="rounding_mismatch",
        )
    return TokenVerdict(
        token=token.raw,
        value=token.value,
        unit=token.unit,
        backing_claim_id=None,
        source_value=None,
        match_status="no_backing_card",
    )


def factcheck_body(
    body: str,
    cards: list[ClaimCardLike],
    surface_id: str,
    char_cap: int,
    rounding_tolerance: float = 0.05,
) -> FactCheckResult:
    """Mode B per-surface factcheck.

    Confirms:
      - cap not exceeded
      - no TK leakage
      - every numeric token has a passing-card backing within tolerance
    """
    text = body.strip()
    body_chars = len(text)
    cap_exceeded = body_chars > char_cap
    tk_leakage = bool(re.search(r"\bTK\b", text)) or bool(
        re.search(r"<\s*placeholder\s*>", text, re.IGNORECASE)
    )

    tokens = extract_numeric_tokens(text)
    verdicts: list[TokenVerdict] = []
    issues: list[str] = []
    if cap_exceeded:
        issues.append(
            f"body exceeds char_cap ({body_chars} > {char_cap})"
        )
    if tk_leakage:
        issues.append("TK or <placeholder> token in body")
    for tok in tokens:
        v = verify_token(tok, cards, rounding_tolerance)
        verdicts.append(v)
        if v.match_status == "no_backing_card":
            issues.append(
                f"numeric token {tok.raw!r} has no backing claim-card"
            )
        elif v.match_status == "rounding_mismatch":
            issues.append(
                f"numeric token {tok.raw!r} closest card "
                f"{v.backing_claim_id} value={v.source_value} "
                f"(delta {abs(tok.value - (v.source_value or 0)):.3f})"
            )

    return FactCheckResult(
        ok=not issues,
        surface_id=surface_id,
        char_cap=char_cap,
        body_chars=body_chars,
        tk_leakage=tk_leakage,
        cap_exceeded=cap_exceeded,
        tokens=verdicts,
        issues=issues,
    )
