"""Per-surface cycle-artifact: YAML front-matter + body Markdown.

A `CycleArtifact` is the on-disk per-surface file. It carries the same
state_history as the `SurfaceSlot` in the wrapper `ReleaseCycle` (the
wrapper is the canonical source of truth; the artifact is the editorial
working surface and the user-review object). The wrapper and the artifact
are written together on every transition.

Front-matter is YAML between `---` fences; body is plain prose under
the fences. Round-trips via `ruamel.yaml` to preserve comments / order.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from ruamel.yaml import YAML

from pipeline.blurbs.release_cycle import StateEvent, SurfaceState


_yaml = YAML(typ="rt")
_yaml.default_flow_style = False
_yaml.allow_unicode = False  # ASCII-only enforcement at write time


class CycleArtifact(BaseModel):
    """Front-matter schema for a per-surface cycle artifact.

    Mirrors the structure in editorial/auto_blurb_process.md Section 3.2,
    adapted for the 5-surface world: instead of a single `unit_slug`, the
    artifact also carries `surface` (the surface kind, e.g.
    `chart_commentary`, `homepage_abstract`) and refers back to the shared
    claim-card file via `shared_cards_path`.
    """

    # Identity
    release_id: str
    release_key: str
    section: str
    unit_slug: str
    surface: str = Field(..., description="surface kind: homepage_abstract, etc.")
    reference_period: str
    release_date: Optional[str] = None
    created_at: str

    # Per-surface variants of the editorial product
    char_cap: int
    voice_register_variant: str = Field(
        "mode_a",
        description=(
            "Sub-register within Mode A: chart_commentary, sparkline_blurb, "
            "active_headline, topic_abstract, homepage_abstract."
        ),
    )

    # State machine
    last_state: SurfaceState = "release_landed"
    state_history: list[StateEvent] = Field(default_factory=list)

    # Shared-card link
    shared_cards_path: str
    researcher_revision_count: int = 0
    writer_revision_count: int = 0
    style_revision_count: int = 0

    # Verification artifacts
    claims_verified_path: Optional[str] = None
    claims_verified_status: Optional[str] = None
    fact_check_path: Optional[str] = None
    fact_check_status: Optional[str] = None
    voice_validation: Optional[str] = None

    # Numerics surfaced in the email summary
    consensus_source: Optional[str] = None
    consensus_value: Optional[float] = None
    print_value: Optional[float] = None
    prior_value: Optional[float] = None
    surprise_units: Optional[str] = None
    surprise_value: Optional[float] = None

    # Free-form flags surface
    flags: list[dict] = Field(default_factory=list)

    # Model pins (per dispatch tier; filled by run.py)
    model_writer: Optional[str] = None
    model_fact_checker: Optional[str] = None
    model_style_editor: Optional[str] = None
    model_verifier: Optional[str] = None

    # User-facing status, lockstep with last_state for the user-review states.
    status: str = "writer_drafted"
    quiet_release: bool = False
    approved_by_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Read / Write
# ---------------------------------------------------------------------------

_FENCE = "---"


def _dump_yaml(data: dict) -> str:
    buf = io.StringIO()
    _yaml.dump(data, buf)
    return buf.getvalue()


def _ensure_ascii(text: str) -> None:
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"Cycle artifact contained non-ASCII at byte {exc.start}: "
            f"{text[exc.start:exc.start + 20]!r}"
        ) from exc


def write_artifact(path: Path, artifact: CycleArtifact, body: str) -> Path:
    """Serialize front-matter + body to Markdown.

    Existing files are overwritten. Body is preserved verbatim except that
    a trailing newline is enforced; non-ASCII content raises.
    """
    payload = artifact.model_dump(mode="json", exclude_none=False)
    fm = _dump_yaml(payload)
    body_text = body.rstrip("\n") + "\n"
    out = f"{_FENCE}\n{fm}{_FENCE}\n\n{body_text}"
    _ensure_ascii(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(out, encoding="utf-8", newline="\n")
    return path


def read_artifact(path: Path) -> tuple[CycleArtifact, str]:
    """Read a cycle artifact; return (CycleArtifact, body_text).

    Raises ValueError if the front-matter fence is missing or malformed.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith(_FENCE):
        raise ValueError(f"artifact {path} missing front-matter fence")
    rest = text[len(_FENCE):].lstrip("\n")
    # find the closing fence
    end = rest.find(f"\n{_FENCE}\n")
    if end < 0:
        # tolerate a closing fence at EOF without trailing newline
        end_eof = rest.rfind(f"\n{_FENCE}")
        if end_eof < 0:
            raise ValueError(f"artifact {path} missing closing front-matter fence")
        fm_text = rest[:end_eof]
        body = ""
    else:
        fm_text = rest[:end]
        body = rest[end + len(f"\n{_FENCE}\n"):]
    fm_data = _yaml.load(io.StringIO(fm_text)) or {}
    # ruamel.yaml returns CommentedMap; pydantic accepts it as a dict.
    artifact = CycleArtifact.model_validate(dict(fm_data))
    return artifact, body
