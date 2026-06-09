"""Write the headline + decomposition sheets back into the LFS-micro workbook.

Used by run.py to refresh an existing workbook in place after a new PUMF month
is processed. Follows the same Windows file-lock companion-fallback pattern as
pipeline/shadow_rate/output_sheet.py.

The workbook must already exist (built by make_workbook.py or a prior run.py).
This module replaces only the data-bearing sheets (headline, decomposition,
latest_month, params_meta) — it does NOT re-create the workbook structure.
For a full rebuild, call make_workbook.build_workbook() directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pipeline.lfs_micro.make_workbook import (
    _load_boc,
    _load_engine_cache,
    _load_replication,
    build_workbook,
)


@dataclass
class OutputWriteResult:
    path: Path
    used_companion: bool


def write_output_sheet(xlsx_path: str | Path) -> OutputWriteResult:
    """Refresh all data sheets in the workbook at xlsx_path.

    Fully rebuilds the workbook content (data changes each refresh), not just
    one sheet. The workbook is saved in place; if it is open in Excel (Windows
    PermissionError), the refreshed version is written to a companion file
    lfs_micro_output.xlsx in the same folder.

    Returns:
        OutputWriteResult(path, used_companion).
    """
    xlsx_path = Path(xlsx_path)
    try:
        out = build_workbook(xlsx_path, overwrite=True)
        return OutputWriteResult(path=out, used_companion=False)
    except PermissionError:
        companion = xlsx_path.with_name(
            xlsx_path.stem.replace("_replication", "_output") + xlsx_path.suffix
        )
        out = build_workbook(companion, overwrite=True)
        return OutputWriteResult(path=out, used_companion=True)
