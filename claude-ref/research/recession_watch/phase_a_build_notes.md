# Recession Watch Phase A — Build Notes

**Date:** 2026-06-02
**Status:** Complete. Output verified.

---

## Chain findings (critical for downstream)

The back_history_recon planned a 3-stage chain (36100390 -> 36100398 -> 36100434).
During build we discovered:

- **36100390 SAAR series starts 1997-01** for price member 2 ("Chained 1997 dollars").
  **Price member 1 ("1997 constant dollars", fixed-weight) starts 1981-01 and is what we use.**
- **36100398 SAAR series starts 1997-01 only** — despite the cube metadata showing
  `cubeStartDate = 1981-01-01`. The pre-1997 data in 36100398 is trading-day adjusted, not SAAR.
  36100398 therefore does NOT extend the back-history before 1997.
- **The effective chain is direct: 36100390 (1981-2007) -> 36100434 (1997-present).**
  Splice calibrated over the 1997-01 to 2007-07 overlap (127 months).

**Splice ratio (total GDP level, 390->434): 1.4996**
The ratio reflects: fixed-weight 1997$ (390) vs chained 2017$ (434). At 1.5x, reasonable.

## Common sector set (19 sectors across 1981-present)

Sectors present in BOTH 36100390 and 36100434 at the NAICS 2-digit level:
`11 21 22 23 31-33 41 44-45 48-49 51 52 53 54 56 61 62 71 72 81 91`

Notable missing sector from the common set: **55** (Management of companies) — not
present in 36100390 at this code level. No material impact on breadth.

## Leaf-industry count for fine GDP breadth

187 leaf NAICS industries identified from 36100434 (1997+). These are terminal nodes
in the NAICS hierarchy (no child industries). This is higher than the ~84 3-digit
industries cited in the scoping recon, because the leaf identification includes some
4-digit and 5-digit sub-industries that have no children in the table.

## Current readings (as of 2026-06-02 run)

| Metric | Current reading | Peak date | Duration |
|---|---|---|---|
| GDP depth | -0.001% | 2026-02-01 | 1 month |
| GDP breadth (19 sectors) | 52.6% | 2026-02-01 | 1 month |
| Employment depth | -0.288% | 2026-02-01 | 2 months (anchored to GDP peak) |
| Employment breadth (17 sectors) | 47.1% | 2026-02-01 | 2 months |
| Fine GDP breadth (187 industries) | 51.9% | 2026-02-01 | 1 month |

Note: Employment series runs through April 2026 (2 months past March 2026 GDP);
GDP peak detected at 2026-02-01 (Feb); LFS breadth uses GDP peak as the anchor.

## Comparator troughs (all recessions)

| Recession | GDP depth | GDP breadth | Emp depth | Emp breadth |
|---|---|---|---|---|
| 1981-82 | -4.29% | 68.4% | -5.03% | 70.6% |
| 1990-92 | -3.07% | 57.9% | -3.19% | 58.8% |
| 2008-09 | -4.44% | 84.2% | -1.92% | 82.4% |
| 2020 | -13.03% | 100.0% | -13.24% | 100.0% |

## Caveat log for charts

1. **Price convention seam at 1997:** 36100390 uses fixed-weight 1997$ (not chained).
   Breadth is not affected (sign-of-growth only); depth comparisons pre-1997 carry a
   small level-shift artifact already absorbed by the splice calibration.

2. **COVID scale:** 2020 trough is ~3x deeper than the next worst comparator.
   Charts should note or truncate the COVID path. Emit true values; chart-builder handles.

3. **LFS breadth denominator is 17 sectors** (not 16) because Wholesale trade [41]
   and Retail trade [44-45] are available as separate series from 2001 onward.
   We include both when available, giving 17 named sector columns vs the 16 named
   in the original 14-10-0355 description. This is consistent across all time periods
   from 2001+; pre-2001 has combined W+R (affects comparator paths slightly).

4. **GDP peak at 2026-02-01:** Expanding HWM of 3mo MA. The recon showed Feb 2026
   GDP slightly above Jan. March 2026 is very slightly below Feb (-0.001%). This is
   effectively at the high-water mark — one month of noise. The peak designation
   is correct per the methodology; the "current recession" path is 1-2 months long
   and shows essentially zero drawdown, which is accurate.

## Files written

- `data/raw/recession_watch/36100390_sa.csv` + `.meta.json`
- `data/raw/recession_watch/36100398_sa.csv` + `.meta.json`
- `data/raw/recession_watch/lfs_by_industry_sa.csv` + `.meta.json`
- `data/raw/recession_watch/gdp_3digit_naics_sa.csv` + `.meta.json`
- `data/site/panel_data/recession_watch.json`
