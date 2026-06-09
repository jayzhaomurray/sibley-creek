"""Defensive aggregator for the historical MPR vintage dicts.

Three transcription agents own the batch fragment files
(``batch_2021_2022.py``, ``batch_2023_2024.py``, ``batch_2024_2026.py``), each
exposing a module-level ``VINTAGES`` list of vintage dicts (schema documented in
``pipeline/shadow_rate/backtest.py``). They are written in parallel and may not
all exist — or may be syntactically broken — when the backtest runs.

This aggregator is fail-soft by design: each fragment is imported in its own
try/except, and a missing or broken fragment is skipped with a one-line stdout
note rather than taking down the whole backtest. The backtest machinery and its
tests therefore never depend on any fragment being present.
"""

from __future__ import annotations

from importlib import import_module

# The fragment module names, in chronological order. The aggregated
# ``ALL_VINTAGES`` preserves this order (oldest batch first).
_FRAGMENTS = (
    "batch_2021_2022",
    "batch_2023_2024",
    "batch_2024_2026",
)

ALL_VINTAGES: list[dict] = []

for _name in _FRAGMENTS:
    try:
        _mod = import_module(f"{__name__}.{_name}")
    except Exception as exc:  # missing or broken fragment -> skip, note, continue
        print(f"[vintages] skipping fragment {_name!r}: {type(exc).__name__}: {exc}")
        continue
    _vins = getattr(_mod, "VINTAGES", None)
    if _vins is None:
        print(f"[vintages] fragment {_name!r} has no VINTAGES list; skipping")
        continue
    try:
        ALL_VINTAGES.extend(_vins)
    except TypeError as exc:
        print(f"[vintages] fragment {_name!r} VINTAGES is not iterable: {exc}; skipping")
        continue
