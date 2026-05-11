# Chart label-vs-data audit
**Date:** 2026-05-11
**Scope:** Splash sparklines, 44 Tier-3 chartbook panels (originals + 6 V2s), 28 alternatives, two review pages.
**Lens:** Does each chart's title / direct labels / axis units match the data the component actually plots?

Only mismatches are listed. Charts where label and data agree do not appear.

---

## Tier-3 originals (live in production, AUDIT-FLAGGED but still shipping)

### 1. gdp/Panel4PerCapita.astro - BLOCKING
- **Says:** primaryLabel `"Real GDP Y/Y"`, secondaryLabel `"Pop. proxy"`, aria `"Real GDP quarterly and population proxy"`.
- **Plots:** raw quarterly real GDP **level** (CAD millions chained) + immigrant-flow proxy levels. No Y/Y arithmetic happens on the canvas.
- **Severity:** BLOCKING — direct label "Y/Y" is a lie; the line is a level. Reader is materially misled about both the metric and the rate.
- **Fix:** Adopt `Panel4PerCapitaV2.astro` (already shipped) which derives per-capita GDP Y/Y from `gdp_quarterly / pop_total`.

### 2. labour/Panel2PerCapita.astro - BLOCKING
- **Says:** primaryLabel `"Unrate (M)"`, secondaryLabel `"Hours"`, aria `"Unemployment level and aggregate hours"`.
- **Plots:** primary is `unemployment_level` in **millions of persons** (a stock, not a rate). Secondary `aggregate_hours` is suppressed by units guard.
- **Severity:** BLOCKING — "Unrate" reads as "unemployment rate" to any analyst; the value is a level in millions. Confusing alone, and on the Labour section page this panel sits next to Panel 1 which IS the unemployment rate.
- **Fix:** Adopt `Panel2PerCapitaV2.astro` (per-capita employment Y/Y derived from `employment_rate`).

### 3. trade/Panel5TermsOfTrade.astro - BLOCKING
- **Says:** primaryLabel `"WTI"`, secondaryLabel `"Brent"`, aria `"Oil price proxies for terms of trade: WTI and Brent"`.
- **Plots:** the panel-5 pipeline primary is `terms_of_trade` (StatCan ToT index, 2017=100, quarterly). The chart's own line is the ToT index but reader sees "WTI" at the line terminus.
- **Severity:** BLOCKING — the chart labels are completely unrelated to the data. The header docstring (comment) admits "pipeline emits `wti` and `brent`" but pipeline actually emits ToT.
- **Fix:** Adopt `Panel5TermsOfTradeV2.astro` (relabels honestly to "Terms of trade").

### 4. trade/Panel3PartnerShares.astro - MINOR
- **Says:** primaryLabel `"Total exports"`, secondaryLabel `"Exports to US"`, page title `"Partner shares of exports"`.
- **Plots:** both as raw CAD millions level lines.
- **Severity:** MINOR — line labels are technically honest, but the PAGE title promises "partner shares" and no share is computed on the canvas. The reader expecting a share-of-total reading cannot get it from two parallel level lines.
- **Fix:** Adopt `Panel3PartnerSharesV2.astro` (derives US share %).

### 5. gdp/Panel1HeadlineGDP.astro - MINOR
- **Says:** primaryLabel `"Monthly GDP"`, secondaryLabel `"Quarterly GDP"`, page title `"Headline real GDP, monthly + quarterly"`.
- **Plots:** raw level lines, both in CAD trillions chained. Labels technically accurate to the lines.
- **Severity:** MINOR — page title and section headline-question imply a growth-rate read; the chart shows levels. Reader has to infer growth from the slope.
- **Fix:** V2 derives m/m % + Q/Q SAAR. Choice of V1 vs V2 is editorial.

### 6. policy/Panel3BoCFedSpread.astro - MINOR
- **Says:** primaryLabel `"2y Canada"`, secondaryLabel `"2y US"`, panel TITLE on Policy section page is `"BoC-Fed spread"`.
- **Plots:** two raw yield % lines. Labels honest at the line; chart title promises "spread".
- **Severity:** MINOR — line labels match what's drawn, but the panel title says spread and no spread is on canvas. Reader has to eyeball the gap.
- **Fix:** V2 derives the spread in bps.

### 7. gdp/Panel5OutputGap.astro - BLOCKING
- **Says:** primaryLabel `"GDP, quarterly"`, secondaryLabel `"Cap. util."`, aria `"Quarterly real GDP and total capacity utilization"`.
- **Plots:** pipeline primary is now `output_gap_mpr` (BoC MPR output gap, % of potential, quarterly). Secondary is capacity utilization (%). Both render — units match (%).
- **Severity:** BLOCKING — wrapper label is stale from when the primary was a GDP level. The chart now correctly plots the output gap, but the direct label on the line says "GDP, quarterly" which is wrong on two counts (it's not GDP, and the unit is % not a level). Y-axis ticks read as %.
- **Fix:** Rename `primaryLabel` to `"Output gap"`; update aria to "BoC MPR output gap, % of potential, and total capacity utilization." No data swap needed.

### 8. trade/Panel2CurrentAccount.astro - BLOCKING
- **Says:** primaryLabel `"Trade bal."`, page TITLE `"Current account: goods, services, primary income"`, page indicator string `"Current account: goods, services, primary income"`.
- **Plots:** pipeline primary is `trade_balance_total` (monthly merchandise trade balance, CAD millions) — NOT the current account. Secondary `ca_goods_income` is quarterly (cadence mismatch suppresses).
- **Severity:** BLOCKING — section page calls this the Current Account panel and walks the reader through CA components in the interpretation copy; the chart plots the monthly merchandise balance. Two different series. The direct label on the line is honest about what's drawn ("Trade bal.") but the panel title is a lie relative to the data.
- **Fix (two options):**
  - Swap data source: route this panel to the `current_account_total` quarterly series (StatCan 36-10-0014-01) — the canon target.
  - OR rename the panel title to "Goods trade balance, monthly" and route the current-account interpretation to a future Panel 2b. Honest about scope.

---

## V2 panels (just shipped — quick verify)

All six V2s carry honest labels for their derived series. No mismatches found:
- `gdp/Panel1HeadlineGDPV2.astro` — "m/m" / "Q/Q SAAR", both % derived correctly.
- `gdp/Panel4PerCapitaV2.astro` — "Per-cap GDP" %, derived per-capita GDP Y/Y from CSVs.
- `labour/Panel2PerCapitaV2.astro` — "Per-cap emp" %, derived from employment_rate Y/Y.
- `policy/Panel3BoCFedSpreadV2.astro` — "CA-US 2y" bps, spread derivation honest.
- `trade/Panel3PartnerSharesV2.astro` — "US share" %, derivation honest.
- `trade/Panel5TermsOfTradeV2.astro` — "Terms of trade" idx, label finally matches the data.

---

## Alternatives (auto-generated, 28 files reviewed)

### 9. _alternatives/markets/Alt1_GoCUstSpread.astro - MINOR
- **Says (in code):** chart direct label `"GoC2-UST2"`, aria `"GoC 2-year minus US Treasury 2-year"`, unit `"pp"`. All correct to data (`yield_2yr.csv - us_2yr.csv`).
- **Says (in docstring header at line 3):** *"10y GoC minus 10y UST spread"* and *"GoC-UST as a single line"* — and the file is named `GoCUstSpread` (no tenor).
- **Severity:** MINOR — comment-only mismatch. Reader sees the chart label "GoC2-UST2" which is honest. The docstring is misleading to future maintainers and the filename suggests a generic GoC-UST spread when the actual tenor is 2y.
- **Fix:** Update the docstring header to say "2y GoC minus 2y UST" and consider renaming the file to `Alt1_Goc2Ust2Spread.astro`. No reader-facing change.

### 10. _alternatives/gdp/Alt4_GdpVsCapacity.astro - MINOR
- **Says:** primaryLabel `"GDP Y/Y"` (range roughly -5% to +5%), secondaryLabel `"Cap. util."` (range 70%-85%), unit `"%"`.
- **Plots:** both in "%", but they are semantically different — a flow-change vs a level — sharing a single y-axis. The shared axis squashes GDP Y/Y into the bottom decile.
- **Severity:** MINOR — labels accurately describe each line, but the "%" unit suffix masks a unit mismatch (rate-of-change % vs utilization % rate). Reader can be misled into reading them as on the same scale.
- **Fix:** Either split into a small-multiple pair, or replace cap-util with a series the same magnitude as GDP Y/Y. Visual-design call.

### 11. _alternatives/housing/Alt3_MortgageVsHpi.astro - MINOR
- **Same pattern as 10:** "5y mortgage" (level, ~5-7%) and "HPI Y/Y" (change, -5% to +20%) sharing a single % axis. Both labels honest; shared axis crowds them.
- **Severity:** MINOR. Visual-design call, not a label lie.

### 12. _alternatives/housing/Alt4_SnlrVsHpi.astro - MINOR
- **Same pattern:** SNLR level (50-80%) and HPI Y/Y change (% Y/Y) sharing the % axis. Reference line at 60% labeled "Sellers' mkt threshold" — applies only to the SNLR line, but the threshold rule sits across both. Honest labels, mildly confusing geometry.
- **Severity:** MINOR.

---

## Splash sparklines + comparison page descriptions + alternatives page descriptions

No mismatches found. For each section's loadBearing print the indicator string, asOf, units, and spark all agree. The chart-improvements page descriptions accurately characterize each V2 derivation. The chart-alternatives page descriptions accurately summarize each Alt's data fields and visual treatment.

---

## Summary tables

### BLOCKING mismatches (urgent — reader materially misled)

| # | File | Lie | Fix |
|---|---|---|---|
| 1 | `src/components/charts/gdp/Panel4PerCapita.astro` | "Real GDP Y/Y" label on raw level data | Adopt V2 |
| 2 | `src/components/charts/labour/Panel2PerCapita.astro` | "Unrate (M)" label on unemployment level (millions) | Adopt V2 |
| 3 | `src/components/charts/trade/Panel5TermsOfTrade.astro` | "WTI / Brent" labels on terms-of-trade index | Adopt V2 |
| 7 | `src/components/charts/gdp/Panel5OutputGap.astro` | "GDP, quarterly" label on BoC MPR output gap (%) | Rename `primaryLabel` to `"Output gap"`; update aria |
| 8 | `src/components/charts/trade/Panel2CurrentAccount.astro` | Page titled "Current account" plots merchandise trade balance | Swap data to `current_account_total` OR rename panel to "Merchandise balance (monthly)" |

### MINOR mismatches (cleanup queue — ambiguous but not lies)

| # | File | Issue |
|---|---|---|
| 4 | `trade/Panel3PartnerShares.astro` | Page says "partner shares"; chart shows raw level lines |
| 5 | `gdp/Panel1HeadlineGDP.astro` | Page implies growth; chart shows levels |
| 6 | `policy/Panel3BoCFedSpread.astro` | Panel title "BoC-Fed spread"; chart shows two yield lines |
| 9 | `_alternatives/markets/Alt1_GoCUstSpread.astro` | Docstring + filename say "10y" or "generic"; code uses 2y |
| 10 | `_alternatives/gdp/Alt4_GdpVsCapacity.astro` | GDP Y/Y rate-of-change and cap-util level share one "%" axis |
| 11 | `_alternatives/housing/Alt3_MortgageVsHpi.astro` | Mortgage level and HPI Y/Y share one "%" axis |
| 12 | `_alternatives/housing/Alt4_SnlrVsHpi.astro` | SNLR level and HPI Y/Y share one "%" axis; threshold rule applies to one |

---

## Recommendation to user

The five BLOCKING items materially mislead the reader and should fix immediately. Items 1-3 already have V2s on the comparison page — the simplest path is: pick the V2 for each, retire the original, and the chart-improvements review page can be deleted in the same sweep.

Items 7 and 8 are new findings (not in the prior editorial audit). Item 7 is a one-line rename (no V2 needed). Item 8 needs an editorial call between "swap data" and "rename panel."

The MINOR items can wait. Items 4-6 are pending the same V2 decision as 1-3; 9 is comment-only; 10-12 are dual-axis aesthetic concerns the art director can revisit.

**Audit recommendations are proposals.** The chart-builder will only act on items flagged BLOCKING above, and only on the specific items the user does not veto.
