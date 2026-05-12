"""Load + validate the tracked claims registry.

The registry lives at ``editorial/drift/tracked_claims.yml``. This
module reads it, validates the shape with pydantic, and yields a flat
list of ``Claim`` records ready for the watcher to process.

Schema rules (enforced):
  * Each pillar has a slug, title, published_at (YYYY-MM-DD), and a non-empty list of claims.
  * Each claim has id, text, data_source, published_value, unit, threshold.
  * data_source must be one of the two supported forms:
        "<path>.csv -> last row"
        "<path>.json -> panels[?key=='<key>'].value"
  * published_value and threshold are floats; threshold is positive.
  * Claim ids must be unique within a pillar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field, field_validator
from ruamel.yaml import YAML

# Canonical registry location relative to repo root. The watcher resolves
# it relative to the project root so callers can invoke from anywhere.
DEFAULT_REGISTRY_PATH = Path("editorial/drift/tracked_claims.yml")

_CSV_SOURCE_RE = re.compile(r"^(?P<path>data/raw/[\w./-]+\.csv)\s*->\s*last row$")
_JSON_SOURCE_RE = re.compile(
    r"^(?P<path>data/site/panel_data/[\w./-]+\.json)\s*->\s*panels\[\?key=='(?P<key>[\w-]+)'\]\.value$"
)


class _ClaimModel(BaseModel):
    id: str
    text: str
    data_source: str
    published_value: float
    unit: str
    threshold: float = Field(gt=0)

    @field_validator("data_source")
    @classmethod
    def _data_source_must_be_supported(cls, v: str) -> str:
        if _CSV_SOURCE_RE.match(v) or _JSON_SOURCE_RE.match(v):
            return v
        raise ValueError(
            f"unsupported data_source form: {v!r}. "
            "Expected '<path>.csv -> last row' or "
            "'<path>.json -> panels[?key==\\'<key>\\'].value'."
        )


class _PillarModel(BaseModel):
    slug: str
    title: str
    published_at: str
    claims: list[_ClaimModel] = Field(min_length=1)

    @field_validator("published_at")
    @classmethod
    def _published_at_iso(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError(f"published_at must be YYYY-MM-DD; got {v!r}")
        return v

    @field_validator("claims")
    @classmethod
    def _unique_claim_ids(cls, v: list[_ClaimModel]) -> list[_ClaimModel]:
        seen: set[str] = set()
        for c in v:
            if c.id in seen:
                raise ValueError(f"duplicate claim id within pillar: {c.id}")
            seen.add(c.id)
        return v


class _RegistryModel(BaseModel):
    pillars: list[_PillarModel] = Field(min_length=1)


@dataclass(frozen=True)
class Claim:
    """A single tracked claim resolved out of the registry."""

    pillar_slug: str
    pillar_title: str
    pillar_published_at: str
    id: str
    text: str
    data_source: str
    published_value: float
    unit: str
    threshold: float

    @property
    def qualified_id(self) -> str:
        """``mortgage-renewal-wall/A1``-style identifier for log lines."""
        return f"{self.pillar_slug}/{self.id}"


def parse_data_source(data_source: str) -> tuple[str, str, str | None]:
    """Parse a data_source expression.

    Returns ``(kind, path, key)`` where ``kind`` is ``'csv_last_row'`` or
    ``'json_panel'``, ``path`` is the file path relative to repo root, and
    ``key`` is the panel-data series key (only set for JSON sources).
    """
    m = _CSV_SOURCE_RE.match(data_source)
    if m:
        return ("csv_last_row", m.group("path"), None)
    m = _JSON_SOURCE_RE.match(data_source)
    if m:
        return ("json_panel", m.group("path"), m.group("key"))
    # _ClaimModel.validate should have caught this; defensive only.
    raise ValueError(f"unsupported data_source: {data_source!r}")


def load_claims_registry(
    path: Path | str = DEFAULT_REGISTRY_PATH,
) -> list[Claim]:
    """Read the YAML registry, validate, and return a flat list of claims."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"claims registry not found: {path}")

    yaml = YAML(typ="safe")
    raw = yaml.load(path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"claims registry is empty: {path}")

    model = _RegistryModel.model_validate(raw)

    out: list[Claim] = []
    for pillar in model.pillars:
        for claim in pillar.claims:
            out.append(
                Claim(
                    pillar_slug=pillar.slug,
                    pillar_title=pillar.title,
                    pillar_published_at=pillar.published_at,
                    id=claim.id,
                    text=claim.text,
                    data_source=claim.data_source,
                    published_value=claim.published_value,
                    unit=claim.unit,
                    threshold=claim.threshold,
                )
            )
    return out


def iter_claims_by_pillar(claims: Iterable[Claim]) -> dict[str, list[Claim]]:
    """Group a flat claims list by ``pillar_slug``, preserving order."""
    grouped: dict[str, list[Claim]] = {}
    for c in claims:
        grouped.setdefault(c.pillar_slug, []).append(c)
    return grouped
