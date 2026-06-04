# BoC Shadow Policy Rate — methodology (April 2026 MPR vintage)

Internal Sibley Creek research tool. Reconstructs the Bank of Canada's
*unpublished* rule-implied policy rate path from the Bank's own published
outputs, by applying ToTEM III's estimated policy reaction function to the
April 2026 Monetary Policy Report projections.

This is a **coherence reading**, not advice or a forecast. The MPR projections
are themselves conditioned on a policy assumption, so feeding them back through
the model's own rule tells you what rate path the rule implies *given those
projections* — it does not tell you what the Bank will do.

Status of this vintage: **UNVERIFIED** until Jay checks every transcribed cell
against the MPR PDF and flips `verified=TRUE` in the workbook params sheet.

---

## 1. The rule

ToTEM III's estimated monetary policy rule (Bank of Canada Technical Report 119,
Table 2.3), applied quarterly:

```
R_{t+1} = rho * R_t
          + (1 - rho) * [ R*_nom + phi_pi * (pi_hat_{t+4} - pi_target) + phi_gap * gap_t ]
R_{t+1} = max(R_{t+1}, ELB_floor)
```

with the estimated coefficients:

| Coefficient | Symbol | Value | Source |
|---|---|---|---|
| Interest-rate smoothing | rho | 0.85 | TR-119, Table 2.3 |
| Inflation response | phi_pi | 4.65 | TR-119, Table 2.3 |
| Output-gap response | phi_gap | 0.40 | TR-119, Table 2.3 |

`R*_nom` is the nominal neutral rate (midpoint of the published neutral range).
`pi_hat_{t+4}` is the model's core-inflation forecast four quarters ahead.
`pi_target` is the 2% CPI target. `gap_t` is the output gap.

The rule is forward-looking in inflation (t+4) — this matches TR-119's
estimation, where the rule responds to the *projected* deviation of inflation
from target, not the contemporaneous reading.

### Inflation input = CORE, not total CPI

The model reads **core inflation** (average of CPI-trim and CPI-median, per the
MPR Table 3 footnote), not total CPI. TR-119's rule was estimated on core
(CPIX-type) inflation deviations, so total CPI would be the wrong input. The
workbook carries total CPI in a `total_cpi_yoy_reference` column for context
only; `model.py` never reads it.

### Effective lower bound

The floor is the BoC's stated **effective lower bound of 0.25%** — the level the
Bank itself stopped at and named the ELB in 2009 and again in April 2020. It is
not literal zero. The param is editable in the workbook (`elb_floor`).

---

## 2. Turning sparse MPR rows into dense quarterly paths

The MPR publishes some series quarterly near-term and others only as Q4/Q4
anchors. The model fills in the gaps mechanically:

### Core inflation (the rule input)
- **Quarterly where given** (2025Q3 through 2026Q2): used directly.
- **Between the last quarterly value and the first Q4/Q4 anchor, and between
  successive anchors:** linear interpolation, quarter by quarter. Example:
  2026Q2 = 2.1 to 2026Q4 = 2.0 puts 2026Q3 at 2.05. The Q4 anchor values are
  treated as true quarterly observations, so this is *not* an annual flat-fill.
- **Beyond the final anchor (2028Q4 = 2.0):** held at the final value. Any t+4
  inflation lookup that reaches past the horizon uses this hold value.

### GDP growth (drives the gap evolution)
- **Direct q/q annualized where the MPR gives it** (2025Q3 through 2026Q2).
- **Later quarters:** a constant q/q-annualized rate within each calendar year,
  equal to that year's Q4/Q4 anchor (2026 remaining quarters: 1.8; 2027: 1.4;
  2028: 1.9).

### Potential growth (the gap's reference)
- Midpoint of that year's published range (Table 2): 2025 = 2.3 (point
  estimate); 2026 = 0.8-1.6 -> 1.2; 2027 = 0.8-1.8 -> 1.3; 2028 = 1.0-2.0 -> 1.5.

---

## 3. Output-gap evolution (anchor + roll-forward)

The gap is **anchored to the Bank's published staff output-gap estimate** and
rolled forward mechanically — no placeholder, no judgment.

### Anchor
The Bank publishes its staff output-gap estimate on the Valet API as series
`INDINF_OUTGAPMPR_Q` ("Current MPR output gap", %, quarterly; raw CSV at
`data/raw/output_gap_mpr.csv`). The **anchor** is the last published observation
of that series: at the April 2026 vintage that is **2025Q4 = -1.0%**
(i.e., 1.0% of excess supply). Two workbook fields carry it:
`output_gap_anchor_quarter` and `output_gap_anchor_value`. `make_workbook.py`
auto-fills both from the last row of the raw CSV, so a quarterly data refresh
that extends the series automatically advances the anchor.

### Roll-forward
The gap path **starts at the anchor quarter** and evolves by the standard
accounting identity (growth above potential opens the gap):

```
gap_{t+1} = gap_t + (gdp_growth_qq_ann_{t+1} - potential_growth_{t+1}) / 4
```

(The `/4` converts an annualized growth differential into one quarter's
contribution to the level of the gap. The gap at t+1 reflects growth DURING
quarter t+1 — i.e., the step from t to t+1 uses quarter t+1's growth and
potential, not quarter t's. This t+1 timing is intentional.)

Rolling forward from the anchor through the seed (MPR) quarter and on to the
horizon end uses the same GDP and potential-growth paths described in Section 2.
This requires those paths to cover every quarter from the anchor onward; the
model **validates (fail-closed)** that (a) the anchor quarter is at or before the
seed quarter and (b) GDP/potential data cover it, raising otherwise.

- **Seed quarter:** the calendar quarter containing the MPR publication date.
  For the April 29, 2026 MPR that is **2026Q2**. The rate iteration still seeds
  here (R_0 = current overnight rate); the gap entering the rule at 2026Q2 is the
  rolled-forward value, not the anchor.
- **Worked arithmetic (April 2026 vintage):**
  anchor 2025Q4 = -1.0;
  2026Q1 = -1.0 + (1.5 - 1.2)/4 = **-0.925**;
  2026Q2 (seed) = -0.925 + (1.5 - 1.2)/4 = **-0.85**.

---

## 4. Iteration

- `R_0` = the actual overnight rate at the MPR quarter, read from the tail of
  `data/processed/overnight_rate_target.csv` (2.25% for this vintage). The
  workbook can override via `current_overnight_rate`.
- Iteration **starts at the seed quarter (2026Q2)**; the first *projected* step
  is 2026Q3; the path ends at **2028Q4**.
- Each step applies the rule above, floored at the ELB.

---

## 5. Provenance map (every workbook field -> source)

### quarterly sheet
| Field | Source |
|---|---|
| `core_cpi_yoy_forecast` (2025Q3-2026Q2, + Q4/Q4 anchors 2026Q4/2027Q4/2028Q4) | MPR Apr-2026, Table 3 (core = avg of CPI-trim and CPI-median) |
| `total_cpi_yoy_reference` | MPR Apr-2026, Table 3 (reference only; model does not use) |
| `gdp_growth_qq_ann_forecast` (2025Q3-2026Q2) | MPR Apr-2026, Table 3 (real GDP q/q annualized) |
| `anchor_type` | derived: `quarterly` for near-term rows, `q4q4` for anchors |

### annual sheet
| Field | Source |
|---|---|
| `potential_growth_low` / `_high` | MPR Apr-2026, Table 2 (range for potential output growth); 2025 is a point estimate (2.3) |
| `gdp_q4q4` | MPR Apr-2026, Table 3 (real GDP y/y Q4/Q4 anchors: 2026 = 1.8, 2027 = 1.4, 2028 = 1.9) |

### params sheet
| Field | Value | Source / status |
|---|---|---|
| `mpr_publication_date` | 2026-04-29 | **VERIFIED** via WebFetch of bankofcanada.ca MPR page |
| `current_overnight_rate` | 2.25 | tail of `data/processed/overnight_rate_target.csv` |
| `neutral_range_low` / `_high` | 2.25 / 3.25 | **VERIFIED** via MPR Apr-2026 Appendix: "the Canadian nominal neutral rate is estimated to be within the range of 2.25% to 3.25%, unchanged from that in the April 2025 Report" |
| `output_gap_anchor_quarter` / `output_gap_anchor_value` | 2025Q4 / -1.0 | **BoC Valet `INDINF_OUTGAPMPR_Q`** (staff output gap, current MPR vintage), last published observation. Auto-filled by `make_workbook.py` from the tail of `data/raw/output_gap_mpr.csv`; rolled forward to the seed quarter by the gap identity (Section 3). |
| `rho` / `phi_pi` / `phi_gap` | 0.85 / 4.65 / 0.40 | BoC Technical Report 119, Table 2.3 |
| `inflation_target` | 2.0 | BoC 2% CPI inflation target |
| `inflation_converge_quarters` | 4 | TR-119 rule horizon (t+4) |
| `elb_floor` | 0.25 | BoC effective lower bound statements, 2009 & Apr 2020 |
| `verified` | FALSE | flip to TRUE only after checking every cell vs the MPR PDF |

---

## 6. What was verified online vs. what Jay still owns

Confirmed by WebFetch of bankofcanada.ca (April 2026 MPR):
- **MPR publication date:** April 29, 2026.
- **Neutral rate range:** 2.25%-3.25%, explicitly unchanged from the April 2025
  Report.
- Potential-growth midpoints (1.2 / 1.3 / 1.5 for 2026/2027/2028) corroborated
  in the MPR Appendix.

Output gap — now mechanical (no placeholder):
- The output-gap seed is no longer a transcribed numeric range. It is **anchored
  to the Bank's own published staff estimate** (`INDINF_OUTGAPMPR_Q` on Valet,
  last obs 2025Q4 = -1.0%) and rolled forward by the gap identity (Section 3).
  Nothing here is read from the MPR PDF text; the anchor refreshes automatically
  with the data pull.
- **Vintage caveat:** the anchor is the *current-vintage* staff output-gap
  estimate as of its last publication. The Bank revises this series across MPRs;
  a later vintage can restate 2025Q4. The model intentionally uses the freshest
  published value at run time and does not freeze a vintage.

The Table 2 / Table 3 transcriptions themselves were taken from Jay's
screenshots and are treated as authoritative pending Jay's PDF cross-check.

---

## 7. Known caveats

- **Coherence reading, not advice.** The MPR forecasts are conditioned on a
  policy path; running them back through the rule reads out the rule's implied
  rate *given those projections*. It is not the Bank's published rate path and
  not a recommendation.
- **Coefficients are historical.** The TR-119 rule was estimated over roughly
  1993Q4-2015Q4. The reaction function may have shifted since.
- **Judgmental add-factors.** Inside ToTEM the staff overlay judgment
  ("add-factors") on top of the mechanical rule, so the Bank's true internal
  path differs from the pure rule output reproduced here.
- **Interpolation choices are assumptions.** Linear interpolation between Q4/Q4
  anchors, constant within-year GDP fill, and potential-growth midpoints are all
  modelling conventions, documented above, not Bank-published quarterly values.

---

## 7b. Calc sheet (live formulas, in the workbook)

Every run writes (or replaces) a **`calc` sheet** back into the punch-in
workbook, placed **first** so it is what Jay sees on open. It is a dense
quarterly grid that **reproduces the entire policy path with live Excel
formulas** referencing the input sheets — change an input and the whole path
recomputes in Excel. (This replaced the earlier values-only `output` sheet: a
static rendering gave no ability to audit the arithmetic by hand. The legacy
`output` sheet is deleted on the next run.)

The **single source of truth for agreement** remains the tested Python engine
(`pipeline/shadow_rate/model.py`). Each computed column is paired with a static
`(python)` column carrying the engine's last-run value, and a `diff` column
`= ABS(formula − python)` with red conditional formatting if the divergence
exceeds `0.0005`. **That is the audit handshake:** Excel recomputes everything
live, and the diff columns prove the live formulas match the engine. (openpyxl
cannot evaluate formulas, so pytest covers structure + reference correctness;
runtime agreement is what the in-sheet diff columns surface in Excel.)

- **Grid range:** one row per quarter from the **gap anchor quarter (2025Q4)**
  through **2029Q4** (= the 2028Q4 horizon + 4 quarters of inflation headroom so
  the terminal quarters' t+4 lookups land on real grid rows). The pre-seed
  roll-forward region (anchor through the quarter before the seed) carries live
  gap formulas but **greyed/blank rate cells** — the rule does not iterate
  before the seed.
- **Columns (all white cells live):** `quarter | core CPI y/y | gdp q/q ann |
  potential | output gap | gap (python) | gap diff | pi t+4 | neutral mid |
  infl term | gap term | bracket | shadow rate R | R (python) | R diff`.
  - **core CPI:** direct `=quarterly!B<row>` where a value exists; explicit
    linear-interpolation formula `=quarterly!B5+(offset/span)*(quarterly!B6-quarterly!B5)`
    between bracketing known quarters; hold (`=quarterly!B8`) past 2028Q4.
  - **gdp:** direct `=quarterly!D<row>` where given, else that year's
    `=annual!D<row>` (gdp_q4q4).
  - **potential:** `=(annual!B<row>+annual!C<row>)/2`.
  - **output gap:** anchor row `=params!$B$<anchor_value>`; each later row
    `=<gap above>+(<gdp this row>-<pot this row>)/4` (t+1 timing, matches engine).
  - **pi t+4:** `=<core CPI cell 4 rows below>`.
  - **rule decomposition** all reference params cells absolutely (`$`):
    `neutral mid =(params!$B$low+params!$B$high)/2`;
    `infl term =params!$phi_pi*(pi_t4-params!$target)`;
    `gap term =params!$phi_gap*gap`; `bracket = neutral+infl+gap`;
    `shadow rate R`: seed row `=params!$current_overnight_rate`, each later row
    `=MAX(params!$rho*<R above>+(1-params!$rho)*<bracket above>,params!$elb_floor)`
    — R_{t+1} uses quarter t's bracket, mirroring `model._rule_step`.
- **Header block:** run timestamp; a big red **UNVERIFIED DRAFT** cell while
  `verified=FALSE`; anchor provenance (quarter, value, Valet source); seed
  quarter + seed rate; R*_nom; the rule citation (TR-119 Table 2.3: rho=0.85,
  phi_pi=4.65, phi_gap=0.40); and one explainer line: *"All white cells are live
  formulas — change an input and the path recomputes. The 'python' columns are
  the engine's values from the last run; diff columns flag any divergence."*
  Grid header row frozen; thin borders; 2-4 decimals.
- **Idempotent regeneration:** the whole `calc` sheet (formulas + fresh python
  values + timestamp/flag) is rebuilt on every run; the formula references are
  derived from the input sheets' row order at generation time, so a future MPR
  regenerates cleanly.
- **Input sheets are never touched.** The `quarterly` / `annual` / `params`
  sheets are read-only to this writer.
- **Windows file lock:** if the workbook is open in Excel, openpyxl's save
  raises `PermissionError`; the writer catches it and writes a companion file
  `boc_shadow_output_2026Q2.xlsx` in the same folder, printing a note to close
  Excel and re-run to embed. (Implemented in
  `pipeline/shadow_rate/output_sheet.py`, wired into `run.py` after the chart.)

## 8. Files

| Path | Purpose |
|---|---|
| `work/research/shadow_rate/boc_shadow_inputs_2026Q2.xlsx` | punch-in workbook (Jay edits) |
| `work/research/shadow_rate/boc_shadow_path_2026-04.{svg,html}` | Jay-facing chart |
| `boc_shadow_inputs_2026Q2.xlsx` → `calc` sheet | live-formula per-quarter path written back on every run, with python-check + diff columns (companion `boc_shadow_output_2026Q2.xlsx` if Excel holds the lock) |
| `data/processed/boc_shadow_rate.csv` + `.meta.json` | output series (transform `totem3_taylor_rule_shadow_path`) |
| `pipeline/shadow_rate/` | inputs / model / chart / run / make_workbook / tests |

Run: `python -m pipeline.shadow_rate.run` (real, requires `verified=TRUE`) or
`python -m pipeline.shadow_rate.run --force-unverified` (watermarked draft).
Regenerate the workbook layout: `python -m pipeline.shadow_rate.make_workbook`.
