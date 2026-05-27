# Wave 1, Brief 1.4 — Basics-Layer Data Scope: Financial and Trade

Scope: dashboard_purpose.md sections 4.6 (Financial) and 4.7 (Trade), plus
Financial-section absorption of daily "what moved" and weekly cross-asset
synthesis (per editorial-director re-sequencing).

Method: boc-tracker first (`C:\Users\jayzh\Documents\boc-tracker`). Inventory
drawn from `fetch.py` (series registry), `analyze.py` (transforms), `build.py`
(chart routing), and the `data/` CSV cache. Web sourcing proposed only for
gaps.

Canon constraint: basics layer only. Deep dives G (LNG/TMX) and H (US trade
/ USMCA) are out of scope here.

---

## 1. Financial section (canon 4.6 + daily + weekly cross-asset)

### 1.1 Coverage table

Columns: basics element | cadence | boc-tracker coverage | primary source | release timing | gotchas

#### Canon 4.6 elements

| Basics element | Cadence | boc-tracker coverage | Primary source | Release timing | Gotchas |
|---|---|---|---|---|---|
| CAD: USDCAD level | Daily | COVERED (`usdcad.csv`, FRED `DEXCAUS` from 1990; tier classifier `_classify_usdcad` with P50/P80/P95/P99 from monthly 1990+) | FRED `DEXCAUS` (originally NY Fed H.10) | Daily, T+1 NY close | FRED `DEXCAUS` is NY noon buying rate, NOT BoC noon; BoC discontinued its noon rate in 2017 and now publishes indicative daily closes on Valet (`FXUSDCAD`). Switch to BoC Valet `FXUSDCAD` for consistency with BoC charts; CEER methodology change in 2018 |
| CAD: BoC nominal effective index (CEER) | Daily | GAP — placeholder in `build.py:3682` ("Coming soon"); no fetcher | BoC Valet `CEER` series (or component series `FXUSDCAD`, `FXEURCAD`, etc.) | Daily, BoC publication ~16:30 ET | CEER weights revised 2018; six trading partners (US, EU, China, Japan, Mexico, UK). Pre-2017 series uses different basket — splice carefully |
| CAD: deviation from oil-and-rate-differential fair value | Daily (constructed) | GAP — needs own construction; `analyze.py:1077` only classifies USDCAD level against historical distribution, not fair value | Own construction from `usdcad` + `wti` + `can_us_2y_spread` | Daily (derives from above) | Standard 2-factor regression (CAD vs WTI Y/Y and 2y differential) is fragile post-2016; coefficient instability is documented (BoC SDP 2014-9, Bailliu/Dib). Flag uncertainty bands |
| CAD: stress-corridor flag | Daily | PARTIAL — `analyze.py:1143-1144` defines `in_stress_corridor` (1.45 <= USDCAD <= 1.47) and `near_stress_corridor` (1.43-1.49) but corridor levels are hardcoded heuristics, not BoC-published | Own definition (currently hardcoded) | Daily | Hardcoded corridor is not a BoC stress indicator; if we keep it, document it as our construction. BoC's actual financial-stress measure is the Financial Stress Indicator (FSI), published in FSR |
| GoC curve: 2y, 5y, 10y, 30y | Daily | COVERED (`yield_2yr/5yr/10yr/30yr.csv`, BoC Valet `BD.CDN.*.DQ.YLD` from 1990) | BoC Valet | Daily, ~16:30 ET | "Benchmark" series re-anchors to a new on-the-run bond each issuance cycle, creating small jumps; for long-history use, GoC zero-coupon (Valet `BD.CDN.*.GC.YLD`) is cleaner but stops earlier |
| GoC-UST spread: 2y | Daily | COVERED (`analyze.py:607-608, 1334`, `can_us_2y_spread`; built from `yield_2yr.csv` + `us_2yr.csv` FRED `DGS2`) | BoC Valet + FRED `DGS2` | Daily | Time-zone alignment: BoC yields are Canadian close, FRED `DGS2` is NY 3:30 PM ET. One-day stagger possible at month-end |
| GoC-UST spread: 10y | Daily | GAP — `us_10yr` not in fetch.py; only US 2y is fetched | FRED `DGS10` | Daily | Trivial add to FRED fetcher |
| Term premium (where decomposable) | Daily | GAP — footnote in `build.py:3701` directs reader to BoC's Financial Stability Indicators page; no series fetched | BoC FSI (Adrian-Crump-Moench style decomposition) | Daily, BoC publishes | BoC publishes a Canadian term-premium series at the 10y on its Financial Stability Indicators page; Valet series key needs probing. ACM decomposition is model-dependent — cite the BoC methodology note |
| Canadian credit spreads: IG vs US equiv | Weekly | GAP — no credit-spread series in boc-tracker | Bloomberg Barclays / ICE BofA Canada IG OAS (no free source); proxy via ETF (XCB-NAV vs CGB) is constructable; alternatively iBoxx Canada IG from S&P or BoC FSR | Daily/weekly | No free official Canadian IG OAS series. FRED has `BAMLC0A0CM` for US IG OAS — usable for the comparator side. Canadian side needs subscription source or our own construction from BoC corporate yield series. BoC Valet has `BD.CDN.CORP.*` for limited maturity buckets — verify availability |
| Canadian credit spreads: HY vs US equiv | Weekly | GAP — same as above | FRED `BAMLH0A0HYM2` (US HY); Canadian HY: very thin, often cited via ETF spreads | Daily | Canadian HY market is shallow; consider only reporting US HY as the global risk-appetite proxy, with caveat |
| Bank senior unsecured vs GoC | Weekly | GAP — no series | BoC FSR senior unsecured spreads chart (typically the Big-Six average vs 5y GoC); CBID/CanDeal pricing if subscription | Daily (constructed); FSR publishes semi-annually | BoC publishes Big-Six senior unsecured 5y spread quarterly in FSR but not as a downloadable series — needs scraping or proxy via individual bank issuer curves |
| Energy: WTI, Brent | Daily | COVERED (`wti.csv`, `brent.csv`, FRED `DCOILWTICO`, `DCOILBRENTEU` from 1990) | FRED (originally EIA) | Daily, EIA close | None material |
| Energy: WCS with WCS-WTI differential | Monthly (WCS) | PARTIAL — `wcs.csv` from Alberta Economic Dashboard API (`api.economicdata.alberta.ca`), monthly; `analyze.py:1130-1132, 1221-1223` computes `wcs_wti_differential` but flags "DATA CAVEAT: monthly, lagged — do NOT surface WCS-WTI differential in blurb prose" because monthly WCS vs. daily WTI is not directly comparable | Daily WCS: Net Energy / NGX (subscription) or Bloomberg `WTC` ; free daily WCS does not appear in public APIs | Daily WTI / monthly WCS | Public daily WCS is unreliable — the BoC and analysts typically cite the differential off bid-week or monthly settles. If we want a daily differential, we likely need a paid feed (or accept monthly cadence and clearly label it). Alberta dashboard is the cleanest free monthly source |
| Energy: AECO gas | Daily/Weekly | GAP — no series | Alberta Energy Regulator (ST98), or NGX bid-week settles; FRED has Henry Hub (`DHHNGSP`) but no AECO | Daily (NGX) / weekly bid-week | AECO basis to Henry Hub matters more than absolute level for Canadian E&P margins. Free daily AECO is harder than WCS; weekly NGX summary is publicly posted but parsing is fragile |
| Implied gasoline-channel CPI impulse | Weekly synthesis | COVERED (derived) — `analyze.py:1125, 1199` computes `cpi_impulse_wti = wti_yoy_pct * 0.037` using gasoline weight in CPI basket | Own construction from `wti.csv` + StatCan CPI weights | Daily (mechanical) | Hardcoded 0.037 basket weight needs refresh on each StatCan basket update (next: 2026 if on five-year cycle). Mechanical pass-through; ignores retail margin lag and provincial fuel-tax changes |
| Bank stability: Big-Six PCL builds | Quarterly | GAP — no series | Big-Six earnings releases (RBC, TD, BMO, Scotia, CIBC, NBC); OSFI's Financial Data on Banks (M4) publishes balance-sheet items but PCL is in earnings supplements | Quarterly, ~end of Feb/May/Aug/Dec | Manual quarterly capture from earnings releases is the realistic path. OSFI M4 reports loan-loss allowances on the balance sheet, which differs from quarterly PCL flow |
| Bank stability: CET1 vs OSFI DSB | Quarterly | GAP — no series | OSFI Domestic Stability Buffer announcements (typically Jun and Dec); CET1 from Big-Six Pillar 3 disclosures; OSFI Financial Data on Banks | Quarterly (CET1); semi-annual (DSB) | DSB level is policy-set by OSFI Superintendent (currently 3.5% as of late 2023; verify against latest OSFI release); CET1 ratios are individual-bank disclosure. Aggregate Big-Six CET1 needs to be averaged or shown as a range |
| Bank stability: uninsured residential exposure | Quarterly | GAP — no series | OSFI Financial Data on Banks (M4 — residential mortgages by insurance status); CMHC Residential Mortgage Industry Report (semi-annual) | Quarterly (OSFI); semi-annual (CMHC) | OSFI M4 has insured/uninsured split for residential mortgages. Direct fetch is feasible; OSFI provides Excel downloads, not a JSON API — scraping required |
| Financial conditions index: composite | Weekly | GAP — no composite | BoC FCI: BoC publishes a Canadian FCI on the Financial Stability Indicators page; alternative: own construction from CAD, GoC yields, credit spreads, equity. Bloomberg / Goldman / Chicago Fed publish US FCIs as a comparator | Weekly (BoC FCI updated weekly) | BoC's published FCI is the right anchor for the Canada side. Confirm Valet series key. If we construct our own, we own the methodology note |

#### Daily-cadence elements absorbed from "what moved overnight"

| Basics element | Cadence | boc-tracker coverage | Primary source | Release timing | Gotchas |
|---|---|---|---|---|---|
| USDCAD overnight | Daily | COVERED — see above | FRED `DEXCAUS` / BoC `FXUSDCAD` | Daily | (above) |
| Major crosses (EUR/CAD, GBP/CAD, JPY/CAD) | Daily | GAP — only USDCAD in boc-tracker | BoC Valet `FXEURCAD`, `FXGBPCAD`, `FXJPYCAD` | Daily | BoC publishes indicative daily closes for ~25 currencies on Valet since 2017 |
| GoC yields 2y / 5y / 10y / 30y | Daily | COVERED (BoC Valet) | BoC Valet | Daily | (above) |
| TSX Composite level/return | Daily | GAP — no series | TMX Group (free EOD via Yahoo `^GSPTSE`); S&P/TSX official is paid | Daily | Public Yahoo feed acceptable for blurb-grade EOD; if archival/reproducibility matters we should switch to a documented source. Total-return vs price-return distinction — TSXR (total return) better for cross-asset comparison |
| S&P 500, Nasdaq comparator | Daily | GAP — no series | FRED `SP500` (S&P 500 close, last 10y only), `NASDAQCOM` | Daily | FRED's `SP500` is restricted to last 10 years per S&P Dow Jones licensing; for deeper history use Yahoo `^GSPC` (price), `^IXIC` |
| WTI / WCS overnight | Daily / monthly | COVERED (WTI); PARTIAL (WCS monthly) — see above | FRED `DCOILWTICO`; Alberta Dashboard | Daily / monthly | (above) |
| Key credit spreads | Daily | GAP — see above | (above) | Daily | (above) |

#### Weekly-cadence cross-asset regime synthesis

These are constructed weekly from underlying daily inputs.

| Basics element | Cadence | boc-tracker coverage | Primary source / construction | Release timing | Gotchas |
|---|---|---|---|---|---|
| Rolling stock-bond correlation (TSX or S&P 500 vs 10y) | Weekly | GAP — no TSX or S&P 500 series; correlation not constructed | Own construction from daily price + yield; standard window 60d or 90d | Weekly | Sign and magnitude regime-dependent: positive correlation = "inflation regime" (both fall together on inflation surprises); negative = "growth regime" (classic diversification). Window choice matters — show 60d and 250d together |
| DXY vs risk (TSX / S&P 500) | Weekly | GAP — no DXY; no TSX/S&P 500 | DXY: ICE futures; proxy via FRED `DTWEXBGS` (broad trade-weighted USD) | Daily / weekly | DXY proper is the ICE DXY index (6-currency basket, EUR-heavy); FRED `DTWEXBGS` is Fed broad TWI — different basket, similar story. For a Canadian publication, `DTWEXBGS` is arguably better than DXY (more representative of Canada's trading-partner FX). BIS publishes nominal effective exchange rates too |
| Gold vs 10y real yield | Weekly | GAP — no gold; no real yield | Gold: FRED `GOLDAMGBD228NLBM` (LBMA AM); 10y real: FRED `DFII10` (TIPS) for US, or BoC's RRB-derived real-yield series for Canada | Daily | Canada equivalent of `DFII10` is the Real-Return Bond (RRB) yield, available on BoC Valet (`BD.CDN.RRB.DQ.YLD` or similar); RRB program was discontinued for new issuance in 2022 budget so long-end real-yield data has structural break risk |
| Credit spreads vs VIX (or equivalent) | Weekly | GAP — no VIX, no credit spreads | VIX: FRED `VIXCLS`; credit spreads see above | Daily | VIX is US-only — Canada has no liquid equivalent index. For Canadian financial-conditions synthesis, US VIX is the standard proxy |
| Term structure shape (2s10s, 2s30s, 3m-10y) | Weekly | PARTIAL — `yield_10y_2y_spread` is constructed (`build.py:3736`, derived series); 2s30s and 3m-10y not | Own construction from existing yield series; 3m T-bill from BoC Valet `V80691340` or `B113875` | Daily | 3m T-bill series needs to be added to fetcher. 2s30s diverged from 2s10s through the recent cycle (long-end term premium); both worth tracking |

### 1.2 Financial gap list (priority-ordered)

1. CEER / trade-weighted CAD — fetcher only, BoC Valet (placeholder already exists in build.py)
2. US 10y Treasury — trivial FRED addition (`DGS10`)
3. TSX Composite (Yahoo `^GSPTSE` or licensed source) and S&P 500 (Yahoo `^GSPC`)
4. BoC term-premium series — Valet key probe needed; verify via BoC Financial Stability Indicators page
5. BoC Financial Conditions Index — Valet key probe needed; same page
6. Major FX crosses (EUR/CAD, GBP/CAD, JPY/CAD) — BoC Valet
7. Gold (FRED `GOLDAMGBD228NLBM`), VIX (FRED `VIXCLS`), broad trade-weighted USD (FRED `DTWEXBGS`)
8. Credit spreads — Canadian IG/HY/bank senior unsecured: hard. Likely accept US-only on first pass (FRED `BAMLC0A0CM`, `BAMLH0A0HYM2`) with explicit caveat about Canadian-spread blind spot. Canadian senior unsecured needs FSR scraping
9. Bank stability — Big-Six PCL, CET1, uninsured exposure: quarterly manual capture from earnings + OSFI M4 scrape; not free-API data
10. AECO natural gas — Alberta Energy Regulator ST98 or NGX bid-week; weekly cadence acceptable
11. Real yield (RRB-derived for Canada, FRED `DFII10` for US comparator)
12. 3-month T-bill yield — BoC Valet
13. Daily WCS — if achievable; otherwise hold the monthly WCS series with the existing "do not surface daily-comparison differential" caveat

### 1.3 Financial construction watchlist (we must build, not fetch)

1. CAD fair-value model (USDCAD vs WTI Y/Y and 2y differential, rolling-window regression). Methodology note required; cite Bailliu/Dib if used. Show confidence band, not point estimate.
2. CAD stress corridor — boc-tracker hardcodes 1.45-1.47; if retained, must be re-documented as our heuristic, not a BoC indicator. Alternative: switch to USDCAD percentile classifier already in `analyze.py:1077` (P95/P99 bands from 1990+) — that is empirical and defensible.
3. Rolling stock-bond correlation (TSX vs 10y GoC) at 60d and 250d windows. Cross-window divergence is itself the signal.
4. Bank senior unsecured spread proxy — if we cannot get BoC's FSR series directly, build a Big-Six average from individual issuer 5y yields vs 5y GoC. Methodology note.
5. Financial conditions composite — only if BoC's published FCI is unavailable. If we build it, we own all weighting decisions; document.
6. Gasoline-channel CPI impulse — already in `analyze.py:1125`; refresh weight on next CPI basket update (2026 cycle).
7. Term-structure shape panel (2s10s, 2s30s, 3m-10y) — straightforward arithmetic on yield series.
8. Cross-asset regime classifier (stock-bond correlation sign + DXY direction + credit spread level) — weekly synthesis output.

---

## 2. Trade section (canon 4.7)

### 2.1 Coverage table

| Basics element | Cadence | boc-tracker coverage | Primary source | Release timing | Gotchas |
|---|---|---|---|---|---|
| Merchandise trade balance (headline) | Monthly | COVERED — `trade_balance_total.csv` (StatCan vector 87008984, Table 12-10-0119-01, BOP basis, SA, C$ millions); displayed in C$ billions via derived `trade_balance_total_b` | StatCan WDS Table 12-10-0119-01 | Monthly, ~35-day lag (early in following month after next) | Customs basis vs BOP basis: boc-tracker uses BOP for balance and Customs for exports/imports — they differ by valuation, coverage (e.g. ships and aircraft), and timing adjustments. StatCan's published headline is BOP; balance and component sums won't tie exactly. Non-monetary gold flagged in `build.py:2924` as a known headline-distorter — strip out for cleaner read |
| Merchandise: exports / imports total | Monthly | COVERED — `trade_exports_total.csv` (v87008897), `trade_imports_total.csv` (v87008781); same table | StatCan WDS Table 12-10-0119-01 | Monthly | Customs basis here; see above |
| Three-month moving average | Monthly | GAP — not constructed in `analyze.py`; build.py only renders raw series | Own construction from `trade_balance_total` | Monthly | Trivial; standard noise-suppression for monthly trade data |
| Decomposition by major category (energy, autos, metals, ag, forestry, consumer goods, machinery) | Monthly | GAP — boc-tracker has only the total and US-bilateral totals; no category breakdown | StatCan WDS Table 12-10-0121-01 (exports by product, SA) and 12-10-0122-01 (imports by product, SA); or Table 12-10-0011-01 (annual) | Monthly | Product categories are HS-section-level in 12-10-0121; ~12 categories. Per-category vector IDs need probing via WDS getSeriesInfoFromVector. Energy export decomposition (crude, refined, gas, electricity) is in Table 25-10-0044-01 |
| Current account (quarterly) | Quarterly | GAP — no series; boc-tracker is merchandise-only | StatCan WDS Table 36-10-0014-01 (CA, SA, by component) | Quarterly, ~60-day lag | Goods, services, primary income, secondary income — each as its own vector. Watch the income account; primary income reflects investment-income flows, often misread as "trade" |
| By-major-partner shares (US dominance) | Monthly | PARTIAL — US is the only partner broken out (`trade_exports_us`, `trade_imports_us`, `trade_balance_us`); no EU / China / UK / Mexico / Japan | StatCan WDS Table 12-10-0011-01 or 12-10-0119-01 (all countries available, by country code) | Monthly | Need to fetch additional vectors per country; structurally the same as the US fetch. Top 5 partners after US: China, UK, Japan, Mexico, Germany |
| Terms of trade | Quarterly | GAP — `build.py:2927` flags as "[Coming soon]" | StatCan Table 36-10-0103-01 (terms of trade index, SA) or derived from export/import price deflators in 36-10-0104 | Quarterly | StatCan publishes ToT in the National Accounts. Distinct from BoC commodity price index (BCPI) — ToT covers all merchandise + services, BCPI is commodity-only |
| BoC commodity price index (BCPI) | Daily | GAP — no series | BoC Valet — series keys `BCPI`, `BCNE` (non-energy), and sub-indices | Daily (BoC publishes daily real-time-ish) | BCPI was redesigned in 2022 with revised weights; pre-2022 series uses old weights. Confirm whether Valet returns the spliced or original series. Useful as a higher-frequency commodity-export proxy than ToT |
| Oil-and-gas component of exports | Monthly | PARTIAL — `wti` and `wcs` are price proxies covered (Financial section); export volumes/values not in boc-tracker | StatCan Table 25-10-0044-01 (energy supply and disposition); CER (Canada Energy Regulator) for crude-by-mode (pipeline/rail/marine); 12-10-0121 for energy in trade by product | Monthly | Energy is the largest single export category — material to headline. CER publishes pipeline throughput including TMX. For basics layer, an aggregate "energy exports, C$" line is enough; mode-split is deep-dive G territory |
| CAD trade-weighted (if not in Financial) | Daily | GAP — same as CEER in Financial. Owned in Financial, not duplicated here | BoC Valet `CEER` | Daily | Cross-reference from Financial; do not duplicate the series in Trade |
| FDI inflows / outflows by sector | Quarterly | GAP — no series | StatCan Table 36-10-0008-01 (FDI flows by industry); BoC Valet has aggregate BOP financial-account series | Quarterly, ~75-day lag | FDI is the most volatile component; sector-level adds signal but data is sparse. M&A-deal-driven spikes (e.g., Suncor / energy assets, telecoms) distort quarterly reads — flag known one-offs |
| Tariff state (canon 4.7 #5) | Event | OUT OF SCOPE for this brief (canon flags deep dive H absorbing live tariff actions). Basics-layer tariff state: simple structured table of in-force US 232/301 actions on Canadian goods | USTR proclamation register; CBSA tariff classifications; DoF retaliatory-tariff notices | Event | Not a numeric series — a maintained reference table. Out of scope per brief instruction (deep dive H out of scope) but flagging that even the basics-layer "tariff state" element is editorial/reference, not data-pipeline content |

### 2.2 Trade gap list (priority-ordered)

1. Trade-balance 3-month moving average — trivial pandas rolling on existing series
2. Current account components — StatCan Table 36-10-0014-01 (goods, services, primary income, secondary income); 4 quarterly vectors to add
3. By-partner breakdown beyond US — add at minimum China, UK, Japan, Mexico, Germany (same table 12-10-0119-01, different country codes)
4. Trade by major product category — StatCan Table 12-10-0121-01 (exports by product) and 12-10-0122-01 (imports by product); ~12 vectors each at HS-section level
5. Terms of trade — StatCan Table 36-10-0103-01 (or derived from 36-10-0104 deflators); quarterly
6. BoC commodity price index (BCPI) and BCNE — BoC Valet
7. Energy exports value/volume — StatCan Table 25-10-0044-01 plus 12-10-0121 energy line
8. FDI by sector — StatCan Table 36-10-0008-01
9. Tariff state reference table — editorial-maintained, not a data series (out of scope this brief but flagged)

### 2.3 Trade construction watchlist

1. Trade-balance 3M moving average + Y/Y comparison.
2. Non-monetary-gold-stripped trade balance — `build.py:2924` already flags this as a goal; we need StatCan's gold series (Table 12-10-0121 line for non-monetary gold) and subtract. Cleaner momentum read.
3. Partner-share rolling — US share of total exports / imports as a percentage trajectory; the structural-shift narrative.
4. Goods vs services current-account split — once 36-10-0014 is wired, the services balance trend is a separate story.
5. Energy export concentration — share of energy in total goods exports, ratio to non-energy.
6. ToT regime classifier — improvement/deterioration vs trailing 5y distribution; BCPI as the high-frequency leading line into ToT.
7. FDI net flow by sector — inflows minus outflows; flag M&A one-offs in methodology note.

---

## 3. Coverage summary

**Financial section.** Counting canon 4.6 (6 elements) + daily what-moved (6 elements) + weekly synthesis (5 elements) = 17 basics elements.

- Fully covered: 5 (USDCAD level, GoC curve 2y/5y/10y/30y, GoC-UST 2y, WTI/Brent, gasoline CPI impulse)
- Partial: 3 (CAD stress corridor [hardcoded heuristic], WCS [monthly only], term structure shape [only 2s10s constructed])
- Gap: 9 (CEER, term premium, US 10y, credit spreads, bank stability, FCI, equities, gold, VIX, real yield, major crosses, AECO, fair-value CAD)

Coverage ratio: roughly **30 percent** fully covered, **18 percent** partial, **53 percent** gap. The boc-tracker Financial deep dive was always thin — its strengths are the CAD/oil/yield-curve triangle; bank stability, credit, and equity comparators are all greenfield.

**Trade section.** Counting canon 4.7 (6 elements, treating tariff state as out-of-scope reference). The 6 elements are: merchandise balance, current account, energy exports, auto/metals cross-border, tariff state, ToT/FDI.

- Fully covered: 1 (merchandise trade balance + US bilateral aggregate)
- Partial: 1 (energy exports — prices yes, volumes/values no)
- Gap: 4 (current account, by-product / by-partner-beyond-US, ToT and BCPI, FDI; auto/metals specifically not in boc-tracker; tariff state is editorial reference, out of scope here)

Coverage ratio: roughly **17 percent** fully covered, **17 percent** partial, **67 percent** gap. boc-tracker carried only the StatCan headline merchandise trade table (12-10-0119-01) and the US-bilateral cut. All other Trade basics need new fetchers.

---

## 4. Cadence implications for the pipeline (hand-off to backend-engineer)

The Financial section as scoped in this brief carries a **daily refresh requirement** that is materially higher-frequency than the publication's other sections. The daily "what moved" elements (CAD crosses, GoC yields, TSX, S&P 500, oil) and the weekly cross-asset synthesis (rolling correlations, DXY, gold, VIX, term structure) both depend on daily-frequency upstream feeds. Practically: the backend pipeline must run a Financial-specific daily fetcher (or a daily run of the full fetcher) on every trading day — not just on the cadence of monthly StatCan releases. boc-tracker's existing `fetch.py` already does this in a single batch run that includes daily series (BoC Valet yields, FRED daily series like `DEXCAUS`, `DCOILWTICO`, `DGS2`), so the **daily-cadence requirement is essentially free if backend lifts the boc-tracker fetcher pattern wholesale**. Two concrete additions: (a) the fetcher must be scheduled to run every North American trading day post-close (suggested: 18:00 ET to capture BoC's ~16:30 ET Valet publication and FRED's late-afternoon updates); (b) the Financial-section build downstream must be able to render on a daily cadence independent of the monthly StatCan-driven sections, which implies decoupling Financial-section page generation from the rest of the build (a separate `build_financial.py` target, or a Financial-section flag in the existing build). Weekly-synthesis elements (rolling correlations, DXY-risk regime read, gold-real-yield, credit-spreads-vs-VIX) are constructed from the same daily inputs but only need to publish once a week — these are downstream of the daily fetch, not a separate pipeline. **The single most useful thing backend can do is preserve boc-tracker's `_safe()` per-series error isolation pattern** (`fetch.py:484-494`): a single daily-series fetch failure must not block the rest of the pipeline, because daily fetches have far more opportunities to fail (FRED outages, BoC Valet schema changes, Yahoo for TSX) than monthly StatCan fetches do.

---

## 5. Verification provenance for this brief

- boc-tracker series registry: `C:\Users\jayzh\Documents\boc-tracker\fetch.py` (lines 46-194 for series definitions)
- boc-tracker analyses for Financial: `C:\Users\jayzh\Documents\boc-tracker\analyze.py` lines 575-674 (yields, BoC-Fed and Can-US spreads, tier classifiers); lines 1077-1240 (CAD, oil, USDCAD tier, stress corridor)
- boc-tracker Financial deep-dive page spec: `C:\Users\jayzh\Documents\boc-tracker\build.py` lines 3659-3743
- boc-tracker Trade deep-dive page spec: `C:\Users\jayzh\Documents\boc-tracker\build.py` lines 3745-3792 and 2900-2950 (V2 spec)
- boc-tracker data cache (verified file inventory): `C:\Users\jayzh\Documents\boc-tracker\data\` — 100+ CSVs, of which the Financial-relevant ones are `usdcad.csv`, `wti.csv`, `brent.csv`, `wcs.csv`, `yield_{2,5,10,30}yr.csv`, `us_2yr.csv`, `overnight_rate.csv`, `overnight_rate_daily.csv`, `corra_daily.csv`; and Trade-relevant ones are `trade_balance_total.csv`, `trade_exports_total.csv`, `trade_imports_total.csv`, `trade_balance_us.csv`, `trade_exports_us.csv`, `trade_imports_us.csv`
- Canon: `C:\Users\jayzh\projects\macro-research-department\editorial\dashboard_purpose.md` sections 4.6, 4.7, 6 (cadence table)

End of brief.
