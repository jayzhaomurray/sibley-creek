# BoC rule-implied shadow rate — methodology (April 2026 MPR vintage)

Internal Sibley Creek research tool. This is the **ToTEM III rule-implied policy
path** computed from the Bank of Canada's own published outputs: it applies
ToTEM III's estimated policy reaction function (TR-119) to the April 2026
Monetary Policy Report projections, using transparent interpolation assumptions
to turn the MPR's sparse rows into a dense quarterly path.

**What this is — and what it is NOT.** The defensible claim is: *the ToTEM III
rule-implied policy path using the April 2026 MPR projections and transparent
interpolation assumptions.* This is **NOT** a recovery of the Bank's actual
internal conditioning path. Two reasons it cannot be:

- The Bank's internal staff overlay **judgmental add-factors** on top of the
  mechanical rule, so its true internal path differs from the pure rule output.
- The MPR forecast is itself **conditioned on a market-implied rate path** (the
  Bank's published convention), not on this rule. Feeding that forecast back
  through the rule reads out what the rule implies *given those projections* — a
  **coherence reading**, not advice, not a forecast, and not the Bank's own path.

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
from target, not the contemporaneous reading. The four-quarter-ahead lookup is
part of the **rule's definition** (TR-119's (1/4)·Σ_{j=1..4} E_t π_{t+j} term),
fixed in code as `model.RULE_INFLATION_HORIZON_Q`, **not** a punch-in parameter;
the deprecated `inflation_converge_quarters` workbook field was removed
2026-06-04 (now accepted as an ignored no-op for backward compatibility).

### Inflation input = CORE, not total CPI

The model reads **core inflation** (average of CPI-trim and CPI-median, per the
MPR Table 3 footnote), not total CPI. TR-119's rule was estimated on core
inflation deviations, so total CPI would be the wrong input. The workbook carries
total CPI in a `total_cpi_yoy_reference` column for context only; `model.py`
never reads it.

#### Inflation-concept mismatch (the top-ranked input risk)

There is a **concept gap** between the inflation series TR-119's rule was
estimated on and the series we feed it, and it deserves to be flagged
prominently because the rule's inflation coefficient is large.

- **What the rule was estimated on:** TR-119's reaction function responds to the
  **4-quarter-ahead forecast of y/y CPIX** (the Bank's then-preferred core
  measure during the estimation window).
- **What we feed it:** the MPR's published core forecast = **the average of
  CPI-trim and CPI-median**, the Bank's *current* preferred core set. We use this
  because **CPIX forecasts are no longer published** — the Bank retired CPIX as
  its operational core measure in favour of the trim/median family, so there is
  no contemporaneous CPIX forecast to feed.
- **Why it's the best available mechanical proxy:** trim/median is the closest
  published successor to CPIX in role (a symmetric-trimmed-mean / weighted-median
  core gauge the Bank itself uses to read underlying inflation), and it is the
  only forward-looking core series the MPR actually publishes. Substituting it
  keeps the input mechanical and sourced rather than reconstructing a defunct
  CPIX forecast by hand.
- **Why the gap matters here specifically:** the rule's inflation response
  coefficient is **phi_pi = 4.65** — every 0.1pp of concept-driven difference
  between trim/median and a true CPIX forecast is **amplified ~0.47pp** in the
  rule's target level (before the rho=0.85 smoothing damps the per-quarter step).
  So any systematic level offset between the two core concepts feeds through with
  large leverage. The annual-average GDP cross-check (Section 10) and the
  sensitivity band (Section 9) bound the *growth/neutral* uncertainty, but the
  inflation-concept gap is a **separate, unbanded** modelling assumption: treat
  the path's level as conditional on trim/median being an acceptable CPIX proxy.

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
- **Missing quarters — residual fill.** Each missing quarter of a calendar year
  is set so the year stays consistent with its published Q4/Q4 anchor:

  ```
  remaining_rate = (4*gdp_q4q4 - sum(direct_rates_that_year)) / n_missing
  ```

  applied equally to every missing quarter of that year. This makes the four
  quarters average the anchor.
  - **Worked 2026 example:** the MPR gives 2026Q1 = 2026Q2 = 1.5 directly and a
    2026 Q4/Q4 anchor of 1.8. The two missing quarters fill at
    `(4*1.8 - 1.5 - 1.5)/2 = 2.1`, so 2026Q3 = 2026Q4 = **2.1** and the year
    averages 1.8. (The earlier convention filled Q3/Q4 at the anchor 1.8, which
    *contradicted* the anchor: a year averaging 1.8 with H1 at 1.5 needs H2 near
    2.1, not 1.8.)
  - **Years with no direct quarters** reduce to a constant fill — the residual
    with zero known terms is the anchor itself (2027: 1.4 in every quarter; 2028:
    1.9 in every quarter, since the MPR gives no direct 2027/2028 quarters).
  - **Arithmetic-mean approximation.** This treats the year's Q4/Q4 growth as the
    arithmetic mean of its four q/q-annualized rates. That is exact under
    summation and a close approximation under compounding (the difference is
    second-order in the within-year rate dispersion), and it keeps the fill a
    simple, auditable linear formula on the calc sheet.
  - **Fail-closed:** a year that needs filling but has no Q4/Q4 anchor raises. A
    year with all four quarters given directly ignores the anchor (n_missing = 0).

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
| `gdp_annual_avg` | MPR Apr-2026, Table 2 (annual-AVERAGE real GDP growth: 2026 = 1.2, 2027 = 1.6, 2028 = 1.7). Reference-only: used solely for the Section 10 cross-check, never a model input. |

### params sheet
| Field | Value | Source / status |
|---|---|---|
| `mpr_publication_date` | 2026-04-29 | **VERIFIED** via WebFetch of bankofcanada.ca MPR page |
| `current_overnight_rate` | 2.25 | tail of `data/processed/overnight_rate_target.csv` |
| `neutral_range_low` / `_high` | 2.25 / 3.25 | **VERIFIED** via MPR Apr-2026 Appendix: "the Canadian nominal neutral rate is estimated to be within the range of 2.25% to 3.25%, unchanged from that in the April 2025 Report" |
| `output_gap_anchor_quarter` / `output_gap_anchor_value` | 2025Q4 / -1.0 | **BoC Valet `INDINF_OUTGAPMPR_Q`** (staff output gap, current MPR vintage), last published observation. Auto-filled by `make_workbook.py` from the tail of `data/raw/output_gap_mpr.csv`; rolled forward to the seed quarter by the gap identity (Section 3). |
| `rho` / `phi_pi` / `phi_gap` | 0.85 / 4.65 / 0.40 | BoC Technical Report 119, Table 2.3 |
| `inflation_target` | 2.0 | BoC 2% CPI inflation target |
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

- **Coherence reading, not the Bank's path, not advice.** This is the ToTEM III
  *rule-implied* path, NOT a recovery of the Bank's actual internal conditioning
  path. The MPR forecasts are conditioned on a **market-implied rate path** (not
  on this rule), so running them back through the rule reads out the rule's
  implied rate *given those projections*. It is neither the Bank's published rate
  path nor a recommendation. (See the intro for the full statement of the
  defensible claim.)
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
  - **gdp:** direct `=quarterly!D<row>` where given; else the **residual**
    formula `=(4*annual!D<yr> - quarterly!D<k1> - quarterly!D<k2>)/n_missing`
    referencing the year's directly-given quarter cells (e.g. 2026Q3 =
    `=(4*annual!$D$3-quarterly!$D$4-quarterly!$D$5)/2`), so the four quarters
    average the year's Q4/Q4 anchor. With zero known quarters this reduces to
    `=annual!D<yr>` (the constant fill). The python-check/diff columns verify the
    live formula matches the engine at runtime.
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
- **Footer note rows:** below the grid the sheet carries (a) the engine
  handshake note, (b) a **band note row** — the sensitivity band is
  engine-computed from the published range corners and is intentionally *not*
  reproduced as in-sheet formulas (4× the grid; see Section 9), and (c) the
  **annual-average GDP cross-check** header plus one line per year (implied vs
  published, with a WARN/ok flag; see Section 10).
- **Input sheets are never touched.** The `quarterly` / `annual` / `params`
  sheets are read-only to this writer.
- **Windows file lock:** if the workbook is open in Excel, openpyxl's save
  raises `PermissionError`; the writer catches it and writes a companion file
  `boc_shadow_output_2026Q2.xlsx` in the same folder, printing a note to close
  Excel and re-run to embed. (Implemented in
  `pipeline/shadow_rate/output_sheet.py`, wired into `run.py` after the chart.)

## 9. Sensitivity band (mechanical, engine-computed)

The central path uses the **midpoints** of the published neutral-rate and
potential-growth ranges. Both range endpoints are real published uncertainty, so
the engine quantifies how much the path moves across them as a mechanical band.

### Definition
`model.run_band` reruns the rule path over the **4 corner combinations** of:

```
{neutral_low, neutral_high}  x  {potential range low, potential range high}
```

- The **neutral** pick is applied as the nominal neutral midpoint `R*_nom` (the
  range collapses to that single endpoint).
- The **potential** pick is applied **consistently to every year**: the "low
  potential" corner uses each year's published range *low* in all years, the
  "high potential" corner uses each year's range *high* in all years. The output
  gap evolves accordingly (the gap's reference path shifts), so the corners
  differ both through `R*_nom` and through the whole gap trajectory.
- Per quarter, the band is the **min / max rate across the 4 corner paths**.
- **Everything else is held at the central case** — core CPI, GDP anchors, the
  output-gap anchor, and all rule coefficients. The band isolates the
  neutral × potential sensitivity only.

### Sign logic
**Lower potential growth → actual growth exceeds potential by more → the output
gap closes faster → higher rates.** So the highest-rate corner pairs
`neutral_high` with `potential_low`, and the lowest-rate corner pairs
`neutral_low` with `potential_high`. The code does not assume this ordering — it
takes an explicit min/max over all four corners, which stays correct even when
the ELB floor flattens one corner.

### Audit-quantified sensitivity rankings

| Driver | Path impact (terminal) | Notes |
|---|---|---|
| Neutral-rate endpoints (2.25 ↔ 3.25) | **±40bp** | Largest driver; enters `R*_nom` 1-for-1 (×(1−rho) per step, accumulating). |
| Potential-growth endpoints (range low ↔ high) | **±25-30bp** | Via the gap trajectory; compounds over the horizon. |
| Output-gap anchor (±0.25pp) | **~8bp** | `phi_gap=0.40` × 0.25 × (1−rho) accumulation. |
| Inflation interpolation | **interior-only** | Linear fill between published anchors moves only the interior quarters; endpoints are pinned to published values. |
| GDP residual-fill shape | **~0.01bp** | The arithmetic-mean fill reshapes within-year quarters but preserves the Q4/Q4 anchor; near-zero net effect on the rate path. |

The band is reported in `run.py` stdout (`band_lo`/`band_hi` columns), in the
output CSV (`date, value, band_lo, band_hi, ...`), and shaded as a light fill
around the dashed central path in the chart. The **calc sheet does NOT reproduce
band formulas** (4× the grid is a complexity explosion); it carries a single note
row pointing here, and the band stays engine-computed.

The inflation-concept gap (Section 1) is a **separate, unbanded** assumption and
is not part of this envelope.

---

## 10. Annual-average GDP cross-check (coherence diagnostic)

The MPR publishes **annual-AVERAGE** real GDP growth (Table 2: 2026 = 1.2,
2027 = 1.6, 2028 = 1.7) in addition to the Q4/Q4 figures the model anchors on.
These are independent published numbers, so the engine cross-checks them against
the annual averages **implied by its own constructed quarterly path** — a
coherence diagnostic on the GDP path construction.

### Method
From the constructed quarterly q/q-annualized GDP path, the engine compounds a
**quarterly level index** (each quarter's level = prior level × (1 + g/100)^¼),
then computes each year's annual-average growth as
`mean(level over that year's 4 quarters) / mean(level over the prior year's 4
quarters) − 1`.

### Honest handling of the 2025 seam
Computing the **2026** annual average needs the full **2025** quarterly level
path as the denominator, but the MPR gives only 2025Q3/Q4 q/q growth — 2025Q1/Q2
are not available. The engine builds the 2025 level path from the available
quarters and **flags 2026 as `approximate`**. Years whose full prior-year
quarterly path is constructed from anchors — **2027 and 2028** — are the strict
check.

### Tolerance and behaviour
- **WARN if |implied − published| > 0.15pp** (rounding tolerance ~0.05pp plus
  within-year fill-shape slack). The warning surfaces in stdout, a calc-sheet
  note row, and the path-table footer.
- **It never fails the run.** This is a coherence diagnostic, not validation.

### April 2026 vintage result

| Year | Implied | Published | Diff | Status |
|---|---|---|---|---|
| 2026 | 0.972 | 1.20 | −0.228pp | WARN (approximate — 2025 seam) |
| 2027 | 1.624 | 1.60 | **+0.024pp** | **PASS** |
| 2028 | 1.713 | 1.70 | **+0.013pp** | **PASS** |

The strict-check years (2027, 2028) agree with the published annual averages to
within ~0.02pp — the residual-fill GDP construction is coherent with the Bank's
own annual-average numbers where the full prior-year path is available. The 2026
gap is expected: the incomplete 2025 denominator and the residual fill's
within-year shape pull the implied average below the published 1.2.

---

## 7c. Quarterly refresh workflow (vintage-flexible)

The tool is vintage-flexible: the projection horizon and every output stamp are
read from the workbook, not hard-coded. Each new MPR is a copy-forward, never a
regenerate. The 5-step ritual:

1. **Copy forward.** `python -m pipeline.shadow_rate.make_workbook --new-quarter
   2026Q3` reads the newest `boc_shadow_inputs_<YYYY>Q<n>.xlsx`, copies it to the
   new quarter's file, resets `verified=FALSE`, blanks `mpr_publication_date` to
   a TO-FILL marker (the runner rejects it until filled), re-seeds the gap anchor
   and overnight rate from the data tails, and **keeps last quarter's data rows**
   so you edit in place. (The seed builder refuses to overwrite an existing
   workbook; copy-forward is the only refresh path.)
2. **Punch in the new MPR.** Edit the `quarterly` and `annual` rows against the
   new MPR Tables 2-3 (core CPI, GDP q/q, Q4/Q4 anchors, potential ranges,
   annual-average GDP), and update each `source_ref` to the new vintage.
3. **Set horizon + date.** Fill `projection_end_quarter` (the new MPR's last
   projection quarter, e.g. `2028Q4`) and `mpr_publication_date` (the real
   publication date). Coverage validation checks the data reaches the horizon.
4. **Verify.** Check every transcribed cell against the MPR PDF.
5. **Flip + run.** Set `verified=TRUE`, then `python -m pipeline.shadow_rate.run`
   (no `--xlsx` needed — it globs the newest workbook). Outputs are
   vintage-stamped: `boc_shadow_path_<YYYY-MM>.{svg,html}` and a vintage copy
   `boc_shadow_rate_<YYYY-MM>.csv` accumulate alongside the stable
   `boc_shadow_rate.csv` (the current vintage, for any site wiring). Past
   vintages become the track record.

## 11. Market-implied path overlay (CORRA futures)

The chart and run now carry a third element beside the rule path and the actual
overnight history: the contemporaneous **market-implied** policy path, drawn as a
dotted green line labelled "market-implied (CORRA futures)". Built by
`pipeline/shadow_rate/market_path.py`; fetched live on every run (skip with
`--no-market`).

**Source.** The Montreal Exchange (TMX) three-month CORRA futures quote table,
symbol CRA: `https://www.m-x.ca/en/trading/data/quotes?symbol=CRA`. A single
polite HTTP GET through the repo's shared httpx client (`pipeline/fetch/_http.py`,
`get_text`). One plain HTML table, one row per quarterly contract month
(Mar/Jun/Sep/Dec) out to ~Dec 2028. We key columns off the header row, so an
upstream column re-order does not silently mis-read the settlement.

**Conversion.** Implied three-month CORRA for a contract = `100 - settlement`
(standard IMM 100-minus-rate quote convention).

**Contract-month -> reference-quarter mapping.** A three-month CORRA future
references the compounding window that begins at the contract month's IMM date and
runs ~three months forward (a "March 2026" future compounds CORRA roughly
mid-March to mid-June 2026). We assign each contract the calendar quarter that
*begins at* the contract month:

    Mar YYYY -> YYYY Q2     Jun YYYY -> YYYY Q3
    Sep YYYY -> YYYY Q4     Dec YYYY -> (YYYY+1) Q1

This lines the futures-implied rate up with the quarter over which it is the
prevailing overnight rate — the same quarter the shadow path labels — so the two
paths are directly comparable quarter-for-quarter.

**Spread adjustment (CORRA -> target).** CORRA is an overnight *funding* rate that
trades a few basis points around the Bank's target for the overnight rate, so the
futures price an instrument that is not the policy rate itself. We estimate a
constant adjustment

    spread = mean(CORRA_daily - overnight_target) over the trailing 60 business days

(Valet daily CORRA `AVG.INTWO` vs `data/processed/overnight_rate_target.csv`,
forward-filled onto the CORRA dates), and define `implied_target = implied_corra -
spread`. The spread is small and typically slightly positive — CORRA usually sits
at or a hair above target; the live 2026-06 read was **+0.029 pp**. Typical
magnitude is roughly -5 to 0 bp historically; the current small positive value
reflects CORRA printing just above target in the trailing window.

**The conditioning caveat (why the divergence is the interesting object).** The
MPR projection that feeds the *rule* path is itself **conditioned on a
market-implied rate path** — the Bank builds its forecast assuming policy follows
roughly what markets price. So the market-implied path is, to first order, the
conditioning assumption *behind* the MPR numbers, while the rule path is what the
ToTEM III reaction function *prescribes* given those same MPR projections. The
gap between them (`rule - market`, printed each run) is therefore the rule's
prescription net of what the market already prices in — not two independent
forecasts disagreeing, but the reaction function pulling against the conditioning
path. A positive gap says the rule wants a higher rate than the curve implies.

**Output + graceful failure.** Writes `data/raw/corra_futures_curve.csv` +
`.meta.json` (ADR-0002 sidecar: contract, quarter, settlement, implied_corra,
implied_target, fetched_at). Any scrape/fetch/parse error returns `None` with a
one-line stdout warning; the chart then renders exactly as before (no dotted
line) and the run prints an "unavailable" notice. Nothing downstream breaks.

**Scrape fragility.** The read depends on the TMX page exposing the CRA quotes as
server-rendered HTML in one `<table>` with a `Month` and a `Settl. price` header.
If TMX moves the quotes behind a JS/XHR endpoint, renames headers, or splits the
table, the parser raises and the overlay drops out cleanly (rule path still
ships). Settlement prices are end-of-previous-session; intraday moves are not
reflected.

## 8. Files

| Path | Purpose |
|---|---|
| `work/research/shadow_rate/boc_shadow_inputs_2026Q2.xlsx` | punch-in workbook (Jay edits) |
| `work/research/shadow_rate/boc_shadow_path_2026-04.{svg,html}` | Jay-facing chart |
| `boc_shadow_inputs_2026Q2.xlsx` → `calc` sheet | live-formula per-quarter path written back on every run, with python-check + diff columns (companion `boc_shadow_output_2026Q2.xlsx` if Excel holds the lock) |
| `data/processed/boc_shadow_rate.csv` + `.meta.json` | output series (transform `totem3_taylor_rule_shadow_path`) |
| `data/raw/corra_futures_curve.csv` + `.meta.json` | market-implied path from CORRA futures (transform `corra_futures_implied_policy_path`) |
| `pipeline/shadow_rate/market_path.py` | CORRA-futures scrape + conversion + spread adjustment (Section 11) |
| `pipeline/shadow_rate/` | inputs / model / chart / run / market_path / make_workbook / tests |

Run: `python -m pipeline.shadow_rate.run` (real, requires `verified=TRUE`) or
`python -m pipeline.shadow_rate.run --force-unverified` (watermarked draft).
Regenerate the workbook layout: `python -m pipeline.shadow_rate.make_workbook`.
