# LFS-micro nowcast — same-day input scoping

Scoping only; nothing pulled into the pipeline. Branch `lfs-micro`.

**Target to nowcast:** BoC composition-adjusted wage growth (SAN 2024-23,
Oaxaca-Blinder on LFS microdata). Published series = Valet `INDINF_LFSMICRO_M`,
cached at `data/raw/lfs_micro.csv` (y/y %, starts 2000-01). The nowcast must
use ONLY data on the StatCan WDS that publishes at 8:30 ET on LFS release
morning.

---

## 0. Environment blocker (read first)

The WDS API host `www150.statcan.gc.ca` is **TLS-handshake-blocked in this
sandbox**. Diagnosis run during scoping:

- `www.statcan.gc.ca` → reachable (HTTP 200).
- `www150.statcan.gc.ca` → DNS resolves (167.44.105.20), raw **TCP :443
  connects**, but the **TLS handshake times out** (`_ssl.c:1063 handshake
  operation timed out`). Same failure via the project client
  (`pipeline/fetch/statcan.py`) and via bare `httpx`, sandboxed and
  unsandboxed. This is SNI/DPI-level egress filtering on that host in this
  environment, not a code or credential problem — Jay's normal pipeline runs
  reach it fine.

Consequence: I could **not** execute a live `getDataFromVectorsAndLatestNPeriods`
test from here. Dimension/frequency/release facts below were verified via
WebFetch against the StatCan table pages + The Daily + WDS-mirrored search
metadata (different egress, works). The **vector-ID confirmation calls are
listed in §6 for Jay to run in a normal terminal** — a 2-minute paste.

---

## 1. Table inventory — the MONTHLY, same-day LFS wage family (14-10-0063 → 0069)

All confirmed: monthly, unadjusted for seasonality, LFS-sourced, history from
**January 1997**, most recent reference period **April 2026, released
2026-05-08** (the LFS release day — see §2). These are the only wage cross-tabs
in the 8:30 bundle.

| PID | Title | Frequency | SA? | Dimensions (besides Geography) | Wage members | Counts? |
|---|---|---|---|---|---|---|
| **14-10-0063-01** | Employee wages by **industry** | Monthly | NSA | Wages, Type of work (FT/PT), Gender, Age group, Industry (NAICS) | avg hourly, avg weekly, median hourly, median weekly | Total # employees is a Wages member |
| **14-10-0064-01** | Employee wages by **occupation** | **ANNUAL** | NSA | Wages, Type of work, Gender, Age group, Occupation | (annual only) | — |
| **14-10-0065-01** | Employee wages by **job permanency & union coverage** | Monthly | NSA | Wages, Gender, Age group, Job permanency (perm/temp), Union coverage | avg/median hourly & weekly | yes |
| **14-10-0066-01** | Employee wages by job permanency & union coverage | **ANNUAL** | NSA | (annual companion to 0065) | — | — |
| **14-10-0067-01** | **Employment** by **establishment size** (x1,000) | Monthly | NSA | NAICS, Gender, Age group (counts only — no wage) | n/a (counts) | yes (count table) |
| **14-10-0068-01** | Employment by establishment size | **ANNUAL** | NSA | — | — | — |
| **14-10-0069-01** | **Union coverage** by industry (x1,000) | Monthly | NSA | Union coverage, Gender, Age group (counts) | n/a (counts) | yes (count table) |

**Companion EMPLOYMENT-COUNT (composition-share) tables, same-day monthly:**
- 14-10-0063 itself exposes "Total number of employees" as a Wages-dimension
  member, so for the industry / FT-PT / sex / age cells you get **mean wage AND
  cell count from a single table** — exactly what a fixed-weight aggregation
  needs.
- 14-10-0067 (establishment-size counts) gives **size shares** even though
  wage×size is unavailable.
- Standard LFS employment tables (14-10-0023 employment by industry/class;
  14-10-0287 the headline characteristics table) publish same-day for any extra
  share denominators.

### The presentation table that proves same-day availability

The Daily's **Table 11** — "Average usual hours and wages of employees by
selected characteristics, unadjusted for seasonality" (release page
`dq250509a` / `t011a`) — is published *in the 8:30 release itself*. Its rows
enumerate exactly which wage cross-tabs are same-day:

- Age groups (15+, 15–24, 25+)
- Gender (men, women)
- **Union coverage / no union coverage**
- **Permanent / temporary employees**
- **Occupation** (10 broad groups: management; business/finance; sciences;
  health; education/law/social; arts/culture/rec; sales/service;
  trades/transport; natural resources/agriculture; manufacturing/utilities)
- **Full-time / part-time** split on every measure

Columns: **number of employees (000s)**, avg weekly hours, avg weekly wage,
avg hourly wage — for total / FT / PT. This is the count+wage pairing per cell,
confirmed for the same morning. (Note: Table 11 shows broad **occupation**
groups monthly even though the *changeable table* 14-10-0064 occupation cut is
annual — the monthly occupation wage detail therefore lives in the
LFS-microdata / Table-11 layer, not in a standalone changeable cube. See §3.)

---

## 2. Release-timing confirmation

- LFS monthly release fires at **8:30 a.m. ET** (StatCan standard; the LFS Daily
  is the canonical 8:30 print).
- The wage family 14-10-0063 / 0065 / 0067 / 0069 all show **release date
  2026-05-08** (April 2026 reference month) — the same day as the April LFS
  Daily. Confirmed on each table's metadata page.
- The **ANNUAL** tables (0064 occupation, 0066, 0068) last released
  **2026-01-09** — once a year, NOT in the monthly bundle. Do not build the
  nowcast on any annual table.
- Table 11 ships inside the Daily release page itself → same-day by
  construction.

**Verdict:** the monthly 0063/0065/0067/0069 family + Daily Table 11 are
genuinely available at 8:30 ET on release morning. The annual detailed cuts
are not.

---

## 3. Coverage of the LFS-micro regression characteristics (same-day aggregates)

The SAN 2024-23 Oaxaca-Blinder controls vs. what a same-day aggregate cross-tab
can see:

| Regression characteristic | Same-day wage×char cross-tab? | Source |
|---|---|---|
| Industry (NAICS) | **Yes** (wage + count) | 14-10-0063 |
| Occupation (broad, 10-group) | **Yes** monthly via Table 11; changeable cube is annual | Daily Table 11 |
| Age group | **Yes** | 0063 / 0065 / Table 11 |
| Sex / gender | **Yes** | 0063 / 0065 / Table 11 |
| Education | **No monthly wage cut.** 14-10-0019 gives LFS chars by education monthly but **no wage**; wage×education is annual only | gap |
| Job tenure | **No** (not an LFS aggregate dimension at all) | gap |
| Union coverage | **Yes** (wage in 0065; counts in 0069) | 0065 / Table 11 |
| Full-time / part-time | **Yes** | 0063 Type-of-work / Table 11 |
| Permanent / temporary | **Yes** (wage in 0065) | 0065 / Table 11 |
| Public / private sector | **No same-day wage cut.** Class-of-worker counts ship monthly (14-10-0023) but not wage×sector | partial (counts only) |
| Establishment / firm size | **Counts only** (14-10-0067 monthly); **no wage×size** | partial (counts only) |
| Province | **Yes** (geography on every wage table) | 0063 / 0065 |
| Immigration | **No same-day wage cut** (immigrant LFS chars are quarterly/3-mma, not in the monthly wage cubes) | gap |
| Marital status | **No** aggregate wage cut | gap |
| Multiple-job holding | **No** aggregate wage cut | gap |

**Dimensions structurally unavailable same-day (confirmed):** education×wage,
tenure, public/private×wage, establishment-size×wage, immigration×wage,
marital, multiple-job. These are exactly the controls that only exist on the
microdata — which is precisely why the BoC measure needs the micro file and a
real-time aggregate proxy is worth building.

**Available same-day for composition adjustment:** industry, occupation (broad),
age, sex, FT/PT, permanent/temp, union, province — 8 of the ~14 controls, and
the ones that carry most of the cyclical composition shift (industry mix, age
mix, FT/PT mix move most over the cycle).

---

## 4. Recommended feature set

Standard: clearest construction that works; small interpretable regression
beats a kitchen sink. The economic target is the **gap** between raw average
hourly wage growth and what growth would have been holding composition fixed —
i.e. a real-time Laspeyres analogue of the BoC's Oaxaca decomposition.

### Core construction (the spine)

For a chosen cell partition, define month-`t` overall mean wage and a
**fixed-weight (Laspeyres) mean wage** that holds the employment shares at their
year-ago (t-12) levels:

```
raw_t       = sum_c ( share_{c,t}  * wage_{c,t} )          # = published overall mean
fixed_t     = sum_c ( share_{c,t-12} * wage_{c,t} )        # composition held at t-12
yoy_raw     = raw_t   / raw_{t-12}   - 1
yoy_fixed   = fixed_t / raw_{t-12}   - 1
comp_effect = yoy_raw - yoy_fixed                          # composition contribution
```

`share_{c}` = cell employee count / total; both numerator and wage come from
the **same** monthly table, so there is no vintage-mismatch risk. `yoy_fixed`
is the composition-purged wage-growth proxy; `comp_effect` is the direct
read on how much composition is flattering/depressing the raw number.

### Features fed to the nowcast regression (parsimonious)

1. **`yoy_raw`** — y/y growth of overall avg hourly wage (the headline number;
   the thing everyone reacts to, and the BoC measure's starting point).
2. **`yoy_fixed_occ`** — Laspeyres fixed-weight growth over the **10 broad
   occupation** cells (Table 11). Occupation mix is the single largest driver in
   the SAN decomposition; this is the highest-value regressor.
3. **`yoy_fixed_ind`** — fixed-weight growth over **industry** cells (0063).
4. **`yoy_fixed_agesex`** — fixed-weight growth over **age×sex** cells
   (0063/0065). Captures the youth-entry / retirement composition swing.
5. **`comp_effect_occ`** (= 1 − 2) and **`comp_effect_ind`** (= 1 − 3) — the
   composition gaps themselves, as direct proxies for the Oaxaca composition
   term. Likely the most predictive single features.
6. **`ftpt_share_chg`** — y/y change in the part-time employment share (0063
   Type-of-work). FT/PT mix is a known same-day composition lever.

That is 6–8 columns, all derivable from 14-10-0063 + 14-10-0065 + Daily Table 11,
all from the same 8:30 vintage. Recommended model: a small OLS / elastic-net of
`INDINF_LFSMICRO_M` (y/y) on features 1–6 with maybe one AR lag of the target.
The hypothesis worth testing first and cheapest: **`yoy_fixed_occ` alone tracks
the BoC measure better than `yoy_raw`**, because the BoC measure *is*
composition-adjusted — if so, the nowcast is close to a one-feature model and
maximally explainable.

### Deliberately excluded

- Wage×education, ×tenure, ×sector, ×firm-size, ×immigration — no same-day
  source. Don't fake them with annual data (stale by up to 16 months and
  introduces a look-ahead/vintage seam).
- Median wage series — keep mean (the BoC measure is mean-based); median is a
  robustness check, not a feature.
- Province cells — province is available but the BoC measure is national and
  cross-province composition is slow-moving; adds columns, little signal. Hold
  as a v2 robustness cut.

---

## 5. Verified facts vs. what still needs a live check

**Verified by WebFetch (StatCan pages / The Daily / WDS-mirrored search):**
- Table PIDs, titles, frequencies, NSA status, history start (1997), and the
  2026-05-08 vs 2026-01-09 release-date split (monthly vs annual). High
  confidence.
- Daily Table 11 row/column structure and its same-day publication. High
  confidence (read the actual table page).
- 14-10-0063 wages-dimension members (avg/median hourly & weekly + total
  employees). High confidence (WDS-mirrored search snippet + Daily Table 11
  column set agree).

**Not yet live-verified (blocked by §0):** the exact **vector IDs** for the
specific cells the features need, and a live data round-trip. Listed in §6.

---

## 6. Vector-ID verification to run in a normal terminal (paste-ready)

`www150` is TLS-blocked in the sandbox, so run this where the pipeline normally
runs. It exercises the real client and prints the latest 3 obs + release date.
Replace the placeholder vector IDs once confirmed from each table's "Add/remove
data → Reference period / download options" (the V-number per cell):

```python
# from repo root, normal terminal
from pipeline.fetch.statcan import fetch_vectors

# Candidate vectors to confirm (FILL with real V-ids from the table UI):
#   overall avg hourly wage, all employees, Canada      -> 14-10-0063
#   total # employees, all, Canada                       -> 14-10-0063
#   avg hourly wage, one occupation cell                 -> Table 11 layer
candidates = {
    "wage_overall_hourly": 0,   # TODO V-id from 14-10-0063 (Wages=avg hourly, all chars)
    "emp_count_overall":   0,   # TODO V-id from 14-10-0063 (Wages=total # employees)
    "wage_union_hourly":   0,   # TODO V-id from 14-10-0065 (union coverage cell)
}
res = fetch_vectors([v for v in candidates.values() if v])
for k, v in candidates.items():
    if v and v in res:
        r = res[v]; print(k, v, "release", r.release_date)
        print(r.data.tail(3).to_string())
```

Fastest way to get the V-ids: open each table (e.g.
`tv.action?pid=1410006301`), select the single cell you want, then "Download
options → download selected data" or hover the cell — WDS exposes the
`vectorId`. Alternatively `getCubeMetadata`/`getSeriesInfoFromCubePidCoord`
once on the unblocked network. I did not guess V-ids here to avoid shipping an
unverified number (no-TK rule).

---

## 7. Blockers / open items

1. **TLS egress to www150 in sandbox** — blocks live WDS calls from automated
   runs *in this environment only*. Confirm the production/cron environment
   reaches www150 (Jay's manual runs do). If the eventual nowcast job runs in a
   restricted CI, this needs a network-allowlist check before go-live.
2. **No live vector round-trip done** — §6 paste closes this in ~2 min.
3. **Monthly occupation wage cells live in the Table-11 layer, not a standalone
   changeable cube.** Need to confirm whether the 10-group occupation wage cells
   are individually vector-addressable on WDS or only via the
   `t011a` presentation table / the underlying LFS-micro. If only presentation,
   the occupation feature (#2, the highest-value one) may require parsing the
   Daily table HTML rather than a clean vector pull — flag for the build phase.
