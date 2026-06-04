"""Write a human-auditable ``output`` sheet back into the punch-in workbook.

After the model runs, this opens the same workbook Jay edits and writes (or
replaces) a sheet named ``output`` placed FIRST in the sheet order, so it is
what Jay sees when he opens the file. The sheet is a full per-quarter
decomposition of the policy-rule step: every number the engine computed laid
out so it can be checked by hand in Excel.

The sheet contains NO live Excel formulas. It is a static rendering of values
computed by the tested Python engine (``pipeline/shadow_rate/model.py``), which
remains the single source of truth.

The input sheets (``quarterly`` / ``annual`` / ``params``) are never touched.

Windows file-lock handling: if the workbook is open in Excel, openpyxl's save
raises ``PermissionError``. We catch it and write a companion file
``boc_shadow_output_2026Q2.xlsx`` in the same folder instead, returning the path
written and whether it was the companion fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from pipeline.shadow_rate.model import ShadowResult, quarter_to_ord

SHEET_NAME = "output"

# --- styling primitives (Vignelli-ish restraint: thin grey rules, no fill noise) ---
_INK = "1A1A1A"
_GREY = "BFBFBF"
_HEADER_FILL = PatternFill("solid", fgColor="F2F2F2")
_RED_FILL = PatternFill("solid", fgColor="C0392B")
_THIN = Side(style="thin", color=_GREY)
_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

_NUM3 = "0.000"
_NUM2 = "0.00"

# Table columns: (header, attribute-or-callable, number_format)
_TABLE_HEADERS = [
    "quarter",
    "shadow rate R_t (%)",
    "output gap (pp)",
    "core CPI t+4 used (%)",
    "gdp q/q ann (%)",
    "potential (%)",
    "infl term = phi_pi*(pi_t4-2.0)",
    "gap term = phi_gap*gap_t",
    "bracket = R*_nom+infl+gap",
    "inertia = rho*R_t",
    "step = (1-rho)*bracket+rho*R_t",
    "ELB binding? (Y/N)",
]


@dataclass
class OutputWriteResult:
    path: Path
    used_companion: bool


def _row_decomposition(step, p) -> dict:
    """Recompute the rule-step decomposition for one quarter, matching model._rule_step.

    The reported step is R_{t+1} BEFORE the ELB clamp; ELB binding is flagged
    when the raw step would fall below the floor.
    """
    infl_term = p.phi_pi * (step.infl_tp4 - p.inflation_target)
    gap_term = p.phi_gap * step.gap
    bracket = p.neutral_nominal_mid + infl_term + gap_term
    inertia = p.rho * step.rate
    raw_step = (1.0 - p.rho) * bracket + p.rho * step.rate
    elb_binding = raw_step < p.elb_floor
    return {
        "infl_term": infl_term,
        "gap_term": gap_term,
        "bracket": bracket,
        "inertia": inertia,
        "step": raw_step,
        "elb_binding": elb_binding,
    }


def _build_output_ws(wb, res: ShadowResult, p) -> None:
    """Create/replace the ``output`` sheet in wb (placed first)."""
    if SHEET_NAME in wb.sheetnames:
        del wb[SHEET_NAME]
    ws = wb.create_sheet(SHEET_NAME, index=0)

    bold = Font(bold=True, color=_INK)
    title_font = Font(bold=True, size=14, color=_INK)
    note_font = Font(italic=True, size=9, color="595959")

    draft = not p.verified
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    r = 1
    ws.cell(r, 1, "BoC Shadow Policy Rate — output").font = title_font
    r += 1
    ws.cell(r, 1, f"Run: {now}").font = Font(size=9, color="595959")
    r += 1

    # Verified status — big red cell if unverified.
    status_cell = ws.cell(r, 1)
    if draft:
        status_cell.value = "UNVERIFIED DRAFT"
        status_cell.font = Font(bold=True, size=14, color="FFFFFF")
        status_cell.fill = _RED_FILL
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    else:
        status_cell.value = "VERIFIED"
        status_cell.font = Font(bold=True, size=12, color="2E7D32")
    r += 2

    # Header / provenance block.
    block = [
        ("Anchor provenance",
         f"output gap anchored at {p.output_gap_anchor_quarter} = "
         f"{p.output_gap_anchor_value:+.2f}pp (source: BoC Valet "
         f"INDINF_OUTGAPMPR_Q, staff output gap, last published obs; "
         f"rolled forward to seed)"),
        ("Seed quarter / seed rate",
         f"{res.seed_quarter} @ {res.seed_rate:.2f}% (actual overnight rate at MPR)"),
        ("R*_nom (nominal neutral midpoint)",
         f"{p.neutral_nominal_mid:.2f}% "
         f"(range {p.neutral_range_low:.2f}-{p.neutral_range_high:.2f})"),
        ("Rule citation",
         f"ToTEM III, TR-119 Table 2.3: rho={p.rho}, phi_pi={p.phi_pi}, "
         f"phi_gap={p.phi_gap}; inflation target {p.inflation_target:.1f}%, "
         f"ELB floor {p.elb_floor:.2f}%, t+{p.inflation_converge_quarters} lookup"),
        ("MPR publication date", p.mpr_publication_date.isoformat()),
    ]
    for label, val in block:
        ws.cell(r, 1, label).font = bold
        ws.cell(r, 2, val)
        r += 1
    r += 1

    # Decomposition table.
    header_row = r
    for c, head in enumerate(_TABLE_HEADERS, start=1):
        cell = ws.cell(header_row, c, head)
        cell.font = bold
        cell.fill = _HEADER_FILL
        cell.border = _BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center",
                                   wrap_text=True)
    r += 1

    for step in res.steps:
        d = _row_decomposition(step, p)
        values = [
            (step.quarter, None),
            (round(step.rate, 4), _NUM3),
            (round(step.gap, 4), _NUM3),
            (round(step.infl_tp4, 4), _NUM3),
            (round(step.gdp_growth, 4), _NUM2),
            (round(step.potential, 4), _NUM2),
            (round(d["infl_term"], 4), _NUM3),
            (round(d["gap_term"], 4), _NUM3),
            (round(d["bracket"], 4), _NUM3),
            (round(d["inertia"], 4), _NUM3),
            (round(d["step"], 4), _NUM3),
            ("Y" if d["elb_binding"] else "N", None),
        ]
        for c, (val, fmt) in enumerate(values, start=1):
            cell = ws.cell(r, c, val)
            cell.border = _BORDER
            if fmt:
                cell.number_format = fmt
            if c == 1 or c == len(values):
                cell.alignment = Alignment(horizontal="center")
        r += 1

    r += 1
    note = (
        "Engine: pipeline/shadow_rate/model.py — this sheet shows values computed "
        "by the tested Python engine; it contains no live formulas (single source "
        "of truth). Methodology: "
        "claude-ref/research/shadow_rate/shadow_rate_methodology_2026-04.md"
    )
    note_cell = ws.cell(r, 1, note)
    note_cell.font = note_font
    note_cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r, start_column=1,
                   end_row=r, end_column=len(_TABLE_HEADERS))

    # Column widths.
    widths = [9, 12, 12, 12, 11, 11, 16, 14, 16, 13, 18, 12]
    for c, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w

    # Freeze the header row of the table so it stays visible on scroll.
    ws.freeze_panes = ws.cell(header_row + 1, 1)


def write_output_sheet(xlsx_path: str | Path, res: ShadowResult, p) -> OutputWriteResult:
    """Write/replace the ``output`` sheet in the workbook at ``xlsx_path``.

    Preserves the input sheets. On a Windows file lock (workbook open in Excel),
    falls back to a companion file ``boc_shadow_output_<stem-suffix>.xlsx`` in the
    same folder and returns ``used_companion=True``.
    """
    xlsx_path = Path(xlsx_path)
    wb = load_workbook(xlsx_path)  # full load (not read_only) so we can save back
    try:
        _build_output_ws(wb, res, p)
        try:
            wb.save(xlsx_path)
            return OutputWriteResult(path=xlsx_path, used_companion=False)
        except PermissionError:
            companion = xlsx_path.with_name(
                xlsx_path.name.replace("_inputs_", "_output_")
                if "_inputs_" in xlsx_path.name
                else f"{xlsx_path.stem}_output{xlsx_path.suffix}"
            )
            wb.save(companion)
            return OutputWriteResult(path=companion, used_companion=True)
    finally:
        wb.close()
