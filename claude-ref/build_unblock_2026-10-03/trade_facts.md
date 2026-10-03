# Trade section fact pack -- build unblock 2026-10-03

Prepared 2026-10-03 (fetches 17:05-17:12 UTC). For the writer redrafting the
`slug: "trade"` block in `src/data/sections.ts` (tileLine + blurb body) and the
four plates in `src/pages/trade.astro`. Primary sources only: Statistics Canada
(The Daily + Web Data Service), White House, Department of Finance Canada, Bank
of Canada, and the repo pipeline files (refreshed 2026-10-03T17:01-17:03Z per
their `.meta.json`). Nothing under `src/` was edited. Nothing committed.

Format of each fact: value | period | source | suggested `source:` string.

READ SECTION 0 FIRST. Three structural problems change what the writer can say.

---

## 0. Things the writer must know before drafting

- W1. THE PIPELINE EXPORT SERIES ARE CUSTOMS-BASIS, NOT THE HEADLINE BASIS.
  `trade_exports_total` (v87008897) and `trade_exports_us` (v87008898) are
  labelled in the catalog as "BOP SA, Table 12-10-0119-01". The Web Data
  Service says otherwise (queried today): both are in Table 12-10-0011-01 and
  are "Export; Customs; Seasonally adjusted". The balance series (v87008984,
  v87008985) ARE balance-of-payments, seasonally adjusted. Consequence:
  - Pipeline values match the Web Data Service exactly (no data error).
  - But export LEVELS and the US SHARE on the page differ from the Statistics
    Canada headline: July exports C$73.4B on the page basis vs $76.1B headline;
    US share 66.6% on the page basis vs 66.3% headline (100 - 33.7).
  - The balance ($769M) is the headline number and matches exactly.
  - Never put a pipeline export level next to a headline balance or a Daily
    percentage in one sentence without saying which basis. Simplest rule: use
    pipeline (customs-basis) numbers for anything the charts show, and use the
    Daily cards only for month-over-month percentages and "record" statements.
  - The correct table for the citation string is 12-10-0011-01. The existing
    strings (`pipeline:statcan:12-10-0119-01`, `pipeline:statcan:12-10-0121-01`)
    point at tables these vectors are not in. Suggested strings below use
    `pipeline:statcan:12-10-0011-01`. The gate accepts any table id
    (scripts/source_audit.mjs builds the link from it), so this is safe.

- W2. TWO OF THE FOUR CHARTS DID NOT MOVE WITH TODAY'S REFRESH.
  - Plate 02 (scatter) reads `data/processed/sectoral_exports_latest_yoy.csv`,
    last fetched 2026-07-07, window May 2025 -> May 2026. It still shows May.
  - Plate 04 (slopegraph, `PanelSectorPivot.astro`) hardcodes "2025-05" and
    "2026-05" (lines 123-126) and the column headers "MAY 2025 / MAY 2026".
    It reads refreshed CSVs, so it now draws REVISED May values (see 2.4).
  - Plates 01 and 03 do follow the data through July 2026.
  So prose for plates 02 and 04 must either describe May-to-May (what the chart
  shows) or wait for a chart/pipeline fix. July-to-July facts for plate 04 are
  in 2.4 so the decision can be made with eyes open. I did not run the
  pipeline and did not touch the components.

- W3. `data/derived/tariff_state.json` IS WRONG AND STALE (as_of 2026-04-06).
  See section 4. Do not write tariff prose from it.

---

## 1. Vintage: what is in the data

- F1.1 Slot carrying 2026-09-01: ONLY `panel-9` extras -> `gold_price_monthly`
  (COMEX gold futures, month-end close keyed to first of month; Yahoo Finance
  GC=F). Value 4,348.0 USD/oz for September 2026.
  | data/site/panel_data/trade.json, panel-9 extras[0], asOfISO 2026-09-01
  This single market-price slot is what trips the 35-day gate. Every Statistics
  Canada slot on the page is as of 2026-07-01.

- F1.2 Latest as-of by slot in `data/site/panel_data/trade.json`:
  - panel-3 (plate 01): trade_exports_total 2026-07-01; trade_exports_us 2026-07-01 (releaseDate 2026-09-03)
  - panel-8 (passed to plate 02): all 34 customs-basis bilateral series 2026-07-01 (releaseDate 2026-09-03)
  - panel-9 (plate 03): exports_gold_total / _uk / _us 2026-07-01; gold_price_monthly 2026-09-01
  - panel-7-alt (plate 04): steel/aluminum/copper/softwood/autos US and non-US, all 2026-07-01
  - Off-panel inputs: data/raw/trade_balance_total.csv 2026-07-01 (plate 01 left
    panel reads it directly); sectoral_exports_latest_yoy.csv window ends 2026-05 (STALE, see W2).
  - sections.json prints: trade balance Jul 2026; US export share Jul 2026;
    current account 2026Q2; terms of trade 2026Q2.

- F1.3 Latest release: "Canadian international merchandise trade, July 2026",
  released 2026-09-03.
  | https://www150.statcan.gc.ca/n1/daily-quotidien/260903/dq260903a-eng.htm
  Next: "Data on Canadian international merchandise trade for August are
  scheduled to be released on October 6." (verbatim, same page). The redraft
  will be one release old within three days.

- F1.4 Headline figures, The Daily (balance-of-payments basis, seasonally adjusted) vs pipeline:

  | Item | The Daily, July 2026 | Pipeline | Match |
  |---|---|---|---|
  | Goods trade balance | $769 million (June $4.2B) | 769.2 (June 4,201.4) v87008984 | YES |
  | Exports | $76.1B, -2.3% m/m | 73,448.0, -4.1% m/m (customs basis) | NO - basis (W1) |
  | Imports | $75.4B, +2.2% m/m | not on this page | n/a |
  | Exports to US | $50.5B (50,517), -6.6% m/m | 48,895.5, -6.5% m/m (customs basis) | NO - basis (W1) |
  | Imports from US | $44.6B (44,604), +1.8% m/m | not on this page (SA) | n/a |
  | Balance with US | $5.9B (June $10.3B) | 5,913.1 (June 10,276.4) v87008985 | YES |
  | Exports to non-US | record $25.6B, +7.4% m/m | 24,552.5, +1.0% m/m (customs basis) | NO - basis (W1) |
  | Non-US share of exports | 33.7% (so US 66.3%) | US 66.57% (customs basis) | NO - basis (W1) |
  | Balance with non-US | -$5.1B (June -$6.1B) | 769.2 - 5,913.1 = -5,143.9 | YES |

  Headline exports/imports verified a second way from the Web Data Service
  (Table 12-10-0011-01, balance-of-payments SA, release 2026-09-03): exports
  all countries 76,137.4 (v87008955), exports to US 50,517.1 (v87008956),
  imports all countries 75,368.2, imports from US 44,604.0.
  Revisions stated in the Daily: June exports revised from $77.5B to $78.0B;
  June imports from $73.6B to $73.8B.

---

## 2. Current values for every existing claim

### 2.1 Tile line and abstract (sections.ts)

- F2.1 Goods trade balance: +C$769.2M | July 2026 | data/raw/trade_balance_total.csv (v87008984)
  | `pipeline:statcan:12-10-0011-01`
  Prior months, current vintage: Mar +1,343.6; Apr +3,348.4; May +3,669.0; Jun +4,201.4.
  Change Jun -> Jul: 769.2 - 4,201.4 = -3,432.2 (narrowed by C$3.4B).
  Fifth straight monthly surplus (Mar-Jul); Daily verbatim: "This was the fifth
  consecutive monthly trade surplus."
  Existing claim "Goods surplus widened to $4.2B in May": OUTDATED and the May
  number itself has been REVISED to $3.7B (3,669.0). $4.2B is now June's value.
  "surplus widened again in May" (abstract): outdated; the latest move is a
  narrowing.

- F2.2 US share of goods exports (page basis, customs SA): 66.57% | July 2026
  | 48,895.5 / 73,448.0 | data/raw/trade_exports_us.csv, trade_exports_total.csv
  | `pipeline:statcan:12-10-0011-01`
  Recent path, current vintage: Mar 65.98; Apr 68.84; May 69.72; Jun 68.26; Jul 66.57.
  Month change: 66.57 - 68.26 = -1.69 pts. Year change: Jul 2025 = 45,404.1 /
  62,211.1 = 72.98%; 66.57 - 72.98 = -6.41 pts.
  July 2026 is the second-lowest reading in the pipeline series (starts Jan
  1997, 355 months); the lowest is March 2026 (65.98%).
  Headline basis for comparison: Jul 2026 66.35% (50,517.1/76,137.4); Jun 69.39%;
  May 69.35%; Jul 2025 72.64% (45,423.9/62,531.5); May 2025 68.46%.
  Existing claims:
  - "US export share rebounded to 70.0%" / "back at 70.0%": NOW FALSE. Latest is
    66.6%. May itself revised to 69.7%.
  - "looks little changed from a year ago": NOW FALSE. July is 6.4 points below
    July 2025 (6.3 on the headline basis).

- F2.3 Gold to London (abstract "gold routed to London", "that flow is cooling"):
  see 2.3. "Cooling" is NOW FALSE as written: total precious-metals exports hit
  a series high in June (C$8.6B) and UK-bound shipments rose in both June and July.

- F2.4 Aluminum / copper sentence in the abstract: see 2.4. True on the chart's
  May-to-May window, false on July-to-July.

### 2.2 Plate 01 -- balance and US share

Title "The US export share is back near 70%." -- NOW FALSE (66.6%).

- F2.5 "66.0% in March": STILL TRUE (65.98%).
- F2.6 "69.2% in April": REVISED to 68.8% (50,140.4 / 72,831.5 = 68.84%).
- F2.7 "70.0% in May": REVISED to 69.7% (52,217.7 / 74,900.6 = 69.72%).
- F2.8 "close to where it was a year earlier" (May 2025 note says 69.6%): May
  2025 is now 68.86% (42,248.9 / 61,355.1). OUTDATED in any case; the live
  comparison is July vs July, -6.4 pts.
- F2.9 Callout "70.0% / +0.8pp m/m": now 66.6% / -1.7 pts m/m (July 2026).
  The sections.json print agrees: "66.6%", "-1.7 pp", "Jul 2026".
- F2.10 "shipments to London surged, then cooled" (note: UK-bound C$7.8B Mar ->
  C$5.6B Apr -> C$4.6B May): current vintage Mar 7,818.6; Apr 5,565.0; May
  4,716.0 (revised up from 4.6B); Jun 5,748.5; Jul 5,939.0. OUTDATED: shipments
  to the UK have risen two months running since May.
- F2.11 Exports to US (page basis): C$48.9B (48,895.5) | July 2026 | -6.5% m/m
  (48,895.5 / 52,279.6). Exports to non-US (page basis): C$24.6B (24,552.5),
  the highest in the pipeline series; +1.0% m/m; +46.1% vs Jul 2025 (16,807.0).
  | `pipeline:statcan:12-10-0011-01`
  Headline-basis equivalents need cards (see section 5):
  `card:claim_statcan_cimt_jul2026_nonus_exports_record`,
  `card:claim_statcan_cimt_jul2026_nonus_export_share` (both PENDING).
- F2.12 Source line on the plate says "12-10-0121-01 (exports by country)". The
  export vectors are in 12-10-0011-01. Factual error in the source line.

### 2.3 Plate 03 -- gold (and the gold claims in plate 02)

Series: NAPCS 35, unwrought gold, silver and platinum-group metals, customs
basis, not seasonally adjusted, Table 12-10-0182-01.
| data/processed/exports_gold_total.csv (v1863625573), exports_gold_uk.csv
(v1863625693), exports_gold_us.csv (v1863625603) | `pipeline:statcan:12-10-0182-01`

| Month | Total C$M | To UK C$M | UK share | To US C$M |
|---|---|---|---|---|
| Jul 2025 | 4,413.4 | 2,533.8 | 57.4% | 1,726.4 |
| Mar 2026 | 8,026.3 | 7,818.6 | 97.4% | 157.3 |
| Apr 2026 | 6,080.0 | 5,565.0 | 91.5% | 301.1 |
| May 2026 | 5,875.0 | 4,716.0 | 80.3% | 737.0 |
| Jun 2026 | 8,577.0 | 5,748.5 | 67.0% | 891.0 |
| Jul 2026 | 6,819.5 | 5,939.0 | 87.1% | 529.3 |

- F2.13 Total, July 2026: C$6.8B, down 20.5% from June (6,819.5 / 8,577.0), up
  54.5% from July 2025. June 2026 (C$8.6B) is the highest month in the pipeline
  series, above March (C$8.0B).
- F2.14 UK share, July 2026: 87.1% (5,939.0 / 6,819.5). | `derived`
- F2.15 June's jump was not London: UK took 67.0%; C$1.9B went to destinations
  other than the UK and US (8,577.0 - 5,748.5 - 891.0 = 1,937.5). The pipeline
  does not say which countries. UNVERIFIED destination; do not name one.
- Existing claims:
  - "C$5.6 billion of precious metals in May": REVISED to C$5.9B (5,875.0).
  - "down from C$8.0 billion in March": March still 8,026.3. TRUE but outdated.
  - "UK's share fell to 83% from 97%": May revised to 80.3%; latest (July) 87.1%.
    Callout "83% / May 2026" is OUTDATED AND REVISED -> "87%" / "July 2026".
  - Title "London is still buying most of Canada's gold" TRUE (87%); "but the
    surge is cooling" NOW FALSE on the page's own series: June is the series
    high and July (C$6.8B) is the third-highest month in the series, behind
    only June 2026 and March 2026.
  - The two `derived` history citations (Ontario/Quebec mining; London bullion
    banks / Bank of England vaults) are not data claims and were not re-verified
    in this pass. They cite no card. If kept, they carry over unverified by me.
- F2.16 Statistics Canada's own read (headline basis, SA), The Daily verbatim:
  "Lower exports of unwrought gold, silver, and platinum group metals, and
  their alloys (-13.1%) were behind the decline in July, mainly because of
  lower purchases of Canadian-held gold by foreign residents, as well as fewer
  shipments destined for the United States." and "Since the peak observed in
  February 2026, export prices of unwrought gold, silver, and platinum group
  metals, and their alloys have decreased 9.0%."
  (The page renders "-13.1%" with spaces inside the number; no card created.)
  Headline-basis levels from the Web Data Service, Table 12-10-0163-01,
  v1566911383: Mar 10,893.9 (record); Jun 10,071.1; Jul 8,752.1.
- F2.17 Gold price (chart overlay): 4,348.0 USD/oz end-Sep 2026; 4,431.1 end-Aug;
  4,049.1 end-Jul; 4,560.5 end-May; peak 5,230.5 end-Feb 2026. Sep vs Feb:
  -16.9%. | data/processed/gold_price_monthly.csv (COMEX front-month futures via
  Yahoo; a market feed, not a government source) | no existing citation string
  for this series in the trade arrays; avoid quoting it in prose.

### 2.4 Plate 04 -- tariff-exposed sectors (US share of sector exports)

Customs basis, not seasonally adjusted, small monthly values: noisy.
| data/processed/exports_<sector>_us.csv and _nonus.csv | `derived` (note should
name StatCan 12-10-0182-01, as the existing notes do)

| Sector | May 2025 | May 2026 | Change | Jul 2025 | Jul 2026 | Change |
|---|---|---|---|---|---|---|
| Aluminum | 88.69% | 62.94% | -25.75 | 90.06% | 81.52% | -8.54 |
| Copper | 87.44% | 90.65% | +3.21 | 93.14% | 84.51% | -8.63 |
| Steel | 90.94% | 87.04% | -3.90 | 89.76% | 84.02% | -5.74 |
| Autos + parts | 90.74% | 88.32% | -2.42 | 89.46% | 88.12% | -1.34 |
| Softwood | 88.78% | 88.13% | -0.65 | 89.17% | 89.43% | +0.26 |

Underlying C$M (US / non-US): aluminum May-26 912.5 / 537.3, Jun-26 937.1 /
225.1, Jul-26 1,017.9 / 230.7; copper Jul-26 283.3 / 52.0; steel Jul-26 472.4 /
89.8; autos Jul-26 4,811.2 / 648.6; softwood Jul-26 994.3 / 117.6.

- F2.18 On the chart's window (May to May, which is what the chart still
  draws): "aluminum is the only clear move away" STILL TRUE; "88.7% to 62.9%"
  STILL TRUE; "steel, softwood, and autos each moved away by less than five
  points" STILL TRUE but the cited numbers were REVISED (steel 90.9 -> 87.0,
  not 91.1 -> 87.0; softwood 88.8 -> 88.1; autos 90.7 -> 88.3); "copper moved
  further toward the US" STILL TRUE but REVISED (87.4 -> 90.7, not 88.9 -> 90.6).
- F2.19 On the latest data (July to July): "aluminum is the only clear move
  away" is NOW FALSE. Copper (-8.6), aluminum (-8.5) and steel (-5.7) all moved
  away; "copper moved further toward the US" is NOW FALSE; "steel ... less than
  five points" is NOW FALSE (-5.7). Softwood is flat-to-up, autos -1.3.
- F2.20 OBSERVATION: aluminum's 62.9% in May 2026 was a one-month spike in
  non-US shipments (C$537M vs C$129M in April and C$225M in June); the share was
  back to 80.6% in June and 81.5% in July. INTERPRETATION (mine): the old
  plate's headline number was a single-month outlier, not a level shift. The
  durable aluminum move is roughly 8-9 points, not 26.

### 2.5 Plate 02 -- sector scatter

- F2.21 "total precious-metals exports fell from C$8.0B in March to C$5.6B in
  May": May REVISED to C$5.9B; OUTDATED (June C$8.6B, July C$6.8B).
- F2.22 "the surge is fading": NOW FALSE (see F2.13).
- F2.23 "exports to the US rose to C$52.2B, a new high in the refreshed data":
  May (52,217.7) is unchanged. But "a new high" was not true on the pipeline
  series even then: January 2025 was 58,460.1 and February 2025 56,390.0. And
  it is NOW FALSE as a current statement: July is 48,895.5.
  | `pipeline:statcan:12-10-0011-01`
- F2.24 "Gold still accounts for the clearest non-US export growth": NOT
  RE-VERIFIABLE for July. The scatter input file is frozen at May 2025 -> May
  2026 (W2). On that frozen window NAPCS 35 non-US domestic exports went from
  4,919.2 to 5,043.1 (C$M). I did not rebuild the July-to-July sector table.
  The Daily's July explanation of record non-US exports names other things:
  "Higher exports to the Netherlands (iron ores, nuclear fuel and crude oil),
  China (various products) and Germany (copper ores) contributed the most to
  the increase." So for July the "it is all gold" reading is at least
  incomplete. UNVERIFIED either way at sector level; the writer should not
  assert it for July.
- F2.25 Title "Trade diversification is extremely limited.": a judgement, but
  the facts under it have shifted. Non-US exports are at a record on both bases
  and the US share is near its series low. The writer needs to decide the take;
  the old one is not supported by July data.

---

## 3. What moved most since the old copy (May data, written July 7)

Ranked by size.

- F3.1 US share of exports: 69.7% (May, revised) -> 66.6% (July), -3.1 pts in
  two months and -6.4 pts on the year; second-lowest in the series. Driven by a
  fall in the numerator: exports to the US -6.5% in July (page basis). Daily
  verbatim: "Exports to the United States fell 6.6% in July, which was the
  strongest percentage decrease since April 2025. Lower exports of crude oil
  and gold were behind the decline in the month."
  OBSERVATION: the share fell because US-bound crude and gold fell while non-US
  shipments rose. INTERPRETATION (mine): this is partly price (oil, gold) and
  partly a real rise in non-US volumes; it is not clean evidence of a durable
  pivot from one month.
- F3.2 Trade balance: +C$3.7B (May, revised) -> +C$4.2B (June) -> +C$0.8B
  (July). The US surplus fell from C$10.3B to C$5.9B, "the lowest surplus since
  February 2026" (Daily); the non-US deficit narrowed to C$5.1B, "the lowest
  deficit observed since January 2021" (Daily).
- F3.3 Energy exports (headline basis; NOT in the pipeline): peaked April 2026
  at C$21.0B (20,964.7, record), May 20,401.3, June 18,881.5, July 18,051.1.
  July is -4.4% m/m, -13.9% from April, +38.5% from July 2025 (13,029.9).
  Crude oil and bitumen: April 15,800.6 (record), July 12,903.2.
  | Web Data Service, Table 12-10-0163-01, v1566911351 (energy), v1566911353
  (crude), release 2026-09-03; and Daily Table 2
  | `card:claim_statcan_cimt_jul2026_energy_exports_decline` (PENDING) for the
  -4.4% / third straight decline. The levels sit in the card's verified_value.
- F3.4 Gold: see 2.3. June series high C$8.6B, July C$6.8B; the "cooling" story
  in the old copy did not hold.
- F3.5 Current account: latest quarter is 2026 Q2 (released 2026-08-27).
  +C$8,836M, from -C$8,310M in Q1 (a C$17.1B swing).
  | data/raw/current_account_balance.csv (v61915304, Table 36-10-0018-01)
  | `pipeline:statcan:36-10-0018-01`
  Daily verbatim: "This was the first current account surplus since the second
  quarter of 2022 (+$3.5 billion) and the largest since the fourth quarter of
  2005 (+$12.5 billion)." Pipeline history agrees (2022Q2 +3,453; 2005Q4 +12,492).
  | https://www150.statcan.gc.ca/n1/daily-quotidien/260827/dq260827a-eng.htm
  Not claimed anywhere in the current trade copy; available if wanted.
- F3.6 Terms of trade: 110.7 in 2026 Q2 (152.7 / 137.9 x 100 = 110.73), from
  107.3 in Q1 (143.4 / 133.6): +3.4 index points, +3.2% q/q; +6.3% vs 2025 Q2
  (104.18). Highest since 2022 Q3 (112.59).
  | data/processed/terms_of_trade.csv; inputs v62307276, v62307279, Table
  36-10-0106-01, release 2026-08-28 | `derived` (ratio of two published price
  indexes), or `pipeline:statcan:36-10-0106-01` for the inputs
  Not claimed in the current copy.
- F3.7 Tariff state: changed materially, see section 4. Key point for the
  writer: every tariff action below took effect AFTER the July reference month.
  No published trade figure reflects them yet.

---

## 4. Tariff state (verified against government sources today)

- F4.1 `data/derived/tariff_state.json` problems:
  a) Rows `eo_14193_amendment_35pct` and `eo_14193_ieepa_canada_2025` say
     status "in_force". FALSE. The executive order "Ending Certain Tariff
     Actions" lists Executive Order 14193 and states the duties "shall no
     longer be in effect and, as soon as practicable, shall no longer be
     collected."
     | https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/
     (fetched 17:11Z, text matched). The order's date (February 2026) is from
     the URL path; I did not capture the signing date from the body.
  b) as_of is 2026-04-06; nothing from July-September 2026 is in it.
  c) Row `usmca_article_34_7` says "Review pending". The July 1, 2026 review
     date has passed. The only primary statement I have on the outcome is the
     White House's: "The United States, under President Trump's leadership, did
     not agree to renew the United States-Mexico-Canada Agreement (USMCA) in
     its current form" (July 20 fact sheet). That is the US position, not a
     joint or Canadian statement. I did not find or fetch a Government of
     Canada statement on the review. UNVERIFIED beyond that sentence.
  The Section 232 rows (steel/aluminum/copper 50%, autos 25%, lumber 10%) were
  NOT re-fetched today; their cards were verified 2026-05-13. The July 20 fact
  sheet still lists Section 232 tariffs on "steel, aluminum, copper, trucks and
  automobiles, timber, lumber, and pharmaceuticals" as actions taken, which is
  consistent with them standing, but I did not re-verify the rates.

- F4.2 New US action: July 20, 2026, three proclamations under Section 338 of
  the Tariff Act of 1930, additional 50% tariffs on certain Canadian goods
  (motor vehicles, alcoholic beverages, dairy as the stated grievances).
  | https://www.whitehouse.gov/fact-sheets/2026/07/fact-sheet-president-donald-j-trump-imposes-additional-tariffs-on-canada/
  | `card:claim_wh_s338_50pct_tariffs_canada_2026_07_20` (PENDING)
  Same page, verbatim: "These Section 338 tariffs apply to all covered goods
  regardless of whether a good originates under the U.S.-Mexico-Canada
  Agreement (USMCA). These Section 338 tariffs will not apply to energy,
  potash, products subject to tariffs under Section 232, and certain other
  goods, such as fish or critical minerals."
- F4.3 Effective date: originally August 19, 2026; moved to 12:01 a.m. eastern
  on August 22, 2026.
  | https://www.whitehouse.gov/presidential-actions/2026/08/temporary-suspension-of-additional-duties-to-offset-canadian-discrimination-against-the-commerce-of-the-united-states-with-respect-to-alcoholic-beverages-dairy-and-motor-vehicles/
  | `card:claim_wh_s338_effective_2026_08_22` (PENDING)
- F4.4 Canadian response: announced August 25, 2026; counter-tariffs of 15, 25
  and 50 per cent effective September 8, on C$27.6 billion of imports from the
  US; plus a C$7.5 billion support package. Canada "suspended negotiations".
  Canada describes the US tariff as "a 50 per cent tariff on $27.6 billion of
  Canadian goods effective August 22".
  | https://www.canada.ca/en/department-finance/news/2026/08/canada-announces-targeted-countermeasures-and-substantive-support-for-workers-and-businesses-in-response-to-us-tariffs.html
  | `card:claim_dof_countertariffs_effective_2026_09_08` (PENDING)
  The $27.6B coverage of the US tariff is CANADA'S figure; the White House fact
  sheet gives no value. Attribute it or leave it out.
- F4.5 US escalation, September 8, 2026: five more Section 338 proclamations;
  import bans on certain Canadian alcohol, dairy and motor-vehicle products
  effective September 29, 2026; product-scope changes effective September 15.
  White House says Canada's retaliation covers "about $20 billion of U.S.
  exports" (vs Canada's $27.6 billion; currencies not stated by either).
  | https://www.whitehouse.gov/fact-sheets/2026/09/fact-sheet-president-donald-j-trump-responds-to-canadas-retaliation/
  (fetched, text matched; NO card created -- request one if the bans go in prose)
- F4.6 Bank of Canada, September 2, 2026 statement (context only): "new US
  tariffs and Canadian counter-measures have been announced following the
  breakdown of trade talks between Canada and the United States."
  | https://www.bankofcanada.ca/2026/09/fad-press-release-2026-09-02/
- F4.7 NOT VERIFIED: the status of the temporary US import surcharge that
  replaced the emergency-powers tariffs in February 2026 (its rate, whether it
  applied to Canadian goods, whether it has lapsed). Secondary summaries say it
  was a 150-day measure; I did not fetch the proclamation. Do not mention it.

---

## 5. Source cards

- F5.1 The existing trade citation arrays (tile line, abstract, all four
  plates) use NO cards. Every entry is `pipeline:statcan:<table>` or `derived`.
  So there is no card to go stale; what went stale is the note text and values.
- F5.2 Registry cards that list `src/pages/trade.astro (plate-4)` in `cited_in`
  but are not actually cited by the current page: pp_section_232_steel_alum_50pct,
  pp_10908_section_232_autos, pp_10976_section_232_lumber,
  pp_section_232_metals_copper_2026, usmca_article_34_7. All verified
  2026-05-13, not re-fetched today. `usmca_article_34_7` is still accurate as
  treaty text but its `next_expected: 2026-07-01` has passed. The two
  emergency-powers cards (eo_14193_ieepa_canada_2025, eo_14193_amendment_35pct)
  describe duties that are no longer in effect (F4.1a); accurate as history,
  wrong if read as current. I did not edit registry.yaml.
- F5.3 New cards created today, all Tier A (primary fetched and excerpt
  string-matched), all in `editorial/source_cards/_pending/trade/` with
  `status: pending_user`. The build gate REFUSES any draft that cites them
  until Jay approves, so a redraft that must ship today should not use them:
  - claim_statcan_cimt_jul2026_nonus_exports_record.yaml
  - claim_statcan_cimt_jul2026_nonus_export_share.yaml
  - claim_statcan_cimt_jul2026_energy_exports_decline.yaml
  - claim_wh_s338_50pct_tariffs_canada_2026_07_20.yaml
  - claim_wh_s338_effective_2026_08_22.yaml
  - claim_dof_countertariffs_effective_2026_09_08.yaml
  The three Statistics Canada cards go stale on October 6.
- F5.4 A card-free redraft is possible. Everything in 2.1-2.4 and F3.5-F3.6
  resolves to pipeline strings:
  - balance, US share, exports to US / non-US (page basis): `pipeline:statcan:12-10-0011-01`
  - gold totals and UK flows: `pipeline:statcan:12-10-0182-01`; shares: `derived`
  - sector shares: `derived` (note naming StatCan 12-10-0182-01)
  - current account: `pipeline:statcan:36-10-0018-01`
  - terms of trade: `derived` / `pipeline:statcan:36-10-0106-01`
  Only energy exports, the headline-basis "record $25.6 billion / 33.7%"
  phrasing, and any tariff sentence need the pending cards.

---

## 6. What changed since the old copy -- plain English

Stamps: `blurb.date` "July 7, 2026", `updatedAt` (July 7), `heroKicker` "May
balance" and the comment "May merch-trade release landed July 7" are all two
releases behind. The latest release is July data, published September 3.

Tile line -- "Goods surplus widened to $4.2B in May; US export share rebounded to 70.0%."
- Both halves are wrong now. The surplus narrowed to $769 million in July (and
  May has been revised to $3.7 billion). The US share fell to 66.6%, not
  rebounded.

Abstract
- "The trade surplus widened again in May" -- outdated; it shrank sharply in July.
- "the US export share is back at 70.0% and looks little changed from a year
  ago" -- false. It is 66.6%, more than six points lower than a year earlier
  and close to the lowest on record.
- "mostly gold routed to London; that flow is cooling" -- false. Precious-metals
  exports set a new high in June and London-bound shipments rose in June and July.
- "aluminum is the only clear shift away from the US while copper leaned more
  heavily toward it" -- true only for the May-to-May comparison the chart still
  draws. On July data copper, aluminum and steel all moved away from the US and
  copper's direction reversed.
- The opening answer "Not really." rests on claims that no longer hold. The
  take needs to be re-decided, not just re-dated.

Plate 01 (balance and US share)
- Title "The US export share is back near 70%." -- false.
- April and May shares in the body are revised (68.8% and 69.7%, not 69.2% and 70.0%).
- "close to where it was a year earlier" -- false on July data.
- Callout "70.0%, +0.8pp" -- should be 66.6%, -1.7 points.
- "shipments to London surged, then cooled" -- outdated; they have since risen again.
- Source line names the wrong table for exports.

Plate 02 (sector scatter)
- "the surge is fading: ... C$8.0B in March to C$5.6B in May" -- May is revised
  to C$5.9B and the statement is overtaken by June's C$8.6B.
- "exports to the US rose to C$52.2B, a new high" -- false. Not a high even
  then; July is C$48.9B.
- "Strip out the gold ... and the pivot still is not there" -- cannot be checked
  for July because the chart's data file is frozen at May. Non-US exports are at
  a record and Statistics Canada credits iron ore, nuclear fuel, crude and
  copper ores, not gold, for July's increase.
- The chart itself still shows May 2025 to May 2026.

Plate 03 (gold)
- "Canada sold C$5.6 billion of precious metals in May" -- revised to C$5.9
  billion, and outdated (July: C$6.8 billion).
- "the UK's share fell to 83% from 97%" and the "83% / May 2026" callout --
  May revised to 80%; the latest is 87% in July.
- Title "...but the surge is cooling." -- false on the latest data.

Plate 04 (tariff-exposed sectors)
- All claims hold only on the May-to-May window the chart hardcodes; several
  supporting numbers in the citation notes were revised (steel, softwood, autos,
  copper starting points).
- On July data the title "Aluminum is the only clear move away from the US" is
  false, and the 62.9% aluminum figure turns out to be a one-month outlier.
- The chart must be re-pointed to the latest month before the prose can be.

Not in the old copy but now material: a new round of US tariffs on Canadian
goods (50%, effective August 22) and Canadian counter-tariffs (effective
September 8), both after the July data. The tariff-state fixture does not
contain them and wrongly shows the cancelled emergency-powers tariffs as in force.
