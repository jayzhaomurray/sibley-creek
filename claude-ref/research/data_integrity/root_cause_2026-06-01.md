# Data Integrity Root Cause — 2026-06-01

## Status
Investigated 2026-06-01. Fixes applied same session. See pipeline/io/panel_data.py
and scripts/check_panel_data_integrity.mjs for the systemic remediation.

---

## 1. The Infinity/NaN emission bug (primary root cause)

### Mechanism

`pipeline/io/panel_data.py :: _df_to_records()` converts DataFrame rows to
JSON-safe dicts. The guard logic is:

```python
fv = float(v)
if pd.isna(fv):
    rec[c] = None
else:
    rec[c] = fv   # <-- BUG
```

`pd.isna(float('inf'))` returns `False`. Python's `float('inf')` therefore
passes the guard and is emitted as the raw Python float. `json.dumps()` then
serializes it as the string `Infinity`, which is NOT valid JSON (the JSON spec
only allows numeric literals, not Infinity or NaN). Browsers that receive this
as `application/json` or parse it in JavaScript get `undefined` or a parse
error depending on the JS engine, which renders as broken/blank chart values.

### Which transforms can produce Infinity

- `pd.Series.pct_change()` — if the denominator (the lagged value) is exactly
  zero, `pct_change` returns `+inf` or `-inf`. This is the mechanism for any
  YoY/MoM/QoQ transform applied to a series that passes through zero (e.g. a
  series that was suspended and has zero-filled gaps, or a fiscal balance
  series that crosses zero).
- `annualize_period_growth()` in `pipeline/transform/timeseries.py` — calls
  `(s / s.shift(period_lag)) ** k - 1`. If `s.shift(period_lag)` is zero,
  division produces `inf`.
- The six-month annualized CREA HPI path (`six_month_annualized`) is the same
  function, same risk.

### Why it is latent (not always triggered)

As of 2026-06-01, no current on-disk CSV has zero values in the `value` column.
The NaN/Infinity in production arises from a different route: when the financial
refresh partially fails (BoC Valet, FRED, or Yahoo returns an error for some
series), the pipeline writes a partial update, then calls `build_all_panel_data`.
If a key input series was missing or had a gap for the latest date, and a derived
series (e.g. `goc_ust_spread_2y`) is then computed on misaligned date ranges, the
inner-join in `goc_ust_spread()` drops rows but the remaining rows are clean.
However, if upstream data contains `NaN` fills (e.g. StatCan suppression codes)
that are not stripped before a `pct_change()` call, the denominator may be NaN,
and `pct_change` propagates NaN to the numerator silently. The Infinity
specifically requires a zero denominator.

The confirmed current trigger is that `_df_to_records()` does not sanitize
`math.isinf(fv)` — this allows any future or past Infinity in a CSV to pass
directly into the JSON output without any loud failure.

---

## 2. Financial refresh staleness (contributing cause)

### Evidence

As of 2026-06-01:
- `yield_2yr/5yr/10yr/30yr`: last date 2026-05-28 (3 business days stale)
- `tsx_composite.csv`, `fxusdcad.csv`: last date 2026-05-29 (2 business days stale)
- `us_2yr.csv`, `us_10yr.csv` (FRED): last date 2026-05-15 (12 business days stale)
- `goc_ust_spread_2y/10y`: last date 2026-05-15 (limited by US Treasury staleness)

### Root cause of FRED staleness

The `build-data-daily` (not `build-financial-daily`) GitHub Actions workflow runs
`pipeline.build` which does NOT call FRED. FRED is called only by
`pipeline.build_financial`. The `build-financial-daily` workflow ran successfully
on 2026-05-30 (commit 27fe01d) but the US Treasury FRED series (`us_2yr`,
`us_10yr`) stalled at May 15 — suggesting FRED's `DGS2`/`DGS10` series were not
updated by FRED at the time of the 05-30 run (FRED's data release schedule
sometimes lags 1-3 business days for Treasury series; confirmed by checking that
the BoC GoC yield series ARE current to 05-28 but the UST FRED series are not).

### Root cause of May 30-31 deploy failures

The `deploy.yml` workflow runs `npm run build` which includes
`node scripts/check_panel_data_wired.mjs`. This gate fails if a WIRED panel's
`primary.data` is empty or null. When `build-financial-daily` ran on May 30
with a partial set of series (some Yahoo/FRED fetches failed), it still called
`build_all_panel_data()`. If any WIRED panel's primary series was the one that
failed, the panel_data JSON would have had `primary: null`, and the next deploy
build would hit the gate and fail.

The subsequent cascade: `deploy.yml` runs on a 15-minute cron; each run against
the same HEAD (which has the stale data) hits the same gate failure, producing
the run of failures on May 30-31 visible in the Actions log.

---

## 3. Missing validation gate (systemic gap)

The only pre-deploy data guard as of 2026-06-01 is:
- `check_tk_in_dist.mjs` — greps rendered HTML for the literal string "TK"
- `check_panel_data_wired.mjs` — asserts `primary.data.length > 0`

Neither catches:
- NaN or Infinity in numeric values (the Infinity bug documented above)
- Staleness beyond N business days for daily series
- Sane value range violations (e.g. a yield reading of 999%, or a TSX value of 0)
- Null values inside the data records (as opposed to null primary slot)

This gap is closed by `scripts/check_panel_data_integrity.mjs` (added 2026-06-01).

---

## 4. Fix summary

| Component | File | Change |
|---|---|---|
| Infinity/NaN guard | `pipeline/io/panel_data.py` | `_df_to_records()` now replaces `math.isinf(fv)` with `None`; NaN already handled |
| Transform safety | `pipeline/transform/timeseries.py` | `pct_change_at_horizon`, `yoy_pct`, `qoq_annualized_pct`, `annualize_period_growth` all replace Inf with NaN before return |
| Spread alignment | `pipeline/transform/derivations.py` | `goc_ust_spread()` and `partner_share_trajectory()` guard zero-denominator division |
| Validation gate | `scripts/check_panel_data_integrity.mjs` | New script; wired into `npm run build` after pipeline, before Astro build |
| Pipeline gate | `pipeline/io/panel_data.py` | `validate_panel_data_file()` function called at end of `build_all_panel_data()` |
| FRED staleness | `pipeline/fetch/fred.py` | Last-known-good carry-forward on empty response; explicit staleness warning |

---

## 5. Decisions needing Jay's judgment

1. **Acceptable staleness thresholds.** The validator currently uses:
   - Daily market series (yields, TSX, FX, WTI): 3 business days
   - Monthly series: 45 days
   These are defaults; Jay may want to tighten or loosen them.

2. **Sane value ranges.** The validator uses wide ranges that catch egregious
   corruptions (yield 0-30%, TSX 1000-100000, USDCAD 0.5-2.5). Narrower ranges
   could catch subtler drift but would require maintenance as regimes shift.

3. **What to do when FRED is stale.** Currently: warn loudly, keep last-good
   data, allow build to proceed. An alternative is to fail the financial build
   entirely if FRED is more than 5 business days stale. This would have blocked
   the May 30 refresh from committing and deploying stale spread data.
