"""Tests for pipeline.fetch.yahoo -- the intraday-partial-bar guard.

Root cause being prevented (markets audit 2026-06-09, F5):
Yahoo's v8 chart endpoint returns the current partial bar alongside completed
history. Two real incidents:
  - 2026-06-05: a 9:15am ET quote (13:15 UTC) was recorded as the June 5
    daily close for CL=F.
  - 2026-06-09: the 22:00 UTC scheduled run captured a Globex evening-session
    quote dated 2026-06-10 and committed it to master as a "close".

The guard: a bar dated D is a completed close only when now >= 21:30 UTC on D.

Pure-function tests only; no network, no production caches touched.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from pipeline.fetch.yahoo import _drop_incomplete_final_bars


def _frame(rows: list[tuple[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime([r[0] for r in rows]),
            "value": [r[1] for r in rows],
        }
    )


def _utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


class TestDropIncompleteFinalBars:
    def test_morning_intraday_quote_dropped(self):
        # The 2026-06-05 incident: fetch at 13:15 UTC, final bar dated the
        # same day, is a 9:15am ET snapshot -- must be dropped.
        df = _frame([("2026-06-03", 96.02), ("2026-06-04", 93.04), ("2026-06-05", 92.16)])
        out = _drop_incomplete_final_bars(df, symbol="CL=F", now=_utc(2026, 6, 5, 13, 15))
        assert len(out) == 2
        assert out["date"].iloc[-1] == pd.Timestamp("2026-06-04")

    def test_evening_globex_bar_dated_tomorrow_dropped(self):
        # The 2026-06-09 incident: fetch at 00:44 UTC June 10 (20:44 ET
        # June 9); Yahoo's live Globex bar is dated June 10. Must be dropped;
        # the completed June 9 / June 8 bars must be kept.
        df = _frame([("2026-06-08", 91.30), ("2026-06-09", 90.10), ("2026-06-10", 89.68)])
        out = _drop_incomplete_final_bars(df, symbol="CL=F", now=_utc(2026, 6, 10, 0, 44))
        assert len(out) == 2
        assert out["date"].iloc[-1] == pd.Timestamp("2026-06-09")

    def test_completed_close_after_threshold_kept(self):
        # Post-close scheduled run (22:00 UTC): today's bar is complete.
        df = _frame([("2026-06-08", 34478.7), ("2026-06-09", 34411.7)])
        out = _drop_incomplete_final_bars(df, symbol="^GSPTSE", now=_utc(2026, 6, 9, 22, 5))
        assert len(out) == 2

    def test_exactly_at_threshold_kept(self):
        df = _frame([("2026-06-09", 1.3947)])
        out = _drop_incomplete_final_bars(df, symbol="X", now=_utc(2026, 6, 9, 21, 30))
        assert len(out) == 1

    def test_one_minute_before_threshold_dropped(self):
        df = _frame([("2026-06-09", 1.3947)])
        out = _drop_incomplete_final_bars(df, symbol="X", now=_utc(2026, 6, 9, 21, 29))
        assert len(out) == 0

    def test_historical_rows_never_dropped(self):
        df = _frame([("2026-06-01", 1.0), ("2026-06-02", 2.0), ("2026-06-03", 3.0)])
        out = _drop_incomplete_final_bars(df, symbol="X", now=_utc(2026, 6, 9, 1, 0))
        assert len(out) == 3

    def test_multiple_trailing_incomplete_bars_dropped(self):
        # Defensive: anomalous future-dated bars beyond the live one are
        # also stripped, from the tail inward.
        df = _frame([("2026-06-08", 91.3), ("2026-06-10", 89.7), ("2026-06-11", 89.5)])
        out = _drop_incomplete_final_bars(df, symbol="CL=F", now=_utc(2026, 6, 10, 0, 44))
        assert len(out) == 1
        assert out["date"].iloc[-1] == pd.Timestamp("2026-06-08")

    def test_empty_frame_passthrough(self):
        df = _frame([])
        out = _drop_incomplete_final_bars(df, symbol="X", now=_utc(2026, 6, 9, 12, 0))
        assert out.empty
