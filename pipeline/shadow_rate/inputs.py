"""Workbook parsing + fail-closed validation for the shadow-rate tool.

Reads the three-sheet punch-in workbook (quarterly / annual / params) with
openpyxl and validates every field with pydantic. Validation is fail-closed:
out-of-bounds or missing values raise rather than silently defaulting, so a
fat-fingered transcription in Jay's spreadsheet stops the run instead of
producing a plausible-but-wrong path.

Sheet schema (each sheet carries a ``source_ref`` provenance column):

  quarterly: quarter, core_cpi_yoy_forecast, total_cpi_yoy_reference,
             gdp_growth_qq_ann_forecast, anchor_type, source_ref
  annual:    year, potential_growth_low, potential_growth_high, gdp_q4q4,
             source_ref
  params:    key/value rows (mpr_publication_date, current_overnight_rate,
             output_gap_anchor_quarter, output_gap_anchor_value,
             neutral_range_low/high, rho, phi_pi,
             phi_gap, inflation_target, inflation_converge_quarters,
             elb_floor, verified) each with a source_ref
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook
from pydantic import BaseModel, Field, field_validator, model_validator


# --------------------------------------------------------------------------- #
# Validated row / param models
# --------------------------------------------------------------------------- #
class QuarterlyRow(BaseModel):
    """One row of the quarterly sheet.

    ``quarter`` is a string like "2026Q2". ``core_cpi_yoy_forecast`` is the
    model input (average of CPI-trim and CPI-median, per MPR Table 3 footnote).
    ``total_cpi_yoy_reference`` is reference-only and NOT consumed by the model.
    ``anchor_type`` is "quarterly" for near-term observed rows or "q4q4" for the
    Q4/Q4 anchor rows the model interpolates between.
    """

    quarter: str
    core_cpi_yoy_forecast: float = Field(..., ge=-5.0, le=15.0)
    total_cpi_yoy_reference: Optional[float] = Field(None, ge=-5.0, le=15.0)
    gdp_growth_qq_ann_forecast: Optional[float] = Field(None, ge=-30.0, le=30.0)
    anchor_type: str
    source_ref: str

    @field_validator("quarter")
    @classmethod
    def _check_quarter(cls, v: str) -> str:
        v = v.strip()
        if len(v) != 6 or v[4].upper() != "Q" or not v[:4].isdigit() or v[5] not in "1234":
            raise ValueError(f"quarter must look like '2026Q2', got {v!r}")
        return v[:4] + "Q" + v[5]

    @field_validator("anchor_type")
    @classmethod
    def _check_anchor(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ("quarterly", "q4q4"):
            raise ValueError(f"anchor_type must be 'quarterly' or 'q4q4', got {v!r}")
        return v

    @field_validator("source_ref")
    @classmethod
    def _check_ref(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("source_ref must not be empty")
        return v.strip()


class AnnualRow(BaseModel):
    """One row of the annual sheet (potential-growth ranges + Q4/Q4 GDP)."""

    year: int = Field(..., ge=2000, le=2100)
    potential_growth_low: float = Field(..., ge=-5.0, le=10.0)
    potential_growth_high: float = Field(..., ge=-5.0, le=10.0)
    gdp_q4q4: Optional[float] = Field(None, ge=-30.0, le=30.0)
    source_ref: str

    @model_validator(mode="after")
    def _check_range(self) -> "AnnualRow":
        if self.potential_growth_high < self.potential_growth_low:
            raise ValueError(
                f"potential_growth_high ({self.potential_growth_high}) < low "
                f"({self.potential_growth_low}) for year {self.year}"
            )
        if not self.source_ref.strip():
            raise ValueError("source_ref must not be empty")
        return self

    @property
    def potential_growth_mid(self) -> float:
        return (self.potential_growth_low + self.potential_growth_high) / 2.0


class Params(BaseModel):
    """The params sheet, flattened into one validated model.

    All rate-like values are in percent units (2.5 == 2.5%), matching the repo
    convention. Bounds are fail-closed: nonsense transcriptions raise.
    """

    mpr_publication_date: date
    current_overnight_rate: float = Field(..., ge=-1.0, le=25.0)
    # Output-gap anchor: the BoC staff output-gap estimate at its last published
    # quarter (Valet INDINF_OUTGAPMPR_Q). The model rolls this forward by the gap
    # evolution identity to the seed (MPR) quarter and on through the horizon.
    output_gap_anchor_quarter: str
    output_gap_anchor_value: float = Field(..., ge=-10.0, le=10.0)
    neutral_range_low: float = Field(..., ge=0.0, le=10.0)
    neutral_range_high: float = Field(..., ge=0.0, le=10.0)
    rho: float = Field(0.85, ge=0.0, le=1.0)
    phi_pi: float = Field(4.65, ge=0.0, le=20.0)
    phi_gap: float = Field(0.40, ge=0.0, le=10.0)
    inflation_target: float = Field(2.0, ge=0.0, le=10.0)
    inflation_converge_quarters: int = Field(4, ge=1, le=40)
    elb_floor: float = Field(0.25, ge=-1.0, le=5.0)
    verified: bool = False

    @field_validator("output_gap_anchor_quarter")
    @classmethod
    def _check_anchor_quarter(cls, v: str) -> str:
        v = str(v).strip()
        if (
            len(v) != 6
            or v[4].upper() != "Q"
            or not v[:4].isdigit()
            or v[5] not in "1234"
        ):
            raise ValueError(
                f"output_gap_anchor_quarter must look like '2025Q4', got {v!r}"
            )
        return v[:4] + "Q" + v[5]

    @model_validator(mode="after")
    def _check_ranges(self) -> "Params":
        if self.neutral_range_high < self.neutral_range_low:
            raise ValueError(
                f"neutral_range_high ({self.neutral_range_high}) < "
                f"neutral_range_low ({self.neutral_range_low})"
            )
        return self

    @property
    def neutral_nominal_mid(self) -> float:
        return (self.neutral_range_low + self.neutral_range_high) / 2.0


class ShadowInputs(BaseModel):
    """Bundle of all three validated sheets."""

    quarterly: list[QuarterlyRow]
    annual: list[AnnualRow]
    params: Params

    @model_validator(mode="after")
    def _check_nonempty(self) -> "ShadowInputs":
        if not self.quarterly:
            raise ValueError("quarterly sheet is empty")
        if not self.annual:
            raise ValueError("annual sheet is empty")
        # Require at least one q4q4 anchor so the model has something to
        # interpolate toward beyond the near-term quarterly rows.
        if not any(r.anchor_type == "q4q4" for r in self.quarterly):
            raise ValueError("quarterly sheet has no q4q4 anchor rows")
        return self


# --------------------------------------------------------------------------- #
# Workbook parsing
# --------------------------------------------------------------------------- #
def _coerce_number(v) -> Optional[float]:
    """Empty cell -> None; otherwise float. Raises on non-numeric junk."""
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return None
        return float(v)  # raises ValueError on junk -> fail-closed
    return float(v)


def _coerce_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes", "y", "1", "verified"):
            return True
        if s in ("false", "no", "n", "0", "unverified", ""):
            return False
    raise ValueError(f"cannot interpret {v!r} as a boolean for 'verified'")


def _header_index(ws, expected: list[str]) -> dict[str, int]:
    """Map column header name -> 0-based column index from the first row."""
    header_cells = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    headers = [str(c).strip() if c is not None else "" for c in header_cells]
    idx = {h: i for i, h in enumerate(headers)}
    missing = [c for c in expected if c not in idx]
    if missing:
        raise ValueError(
            f"sheet {ws.title!r} missing expected columns: {missing}; "
            f"found {headers}"
        )
    return idx


def parse_workbook(path: str | Path) -> ShadowInputs:
    """Parse + validate the punch-in workbook into a ShadowInputs bundle."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"workbook not found: {path}")

    wb = load_workbook(path, data_only=True, read_only=True)
    try:
        for sheet in ("quarterly", "annual", "params"):
            if sheet not in wb.sheetnames:
                raise ValueError(
                    f"workbook missing required sheet {sheet!r}; "
                    f"found {wb.sheetnames}"
                )

        quarterly = _parse_quarterly(wb["quarterly"])
        annual = _parse_annual(wb["annual"])
        params = _parse_params(wb["params"])
    finally:
        wb.close()

    return ShadowInputs(quarterly=quarterly, annual=annual, params=params)


def _parse_quarterly(ws) -> list[QuarterlyRow]:
    cols = [
        "quarter",
        "core_cpi_yoy_forecast",
        "total_cpi_yoy_reference",
        "gdp_growth_qq_ann_forecast",
        "anchor_type",
        "source_ref",
    ]
    idx = _header_index(ws, cols)
    rows: list[QuarterlyRow] = []
    for raw in ws.iter_rows(min_row=2, values_only=True):
        if raw is None or all(c is None for c in raw):
            continue
        if raw[idx["quarter"]] is None:
            continue
        rows.append(
            QuarterlyRow(
                quarter=str(raw[idx["quarter"]]).strip(),
                core_cpi_yoy_forecast=_coerce_number(raw[idx["core_cpi_yoy_forecast"]]),
                total_cpi_yoy_reference=_coerce_number(raw[idx["total_cpi_yoy_reference"]]),
                gdp_growth_qq_ann_forecast=_coerce_number(raw[idx["gdp_growth_qq_ann_forecast"]]),
                anchor_type=str(raw[idx["anchor_type"]]).strip(),
                source_ref=str(raw[idx["source_ref"]]).strip(),
            )
        )
    return rows


def _parse_annual(ws) -> list[AnnualRow]:
    cols = [
        "year",
        "potential_growth_low",
        "potential_growth_high",
        "gdp_q4q4",
        "source_ref",
    ]
    idx = _header_index(ws, cols)
    rows: list[AnnualRow] = []
    for raw in ws.iter_rows(min_row=2, values_only=True):
        if raw is None or all(c is None for c in raw):
            continue
        if raw[idx["year"]] is None:
            continue
        rows.append(
            AnnualRow(
                year=int(raw[idx["year"]]),
                potential_growth_low=_coerce_number(raw[idx["potential_growth_low"]]),
                potential_growth_high=_coerce_number(raw[idx["potential_growth_high"]]),
                gdp_q4q4=_coerce_number(raw[idx["gdp_q4q4"]]),
                source_ref=str(raw[idx["source_ref"]]).strip(),
            )
        )
    return rows


# params keys that are dates / bools / ints / strings get special coercion;
# the rest are floats.
_PARAM_DATE_KEYS = {"mpr_publication_date"}
_PARAM_BOOL_KEYS = {"verified"}
_PARAM_INT_KEYS = {"inflation_converge_quarters"}
_PARAM_STR_KEYS = {"output_gap_anchor_quarter"}


def _parse_params(ws) -> Params:
    idx = _header_index(ws, ["key", "value"])
    kv: dict[str, object] = {}
    for raw in ws.iter_rows(min_row=2, values_only=True):
        if raw is None or all(c is None for c in raw):
            continue
        key = raw[idx["key"]]
        if key is None:
            continue
        key = str(key).strip()
        val = raw[idx["value"]]
        if key in _PARAM_DATE_KEYS:
            kv[key] = _coerce_date(val)
        elif key in _PARAM_BOOL_KEYS:
            kv[key] = _coerce_bool(val)
        elif key in _PARAM_INT_KEYS:
            kv[key] = int(_coerce_number(val))
        elif key in _PARAM_STR_KEYS:
            kv[key] = "" if val is None else str(val).strip()
        else:
            kv[key] = _coerce_number(val)
    return Params(**kv)


def _coerce_date(v) -> date:
    if isinstance(v, date):
        return v
    if hasattr(v, "date"):  # datetime
        return v.date()
    if isinstance(v, str):
        return date.fromisoformat(v.strip())
    raise ValueError(f"cannot interpret {v!r} as a date for mpr_publication_date")
