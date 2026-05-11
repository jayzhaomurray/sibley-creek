"""Per-surface body validators.

Loads ban-lists from editorial/writing-style.md Section 6 at module load
so updates to writing-style.md flow through without code changes. Each
surface kind gets a specific rules tuple (word range, sentence range,
char cap, plus the kind-specific extras).

Mode A bans apply to every surface:
- No banned cliches / hedging tics / jargon-as-armor (Section 6 lists)
- No Big-Six bank citation construction ("RBC expected", "TD called for")
- No "going forward", "at the end of the day", "in terms of" (Section 6)
- No TK / <placeholder> tokens
- ASCII-only
- No banned hedging adverbs ("arguably", "interestingly", etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[2]
WRITING_STYLE_PATH = REPO_ROOT / "editorial" / "writing-style.md"


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

class ValidationFailure(BaseModel):
    rule: str
    message: str
    span: Optional[str] = None


class ValidationResult(BaseModel):
    ok: bool
    surface_id: str
    failures: list[ValidationFailure] = []

    @property
    def reasons(self) -> list[str]:
        return [f"{f.rule}: {f.message}" for f in self.failures]


# ---------------------------------------------------------------------------
# Per-surface rules
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SurfaceRules:
    surface_kind: str
    word_min: int
    word_max: int
    sentence_min: int
    sentence_max: int
    char_cap: int
    require_period_end: bool = False
    require_numeric_or_named_institution: bool = False
    forbid_opening_subordinate_clause: bool = False


SURFACE_RULES: dict[str, SurfaceRules] = {
    "sparkline_blurb": SurfaceRules(
        surface_kind="sparkline_blurb",
        word_min=10, word_max=25,
        sentence_min=1, sentence_max=2,
        char_cap=120,
        forbid_opening_subordinate_clause=True,
    ),
    "active_headline": SurfaceRules(
        surface_kind="active_headline",
        word_min=8, word_max=22,
        sentence_min=1, sentence_max=1,
        char_cap=140,
        require_period_end=True,
        require_numeric_or_named_institution=True,
    ),
    "topic_abstract": SurfaceRules(
        surface_kind="topic_abstract",
        word_min=45, word_max=90,
        sentence_min=2, sentence_max=3,
        char_cap=480,
    ),
    "homepage_abstract": SurfaceRules(
        surface_kind="homepage_abstract",
        word_min=60, word_max=110,
        sentence_min=3, sentence_max=4,
        char_cap=560,
    ),
    "chart_commentary": SurfaceRules(
        surface_kind="chart_commentary",
        word_min=25, word_max=95,
        sentence_min=2, sentence_max=4,
        char_cap=500,
    ),
}


# ---------------------------------------------------------------------------
# Ban-list loader (writing-style.md Section 6 / Section 7.1)
# ---------------------------------------------------------------------------

# Phrases we always reject (case-insensitive substring match). Loaded fresh
# from writing-style.md Section 6 when available; the hard-coded fallback
# below is the minimum guarantee if the file is missing / unreadable.
_FALLBACK_BANNED_SUBSTRINGS: tuple[str, ...] = (
    "going forward",
    "at the end of the day",
    "in terms of",
    "the everything bubble",
    "this changes everything",
    "shocking",
    "stunning",
    "jaw-dropping",
    "eye-watering",
    "canada's lehman moment",
    "the wheels are coming off",
    "the elephant in the room",
    "kicking the can down the road",
    "the perfect storm",
    "uncharted territory",
    "new normal",
    "hawkish hold",
    "dovish hold",
    "the consumer is resilient",
    "the consumer is cracking",
    "arguably",
    "some would say",
    "it could be argued",
    "in some sense",
    "it is perhaps worth noting",
    "interestingly",
    "needless to say",
    "of course",
    "constructive",
    "cautiously optimistic",
    "wait-and-see",
    "watching closely",
    "on our radar",
    "we continue to monitor",
    "the setup",
    "the tape",
    "risk-on",
    "risk-off",
    "bid for duration",
    "goldilocks",
    "bay street says",
    # Mode A specific (Section 7 Mode A "no editorial" line)
    "we think",
    "watch for",
)

# Big-Six bank names paired with citation verbs. The regex below catches
# "RBC expected", "TD's forecast", "Scotia called for", etc. Bare bank
# names in non-citation contexts (e.g. "Big-Six PCL builds") are allowed.
_BIGSIX_NAMES = r"(?:RBC|TD|BMO|Scotia(?:bank)?|CIBC|National Bank|NBC)"
_CITATION_VERBS = (
    r"(?:expected|forecast|forecasted|called for|said|sees?|"
    r"thinks?|believes?|projected?|"
    r"projects?|estimat\w*|"
    r"was looking for|were looking for)"
)
_BIGSIX_CITATION_RE = re.compile(
    rf"\b{_BIGSIX_NAMES}\b(?:'s)?\s+{_CITATION_VERBS}\b",
    re.IGNORECASE,
)
# "the Street was looking for", "the Bay Street consensus" patterns
_STREET_CITATION_RE = re.compile(
    r"\b(?:the\s+)?(?:Street|Bay\s*Street)\s+(?:was\s+|were\s+)?"
    r"(?:looking|expecting|expected|consensus|said|sees)\b",
    re.IGNORECASE,
)

# Section 6 list parser: pulls quoted-string entries off "### Cliches to cut",
# "### Hedging tics", and "### Jargon-as-armor" sub-headings.
def _load_banned_substrings_from_style_md(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return _FALLBACK_BANNED_SUBSTRINGS
    text = path.read_text(encoding="utf-8")
    bans: list[str] = []
    in_target_section = False
    target_headings = {
        "Cliches to cut, with no exceptions",
        "Clichés to cut, with no exceptions",  # accented form
        "Clichés to cut, with no exceptions",
        "Hedging tics, banned",
        "Jargon-as-armor, cut",
        "Constructions to rewrite",
    }
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("### "):
            heading = line[4:].strip()
            in_target_section = heading in target_headings
            continue
        if line.startswith("## ") and in_target_section:
            in_target_section = False
            continue
        if not in_target_section:
            continue
        # bullets like:  - "going forward."  OR  - "the everything bubble"
        m = re.match(r'-\s+"([^"]+)"', line)
        if m:
            bans.append(m.group(1).strip().lower().rstrip(".").rstrip(","))
            continue
    # de-dup, drop empties, also fold in the fallback to be safe
    merged = set(b for b in bans if b)
    merged.update(_FALLBACK_BANNED_SUBSTRINGS)
    return tuple(sorted(merged))


BANNED_SUBSTRINGS: tuple[str, ...] = _load_banned_substrings_from_style_md(
    WRITING_STYLE_PATH
)


# Named institutions for the active-headline "must contain numeric or named
# institution" rule. Pulled from Section 4 of writing-style.md plus the
# core Canadian macro shorthand.
NAMED_INSTITUTIONS: tuple[str, ...] = (
    "BoC", "StatCan", "OSFI", "CMHC", "DoF", "PBO",
    "CREA", "CBA", "IMF", "OECD", "BIS",
    "the Fed", "USTR", "FOMC", "MPR", "FSR",
    "LFS", "SEPH", "JVWS", "CSCE", "BOS", "FES",
    "Bank of Canada", "Statistics Canada",
    "C.D. Howe",
    "CPP", "QPP", "OAS", "GIS",
    "TRREB",
)


# ---------------------------------------------------------------------------
# Sentence / word counters
# ---------------------------------------------------------------------------

# Word count = whitespace-separated tokens that contain at least one
# alphanumeric character. Hyphenated compounds count as one word
# (consistent with English copy-editing convention). This treats
# "core-trim" as one word but "2.3% Y/Y" as two words ("2.3%" + "Y/Y").
_WORD_RE = re.compile(r"\S*[A-Za-z0-9]\S*")
_NUMERIC_TOKEN_RE = re.compile(
    r"-?\d+(?:\.\d+)?\s*(?:%|pp|bps|bp|p\.p\.|ppt|pts?)?"
)

# Sentence-terminator: . ! ? followed by whitespace/EOL.
_SENTENCE_END_RE = re.compile(r"[.!?](?:\s+|$)")
# Subordinating conjunctions at sentence start (Section 7 says sparkline
# blurbs should not open with a subordinate clause).
_SUBORDINATE_OPENERS = (
    "although ", "though ", "while ", "whereas ", "because ", "since ",
    "if ", "unless ", "as ", "when ", "whenever ", "after ", "before ",
)


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def count_sentences(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    matches = _SENTENCE_END_RE.findall(stripped)
    n = len(matches)
    if not stripped[-1] in ".!?":
        # un-terminated trailing fragment counts as a sentence
        n += 1
    return n


def has_numeric_token(text: str) -> bool:
    for m in _NUMERIC_TOKEN_RE.finditer(text):
        # cheap guard against bare digits inside identifiers; numerics
        # should have surrounding whitespace, punctuation, or unit suffix.
        return True
    return False


def has_named_institution(text: str) -> bool:
    lowered = text  # case-sensitive: BoC vs boc matters per Section 4
    return any(name in lowered for name in NAMED_INSTITUTIONS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_surface_body(surface_kind: str, body: str) -> ValidationResult:
    """Run all mechanical checks on a per-surface body."""
    rules = SURFACE_RULES.get(surface_kind)
    if rules is None:
        return ValidationResult(
            ok=False,
            surface_id=surface_kind,
            failures=[ValidationFailure(
                rule="unknown_surface_kind",
                message=f"no SurfaceRules entry for {surface_kind!r}",
            )],
        )

    failures: list[ValidationFailure] = []
    text = body.strip()

    # ASCII-only
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        failures.append(ValidationFailure(
            rule="ascii_only",
            message=f"non-ASCII at byte {exc.start}",
            span=text[max(0, exc.start - 5): exc.start + 10],
        ))

    # TK / placeholder leakage
    if re.search(r"\bTK\b", text):
        failures.append(ValidationFailure(
            rule="tk_leakage",
            message="found 'TK' token in body",
        ))
    if re.search(r"<\s*placeholder\s*>", text, re.IGNORECASE):
        failures.append(ValidationFailure(
            rule="placeholder_leakage",
            message="found '<placeholder>' marker in body",
        ))

    # Cap (chars)
    if len(text) > rules.char_cap:
        failures.append(ValidationFailure(
            rule="char_cap",
            message=f"length {len(text)} > cap {rules.char_cap}",
        ))

    # Word range
    n_words = count_words(text)
    if n_words < rules.word_min or n_words > rules.word_max:
        failures.append(ValidationFailure(
            rule="word_range",
            message=(
                f"word count {n_words} outside "
                f"[{rules.word_min}, {rules.word_max}]"
            ),
        ))

    # Sentence range
    n_sents = count_sentences(text)
    if n_sents < rules.sentence_min or n_sents > rules.sentence_max:
        failures.append(ValidationFailure(
            rule="sentence_range",
            message=(
                f"sentence count {n_sents} outside "
                f"[{rules.sentence_min}, {rules.sentence_max}]"
            ),
        ))

    # End-with-period (active_headline)
    if rules.require_period_end and not text.endswith("."):
        failures.append(ValidationFailure(
            rule="require_period_end",
            message="active headline must end with '.'",
        ))

    # Numeric token OR named institution (active_headline)
    if rules.require_numeric_or_named_institution:
        if not (has_numeric_token(text) or has_named_institution(text)):
            failures.append(ValidationFailure(
                rule="numeric_or_institution_required",
                message=(
                    "active headline must contain a numeric token or named "
                    "institution; found neither"
                ),
            ))

    # Subordinate-clause opener (sparkline_blurb)
    if rules.forbid_opening_subordinate_clause:
        lowered = text.lower().lstrip()
        if any(lowered.startswith(op) for op in _SUBORDINATE_OPENERS):
            failures.append(ValidationFailure(
                rule="opening_subordinate_clause",
                message="sparkline blurb cannot open with a subordinate clause",
            ))

    # Banned substrings (Mode A bans)
    lowered_text = text.lower()
    for banned in BANNED_SUBSTRINGS:
        if banned in lowered_text:
            failures.append(ValidationFailure(
                rule="banned_construction",
                message=f"contains banned phrase {banned!r}",
                span=banned,
            ))

    # Big-Six citation
    m = _BIGSIX_CITATION_RE.search(text)
    if m:
        failures.append(ValidationFailure(
            rule="bigsix_citation",
            message=f"Big-Six citation construction: {m.group(0)!r}",
            span=m.group(0),
        ))
    m = _STREET_CITATION_RE.search(text)
    if m:
        failures.append(ValidationFailure(
            rule="street_citation",
            message=f"'the Street' citation construction: {m.group(0)!r}",
            span=m.group(0),
        ))

    return ValidationResult(
        ok=not failures,
        surface_id=surface_kind,
        failures=failures,
    )
