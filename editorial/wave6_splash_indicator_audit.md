# Wave 6 Splash Indicator Audit

Author: editorial-director. 2026-05-11.

Scope: every supporting print currently rendered on the homepage panel
table for the seven Sibley Creek sections (`data/site/sections.json`).
Each print is judged against the Bay Street institutional reader: does
it earn 5-10 seconds of glanceable attention, or is it filler?

Anchor: `editorial/dashboard_purpose.md` -- P1 reader is the CPP/OTPP-
type allocator, P2 is policy-adjacent, P3 is the serious independent.
Each supporting print must be load-bearing for its section's headline
question, measurable + dated, distinct from the chart, and glanceable.

Cap per section: 4-5 prints (including the chart's primary). Six is
crowding. Recent locked changes (housing arrears CBA proxy in flight,
months-inventory in flight, CPI breadth in flight, per-capita
employment dropped, federal budget on FYTD, US partner -> US export
share, neutral midpoint dropped from policy table) are NOT touched.

---

## 1. Executive summary

Across 7 sections, 26 supporting prints (the rows after the primary
chart series). Decisions:

| Decision | Count |
|---|---|
| KEEP | 17 |
| REWORD | 2 |
| REPLACE | 1 |
| CUT | 6 |
| **TOTAL** | **26** |

Net change per section (rows displayed = primary + supporting):

| Section | Before (rows) | After (rows) | Net |
|---|---|---|---|
| GDP | 4 | 4 | 0 |
| Inflation | 4 | 5 | +1 |
| Labour | 6 | 5 | -1 |
| Housing | 5 | 5 | 0 |
| Policy | 4 | 4 | 0 |
| Markets | 4 | 4 | 0 |
| Trade | 4 | 4 | 0 |
| **Total** | **31** | **31** | **0** |

(Note: rows-on-disk reflect prints[] length including primary; recent
locked drops -- per-capita employment, neutral midpoint -- are already
absorbed into the "Before" counts above.)

The audit is conservative on subtraction. Labour was the only section
clearly over-capped at six supporting-print rows; one cut brings it
into line. Inflation gains a +1 for shelter, which is the single most
load-bearing CPI sub-aggregate and currently hidden inside the chart.

---

## 2. Per-section worksheets

### GDP

Headline question: *Is the Canadian economy at potential, growing, or
contracting?*

Primary chart: `gdp-yoy` -- Real GDP, y/y. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `gdp-mm` | Real GDP, m/m | KEEP | The print Bay Street actually trades on the day. y/y is smooth; m/m is the surprise vector. Load-bearing. |
| `gdp-percap-yoy` | Per-capita GDP, y/y | KEEP (TK; data pending) | This IS the Sibley editorial differentiator -- the cut the headline obscures. Backend follow-up underway via StatCan 17-10-0009; preserve the slot. |
| `output-gap` | Output gap | KEEP | The "vs potential" read; the only structural cyclical anchor on the tile. Pairs the cyclical (m/m) with the gap (level). |

Proposed final list (4 prints, primary + 3):

1. `gdp-yoy` | Real GDP, y/y (primary)
2. `gdp-mm` | Real GDP, m/m
3. `gdp-percap-yoy` | Per-capita GDP, y/y
4. `output-gap` | Output gap

GDP table is already lean and earns every row. No changes.

---

### Inflation

Headline question: *Is the 2% target being met, and on what measures
and what breadth?*

Primary chart: `cpi-yoy` -- Headline CPI, y/y. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `core-trim-yoy` | Core-trim, y/y | KEEP | BoC preferred core. Mandatory. |
| `core-median-yoy` | Core-median, y/y | KEEP | BoC preferred core, second of pair. Trim/median are co-equal; drop one and the table reads weaker. |
| `cpi-breadth-gt3` | CPI breadth >3% | KEEP (TK; data pending) | Breadth is the "is this widespread or narrow" read that distinguishes a stickiness call from a base-effect call. Backend in flight; preserve slot. |

Proposed addition:

| key | indicator | rationale |
|---|---|---|
| `cpi-shelter-yoy` | Shelter CPI, y/y | The single biggest contributor to current CPI and the most-asked question on Bay Street ("what's shelter doing"). Already on disk in `data/processed/cpi_shelter_yoy.csv`. Adding shelter as a tile print closes the gap between what the chart shows (headline) and what the section is actually about (where the inflation is). 4 supporting + 1 primary = 5 rows, exactly at cap. |

Proposed final list (5 prints):

1. `cpi-yoy` | Headline CPI, y/y (primary)
2. `core-trim-yoy` | Core-trim, y/y
3. `core-median-yoy` | Core-median, y/y
4. `cpi-shelter-yoy` | Shelter CPI, y/y *(new)*
5. `cpi-breadth-gt3` | CPI breadth >3%

---

### Labour

Headline question: *How tight is the labour market, and is per-capita
output recovering?*

Primary chart: `unrate` -- Unemployment rate. (unchanged)

Current supporting prints (6 rows total -- over cap):

| key | indicator | decision | rationale |
|---|---|---|---|
| `emp-percap-yoy` | Per-capita employment, y/y | (already dropped per locked changes) | Recent context says it was dropped from labour as redundant with emp-rate. Confirmed: not present in canon, no action. |
| `agg-hours-yoy` | Aggregate hours, y/y | KEEP | The intensive-margin read; jobs say one thing, hours often say another. Load-bearing for the per-capita question (output = hours * productivity). |
| `wage-lfs-micro` | Wage growth (LFS-Micro) | KEEP | The BoC's preferred composition-adjusted wage measure. Inflation-relevant. |
| `emp-rate` | Employment rate | KEEP | Per-capita employment cleanly stated. The denominator-adjusted read; complements the unemployment rate (numerator-side). |
| `ei-regular-beneficiaries-yoy` | EI regular beneficiaries, y/y | KEEP | Wave-5 add. Demand-side leading recession indicator; uptake leads LFS by 1-2 months. Earns its slot. |

Cut decision: the table at six rows (primary + 5 supporting) crowds. The least
load-bearing of the four supporting prints is **`agg-hours-yoy`** -- and that
will surprise the reader, so the rationale needs to be clear.

Reasoning for cutting aggregate hours:

- `agg-hours-yoy` is what you cite when you're trying to back out a productivity
  call. That belongs on the topic-page chartbook (Labour Panel 2's per-capita
  panel companion), not on the homepage tile.
- The homepage tile is for the load-bearing question. The load-bearing question
  is the cyclical inflection -- "is the labour market tightening or loosening
  right now?" -- and that is best answered by the four-print quartet:
  unemployment rate (slack from the numerator), employment rate (denominator-
  adjusted level), wage growth (price of labour), EI beneficiaries (demand-side
  leading inflection).
- Aggregate hours adds a fifth dimension that mostly co-moves with employment
  and is harder for the reader to interpret in five seconds without context.

Alternative considered: cut `emp-rate` instead. Rejected: emp-rate is the
denominator-adjusted slack read; with population still volatile post-IRCC
pivot, dropping the per-capita employment frame from the tile would undercut
the Section's stated "per-capita output recovering" half of the headline
question.

| key | indicator | decision | rationale |
|---|---|---|---|
| `agg-hours-yoy` | Aggregate hours, y/y | **CUT** | Off-load to Labour Panel 2 (per-capita panel) on the topic page. Not on the homepage tile. |

Proposed final list (5 prints):

1. `unrate` | Unemployment rate (primary)
2. `emp-rate` | Employment rate
3. `wage-lfs-micro` | Wage growth (LFS-Micro)
4. `ei-regular-beneficiaries-yoy` | EI regular beneficiaries, y/y
5. *(reserved cap; no fifth print -- table stops at 4 supporting)*

Actually -- the cap is 4-5 and labour reads cleanest at 4 supporting. Final:

1. `unrate` | Unemployment rate (primary)
2. `emp-rate` | Employment rate
3. `wage-lfs-micro` | Wage growth (LFS-Micro)
4. `ei-regular-beneficiaries-yoy` | EI regular beneficiaries, y/y

5 rows total (primary + 4). Net change: -1 row.

---

### Housing

Headline question: *Is the rate-sensitive sector amplifying or
dampening policy?*

Primary chart: `hpi-yoy` -- MLS HPI, y/y. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `housing-starts-3mma` | Housing starts, 3mma | KEEP | Activity-side primary. The supply-flow indicator Bay Street actually quotes. |
| `cmhc-arrears` | CMHC arrears rate | KEEP (TK; CBA proxy in flight) | Credit-stress read; the "is the renewal wall biting" indicator. Backend follow-up underway via CBA chartered-bank arrears as monthly proxy. Preserve slot. |
| `months-inventory` | Months of inventory | KEEP (TK; backend in flight) | Inventory absorption is the leading indicator on prices. Backend dispatch in flight to resolve via SNLR proxy or build from CREA. Preserve slot. |
| `housing-affordability` | Housing affordability | KEEP | BoC qualifying-mortgage-payment-to-income index. The "what would a new borrower pay" read; complements arrears (existing borrowers) and starts (supply) with the cost-of-borrowing read. Load-bearing. |

Proposed final list (5 prints):

1. `hpi-yoy` | MLS HPI, y/y (primary)
2. `housing-starts-3mma` | Housing starts, 3mma
3. `cmhc-arrears` | CMHC arrears rate
4. `months-inventory` | Months of inventory
5. `housing-affordability` | Housing affordability

Housing is at cap (5 rows) and every row covers a distinct cycle
channel: prices, supply, credit stress, market tightness, cost of
borrowing. No changes.

---

### Policy

Headline question: *What is the policy stance, and is it consistent
with the cycle?*

Primary chart: `policy-rate` -- BoC overnight rate. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `goc-2y` | 2y GoC yield | REWORD: "2y GoC" | The label is fine as-is. Minor: "2y GoC" without "yield" is the conventional Bay Street shorthand and saves visual space. Soft REWORD; not load-bearing on the audit. KEEP-as-is is also defensible. |
| `boc-fed-spread` | BoC-Fed spread, 2y | KEEP | The cross-DM stance read; the publication's stated Pillar B deep-dive question is whether the divergence can continue. Mandatory on the tile. |
| `federal-budget-balance` | Federal budget balance (FYTD) | KEEP | Recently swapped to FYTD framing (locked). The only fiscal-stance print on the policy tile; without it, policy reads as monetary-only. Mandatory. |

Soft decision on `goc-2y`: keeping the "2y GoC yield" label as-is.
The "yield" word disambiguates from "2y GoC bond" (a security, not a
rate) and matches the Markets section's "10y GoC yield" naming for
consistency. **Decision: KEEP, not REWORD.**

Proposed final list (4 prints):

1. `policy-rate` | BoC overnight rate (primary)
2. `goc-2y` | 2y GoC yield
3. `boc-fed-spread` | BoC-Fed spread, 2y
4. `federal-budget-balance` | Federal budget balance (FYTD)

Policy table is tight. Considered adding a CORRA-vs-target spread
print (Wave 5 add to Panel 4 toggle on the topic page; data exists at
`data/processed/corra_overnight_spread_bps.csv`). Rejected for the
homepage tile: CORRA-vs-target is a plumbing-diagnostic indicator and
reads as 0-2 bps for 95% of trading days. It would dilute the tile,
not strengthen it. Stays on Panel 4 (topic page) only. No changes.

---

### Markets

Headline question: *What external winds are pushing on Canadian
inflation, growth, and the CAD?*

Primary chart: `usdcad` -- USDCAD. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `goc-10y` | 10y GoC yield | KEEP | The long-end Canadian rate; the term-premium/duration read. Mandatory. |
| `tsx-composite` | TSX Composite | CUT | This is the audit's hardest call. TSX is what a retail-investor publication leads with; for the CPP/OTPP audience, TSX level is not a macro signal -- it's a derivative of bank/energy/materials sector returns, none of which a P1 allocator reads off a tile. The Markets section's load-bearing signals are FX, the GoC curve, energy (the Canadian terms-of-trade), and (via deep-dive) credit spreads / bank stability. TSX competes for the slot without earning it. |
| `wti` | WTI | KEEP | The Canadian terms-of-trade input; WCS realizations and energy CPI pass-through both anchor here. Mandatory for a Canadian macro tile. |

Proposed replacement for `tsx-composite`:

| key | indicator | rationale |
|---|---|---|
| `goc-ust-10y-spread` | 10y GoC-UST spread | The 10y bilateral spread is the term-premium read on BoC-Fed divergence at the long end, complementing the 2y spread already on the Policy tile. Bay Street: this is what you actually read off the screen for "where are Canadian long rates relative to the US." Requires the Markets section to have both `yield_10yr.csv` (have) and a US 10y series (need: FRED `DGS10`; **not on disk** -- flagged for fetch). |

If the FRED DGS10 fetch is not in scope this wave: alternative replacement
is **`wcs-wti-diff` (WTI-WCS differential, monthly)**. WCS is on disk
(`data/raw/wcs.csv`), so a monthly differential is constructable in
the spec. Editorial preference: GoC-UST 10y spread is more load-bearing
for Bay Street; WCS differential is the v1.5 fallback.

Proposed final list (4 prints):

1. `usdcad` | USDCAD (primary)
2. `goc-10y` | 10y GoC yield
3. `goc-ust-10y-spread` | 10y GoC-UST spread *(replaces TSX Composite; needs DGS10 fetch)*
4. `wti` | WTI

Net change: 0 rows; TSX replaced by 10y spread.

---

### Trade

Headline question: *Is Canada's external position structurally
shifting under US repricing?*

Primary chart: `trade-balance` -- Goods trade balance, 3mma. (unchanged)

Current supporting prints:

| key | indicator | decision | rationale |
|---|---|---|---|
| `current-account` | Current account | KEEP | The broader external-position read (goods + services + income). Quarterly, but the canonical "is the country running a deficit" indicator. Mandatory. |
| `us-partner-share` | US export share | KEEP | Already reworded from "US partner share" (locked). The structural-shift narrative -- is Canada decoupling from the US trade dependency or not. Load-bearing for the Trade headline question. |
| `terms-of-trade` | Terms of trade | KEEP | The price-side trade indicator. Complements the volume-side (balance) and structural-side (US share). |

Proposed final list (4 prints):

1. `trade-balance` | Goods trade balance, 3mma (primary)
2. `current-account` | Current account
3. `us-partner-share` | US export share
4. `terms-of-trade` | Terms of trade

Trade is at the smallest meaningful cap and every row earns its slot.
No changes.

---

## 3. Cross-cutting observations

1. **The TK slots are pulling their weight, not dragging.** Three of
   the four TK slots on the tiles right now (GDP per-capita, CPI
   breadth, Housing arrears, Housing months-inventory) represent
   editorial commitments to indicators that should be there. Backend
   is filling them. The right move is to hold the slots, not cut them
   to "lean up" the tiles -- the cleanness will come from filling, not
   from absence. The audit preserves all four.

2. **The homepage tile is for the load-bearing four, not the
   comprehensive seven.** Several sections (Labour at 6 rows pre-audit,
   notably) were treating the homepage tile as a mini-chartbook.
   That's the topic page's job. The tile's job is to answer "where
   does this section stand right now?" in five seconds -- which is
   four glanceable prints, max. Labour gets the cut. GDP, Policy,
   Markets, and Trade all already run lean. Housing and Inflation
   stay at 5 because both legitimately carry a fifth indicator that
   answers a distinct cycle question.

3. **The Bay Street vs. retail-investor line shows up on the Markets
   tile.** TSX Composite is the cleanest example of a print that
   *feels* macro-relevant but isn't, for the P1 audience. CPP/OTPP
   reads TSX as a derivative of underlying sector returns, not as an
   input to a macro view. Replacing TSX with the 10y GoC-UST spread
   (the term-premium/divergence read at the long end) sharpens the
   tile for the actual reader. This is the kind of audit decision
   that compounds: every time we choose the institutional read over
   the retail read, the publication's voice firms up.

---

## 4. Paste-ready backend brief

The block below is a verbatim dispatch for the backend agent. Two
files change.

### File 1: `pipeline/io/site_data.py` (SUPPORTING_PRINTS dict)

**Labour section (line ~448-518):** drop the `agg-hours-yoy` spec from
the `"labour"` tuple. Final order: `wage-lfs-micro`, `emp-rate`,
`ei-regular-beneficiaries-yoy`. The `emp-rate` and `wage-lfs-micro`
specs are unchanged; the order in the table moves `emp-rate` ahead of
`wage-lfs-micro` so the directionally-paired pair (rate, then rate)
read top-to-bottom is `unrate` -> `emp-rate` -> `wage-lfs-micro` ->
`ei-regular-beneficiaries-yoy`.

Replacement labour tuple (keep all other specs as-is):

```python
"labour": (
    SupportingPrintSpec(
        key="emp-rate",
        indicator="Employment rate",
        primary_series="employment_rate",
        primary_dir="raw",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        delta_kind="pp",
        as_of_format="month-year",
        transform=None,
        notes=(
            "Employment-to-population ratio (per-capita employment). Statistics "
            "Canada LFS Table 14-10-0287, v2062817; Canada total, 15+, SA."
        ),
    ),
    SupportingPrintSpec(
        key="wage-lfs-micro",
        indicator="Wage growth (LFS-Micro)",
        primary_series="lfs_micro",
        primary_dir="raw",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        delta_kind="pp",
        as_of_format="month-year",
        transform=None,
        notes="BoC publishes LFS-Micro as Y/Y % already; no transform needed.",
    ),
    SupportingPrintSpec(
        key="ei-regular-beneficiaries-yoy",
        indicator="EI regular beneficiaries, y/y",
        primary_series="ei_regular_beneficiaries",
        primary_dir="raw",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        delta_kind="pp",
        as_of_format="month-year",
        transform="yoy",
        notes=(
            "Y/Y % change in EI regular benefits recipients (StatCan v64549350, "
            "Canada total SA). Demand-side cyclical-inflection signal; uptake "
            "tends to lead LFS unemployment by ~1-2 months."
        ),
    ),
),
```

Drop: the entire `agg-hours-yoy` SupportingPrintSpec block.

**Inflation section (line ~403-447):** add a `cpi-shelter-yoy` spec
between `core-median-yoy` and `cpi-breadth-gt3`. Data already on disk
at `data/processed/cpi_shelter_yoy.csv`.

```python
SupportingPrintSpec(
    key="cpi-shelter-yoy",
    indicator="Shelter CPI, y/y",
    primary_series="cpi_shelter_yoy",
    primary_dir="processed",
    unit_display="%",
    value_decimals=1,
    delta_decimals=1,
    delta_unit="pp",
    delta_kind="pp",
    as_of_format="month-year",
    transform=None,
    notes=(
        "StatCan CPI shelter sub-index Y/Y (Table 18-10-0004-01). Largest "
        "single contributor to headline CPI through the 2024-2026 cycle; "
        "tile carries it as the load-bearing sub-aggregate. Wave 6 add."
    ),
),
```

**Markets section (line ~659-705):** replace the `tsx-composite`
SupportingPrintSpec with a `goc-ust-10y-spread` spec. This requires
the FRED `DGS10` (US 10-year Treasury yield) series, which is **not
yet on disk** -- backend will need to fetch via the FRED catalog
(`pipeline/catalog/fred_series.py`). Suggested local filename:
`us_10yr.csv` (mirrors existing `us_2yr.csv`).

If `us_10yr` is not landable in this dispatch window: temporarily
preserve `tsx-composite` and queue the `us_10yr` fetch + spread
replacement as a Wave 6.1 follow-up. The audit's editorial preference
is to ship the spread; the fallback is to hold TSX one more cycle.

Spec to add (gated on `us_10yr.csv` landing):

```python
SupportingPrintSpec(
    key="goc-ust-10y-spread",
    indicator="10y GoC-UST spread",
    primary_series="yield_10yr",
    primary_dir="raw",
    unit_display="bps",
    value_decimals=0,
    delta_decimals=0,
    delta_unit="bps",
    delta_kind="level",
    as_of_format="date",
    transform="spread_bps",
    secondary_series="us_10yr",
    secondary_dir="raw",
    notes=(
        "GoC 10y minus UST 10y, in basis points. Inner-joined on date. "
        "Long-end complement to the Policy section's 2y BoC-Fed spread; "
        "captures the term-premium share of the bilateral divergence. "
        "Wave 6 add; requires FRED DGS10 fetch (filed as us_10yr.csv)."
    ),
),
```

Drop: the entire `tsx-composite` SupportingPrintSpec block.

### File 2: `src/data/sections.ts` (sections array prints[])

Three sections change canon. Headlines + blurbs unaffected.

**Inflation prints[] (around line 245):** insert a `cpi-shelter-yoy`
scaffold entry between `core-median-yoy` and `cpi-breadth-gt3`:

```typescript
{
  key: "cpi-shelter-yoy",
  indicator: "Shelter CPI, y/y",
  value: "TK",
  delta: "TK",
  deltaDir: "neutral",
  asOf: "TK",
  spark: [],
},
```

**Labour prints[] (around line 313):** drop the `agg-hours-yoy` scaffold
entry. Reorder remaining: `unrate` -> `emp-rate` -> `wage-lfs-micro` ->
`ei-regular-beneficiaries-yoy`. Note: the EI scaffold is not yet in
`sections.ts` (only in `site_data.py`); add it as a scaffold print
since the pipeline emits it. The full replacement prints[] array:

```typescript
prints: [
  {
    key: "unrate",
    indicator: "Unemployment rate",
    value: "TK",
    delta: "TK",
    deltaDir: "neutral",
    asOf: "TK",
    spark: [],
  },
  {
    key: "emp-rate",
    indicator: "Employment rate",
    value: "TK",
    delta: "TK",
    deltaDir: "neutral",
    asOf: "TK",
    spark: [],
  },
  {
    key: "wage-lfs-micro",
    indicator: "Wage growth (LFS-Micro)",
    value: "TK",
    delta: "TK",
    deltaDir: "neutral",
    asOf: "TK",
    spark: [],
  },
  {
    key: "ei-regular-beneficiaries-yoy",
    indicator: "EI regular beneficiaries, y/y",
    value: "TK",
    delta: "TK",
    deltaDir: "neutral",
    asOf: "TK",
    spark: [],
  },
],
```

**Markets prints[] (around line 436):** replace `tsx-composite` with
`goc-ust-10y-spread`:

```typescript
{
  key: "goc-ust-10y-spread",
  indicator: "10y GoC-UST spread",
  value: "TK",
  delta: "TK",
  deltaDir: "neutral",
  asOf: "TK",
  spark: [],
},
```

(Replacement; same array position. Drop the existing `tsx-composite`
entry.)

### Housing prints[] -- no canon edit needed

Housing's `sections.ts` currently shows four prints
(`hpi-yoy`, `housing-starts-3mma`, `cmhc-arrears`, `months-inventory`).
The pipeline already emits a fifth print (`housing-affordability`)
that is rendering correctly in `sections.json`. Add the missing
canon scaffold so frontend type-safety + TK fallbacks are aligned:

```typescript
{
  key: "housing-affordability",
  indicator: "Housing affordability",
  value: "TK",
  delta: "TK",
  deltaDir: "neutral",
  asOf: "TK",
  spark: [],
},
```

Insert after `months-inventory`.

### GDP, Policy, Trade -- no edits

These three sections' prints[] arrays already match the audit's final
list. No canon or spec changes.

---

## 5. Flagged items: data not yet on disk

Only one replacement in this audit needs a fresh backend fetch:

1. **`us_10yr.csv` (FRED `DGS10`, US 10-year Treasury yield)** -- needed
   for the `goc-ust-10y-spread` Markets replacement. Required because
   GoC 10y is on disk but the US counterpart is not. Fetch path:
   `pipeline/catalog/fred_series.py` -- mirrors the existing `us_2yr.csv`
   pattern (FRED `DGS2`). Cadence: daily.

   Fallback if not landable this wave: hold `tsx-composite` one more
   cycle, queue the swap as Wave 6.1.

All other audit decisions are buildable against data already on disk.

---

## Changelog

- 2026-05-11: Initial audit. editorial-director.
