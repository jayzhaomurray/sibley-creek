# Trade section redraft -- build unblock 2026-10-03

Writer draft. Exact replacement text. Nothing under `src/` was edited.
Only fact source: `claude-ref/build_unblock_2026-10-03/trade_facts.md` (fact ids F... below).
Vintage: July 2026 merchandise trade release, published 2026-09-03. Not anticipating August (Oct 6).
No pending cards cited. Every source string is `pipeline:statcan:<table>` or `derived`.

Basis key used in notes:
- BoP SA = balance-of-payments basis, seasonally adjusted (the balance series; equals the StatCan headline).
- Customs SA = customs basis, seasonally adjusted (the page's export series; differs from headline).
- Customs NSA = customs basis, not seasonally adjusted (precious metals and sector series, Table 12-10-0182-01).

---

## A + B. `src/data/sections.ts`, block `slug: "trade"`

### Stamps

| Field | Current | New |
|---|---|---|
| code comment | `// May merch-trade release landed July 7, 2026.` | `// July merch-trade release landed September 3, 2026.` |
| `updatedAt` | `Date.UTC(2026, 6, 7, 8, 30)` | `Date.UTC(2026, 8, 3, 8, 30)` |
| `heroKicker` | `"May balance"` | `"July balance"` |
| `blurb.date` | `"July 7, 2026"` | `"Oct 3, 2026"` |

(`Date.UTC` months are zero-indexed: 8 = September. Time of day 8:30 kept.)

### A. tileLine

Current (74 characters):

```
Goods surplus widened to $4.2B in May; US export share rebounded to 70.0%.
```

New (75 characters; cap 90; +1.4% on the old one):

```
Goods surplus shrank to $769M in July from $4.2B as exports to the US fell.
```

```ts
    tileLine:
      "Goods surplus shrank to $769M in July from $4.2B as exports to the US fell.",
    tileLineCitations: [
      { phrase: "$769M in July", source: "pipeline:statcan:12-10-0011-01", note: "Goods trade balance, all countries, BoP SA (v87008984), July 2026: +C$769.2M. Equals the StatCan headline." },
      { phrase: "from $4.2B", source: "pipeline:statcan:12-10-0011-01", note: "Goods trade balance, BoP SA (v87008984), June 2026: +C$4,201.4M. Change June to July: 769.2 - 4,201.4 = -3,432.2." },
      { phrase: "exports to the US fell", source: "pipeline:statcan:12-10-0011-01", note: "Direction only, no number quoted. Exports to the US, customs SA (v87008898): 52,279.6 in June to 48,895.5 in July 2026 = -6.5%. Same direction on the BoP basis (-6.6%). Goods balance with the US, BoP SA (v87008985): 10,276.4 in June to 5,913.1 in July, a fall of 4,363.3, larger than the 3,432.2 fall in the total balance." },
    ],
```

Basis: both quoted numbers are BoP SA. The closing clause quotes no number and holds on both bases.

### B. blurb.body (answers "Is Canada's trade pivot working?")

Current (359 characters, 63 words):

```
Not really. The trade surplus widened again in May, but the US export share is back at 70.0% and looks little changed from a year ago. The apparent diversification pulse was still mostly gold routed to London; that flow is cooling, and among tariff-exposed sectors aluminum is the only clear shift away from the US while copper leaned more heavily toward it.
```

New (Gate 2 final: 346 characters, 65 words, 3 sentences):

```
It has started to, though gold flatters it. The US took 66.6% of goods exports in July, 6.4 points less than a year earlier, as sales to other markets rose 46%, far faster than US-bound sales. Precious metals shipped outside the US more than doubled over that year, and the share's fall from June owed as much to weaker US sales as to new buyers.
```

Structure: take (sentence 1) / mechanism (sentence 2: the share fell because non-US sales outgrew US sales) / landing (sentence 3: two reasons to discount the size). Three grounding numbers: 66.6%, 6.4 points, 46%.

```ts
    blurb: {
      kind: "last",
      date: "Oct 3, 2026",
      body:
        "It has started to, though gold flatters it. The US took 66.6% of goods exports in July, 6.4 points less than a year earlier, as sales to other markets rose 46%, far faster than US-bound sales. Precious metals shipped outside the US more than doubled over that year, and the share's fall from June owed as much to weaker US sales as to new buyers.",
    },
    abstractCitations: [
      { phrase: "66.6% of goods exports in July", source: "pipeline:statcan:12-10-0011-01", note: "US share of goods exports, customs SA, July 2026: 48,895.5 (v87008898) / 73,448.0 (v87008897) = 66.57%. Headline BoP basis is 66.3%; the page's charts draw the customs series." },
      { phrase: "6.4 points less than a year earlier", source: "derived", note: "Customs SA. July 2025: 45,404.1 / 62,211.1 = 72.98%. July 2026: 66.57%. 66.57 - 72.98 = -6.41 points. Source: StatCan 12-10-0011-01." },
      { phrase: "sales to other markets rose 46%", source: "derived", note: "Exports to non-US destinations, customs SA (total minus US): 24,552.5 in July 2026 vs 16,807.0 in July 2025 = +46.1%. Source: StatCan 12-10-0011-01." },
      { phrase: "far faster than US-bound sales", source: "derived", note: "Exports to the US, customs SA: 48,895.5 in July 2026 vs 45,404.1 in July 2025 = +7.7%, against +46.1% for non-US. Source: StatCan 12-10-0011-01." },
      { phrase: "gold flatters it", source: "derived", note: "Rests on the next entry: precious-metals exports outside the US rose from C$2,687.0M to C$6,290.2M July to July (customs NSA, StatCan 12-10-0182-01)." },
      { phrase: "Precious metals shipped outside the US more than doubled over that year", source: "derived", note: "NAPCS 35 (unwrought gold, silver, platinum-group metals), customs NSA, total minus US. July 2026: 6,819.5 - 529.3 = 6,290.2. July 2025: 4,413.4 - 1,726.4 = 2,687.0. Ratio 2.34. Source: StatCan 12-10-0182-01." },
      { phrase: "owed as much to weaker US sales as to new buyers", source: "derived", note: "June to July 2026, two decompositions of the fall in the US share. Customs SA (charted): exports to the US -3,384 (-6.5%), non-US +243 (+1.0%); share 68.26% to 66.57% = -1.69 points, of which -1.47 (87%) is due to the US fall. BoP SA (headline): exports to the US -3,578 (-6.6%), non-US +1,756 (+7.4%); share 69.39% to 66.35% = -3.04 points, of which -1.49 (49%) is due to the US fall. The US fall accounts for at least about half of the drop on both. Source: StatCan 12-10-0011-01." },
    ],
```

Basis: every number is customs basis. Sentence 2 is customs SA throughout. Sentence 3 pairs a customs NSA year-over-year ratio (precious metals) with an unquantified month-over-month comparison worded to hold on both the customs and the headline basis.

---

## C. `src/pages/trade.astro`

### Plate 01 (`plate-lead`) -- chart follows data to July 2026

Title, current:
```
The US export share is back near 70%.
```
Title, new (Gate 1 delta final, per Gate 3 retitle: 12 words, 64 characters):
```
The US export share fell in July even as gold shipments dropped.
```

interpretationHtml, current (47 words):
```
Canada's US-bound export share fell to 66.0% in March, then rebounded to 69.2% in April and 70.0% in May. That is close to where it was a year earlier. The apparent diversification pulse was mostly gold: shipments to London surged, then cooled as the gold flow normalized.
```
interpretationHtml, new (Gate 2 final: 66 words, 3 sentences):
```
The US took 66.6% of Canada's goods exports in July, 6.4 points less than a year earlier and close to March's low. Exports to the US fell 6.5% in the month while sales elsewhere reached their highest in data back to 1997. March's low rode a spike in bullion shipments to the UK; in July precious-metals exports fell by a fifth and the share dropped anyway.
```

Callout, current: `value: "70.0%"`, `delta: "+0.8pp m/m"`. New: `value: "66.6%"`, `delta: "-1.7pp m/m"`. `unitPrefix` and `direction` unchanged.

Source line, current:
```
Statistics Canada Tables 12-10-0011-01 (trade balance) and 12-10-0121-01 (exports by country).
```
Source line, new (F2.12: the export vectors are in 12-10-0011-01):
```
Statistics Canada Table 12-10-0011-01 (trade balance and exports by country); Table 12-10-0182-01 (precious-metals exports).
```

```ts
    title: "The US export share fell in July even as gold shipments dropped.",
    interpretationHtml:
      "The US took 66.6% of Canada's goods exports in July, 6.4 points less than a year earlier and close to March's low. " +
      "Exports to the US fell 6.5% in the month while sales elsewhere reached their highest in data back to 1997. " +
      "March's low rode a spike in bullion shipments to the UK; in July precious-metals exports fell by a fifth and the share dropped anyway.",
    callout: {
      value: "66.6%",
      unitPrefix: "US share of goods exports",
      delta: "-1.7pp m/m",
      direction: "neutral",
    },
    source: "Statistics Canada Table 12-10-0011-01 (trade balance and exports by country); Table 12-10-0182-01 (precious-metals exports).",
    data: leadData,
    citations: [
      { phrase: "gold shipments dropped", source: "pipeline:statcan:12-10-0182-01", note: "Title claim. NAPCS 35 total exports, customs NSA: 8,577.0 in June to 6,819.5 in July 2026 = -20.5% (headline basis: 10,071.1 to 8,752.1 = -13.1%). US share of goods exports fell June to July on both bases: customs SA 68.26% to 66.57%; headline 69.39% to 66.35%." },
      { phrase: "66.6% of Canada's goods exports in July", source: "pipeline:statcan:12-10-0011-01", note: "US share of goods exports, customs SA, July 2026: 48,895.5 / 73,448.0 = 66.57%. Callout delta: 66.57 - 68.26 (June) = -1.69 points." },
      { phrase: "6.4 points less than a year earlier", source: "derived", note: "Customs SA. July 2025: 45,404.1 / 62,211.1 = 72.98%. 66.57 - 72.98 = -6.41 points. Source: StatCan 12-10-0011-01." },
      { phrase: "close to March's low", source: "pipeline:statcan:12-10-0011-01", note: "Customs SA. March 2026 = 65.98%, the lowest of the 355 months in the series (starts January 1997). July 2026 = 66.57%, 0.59 points above it." },
      { phrase: "Exports to the US fell 6.5% in the month", source: "pipeline:statcan:12-10-0011-01", note: "Exports to the US, customs SA (v87008898): 52,279.6 in June to 48,895.5 in July 2026 = -6.5%. (Headline BoP basis: -6.6%.)" },
      { phrase: "sales elsewhere reached their highest in data back to 1997", source: "derived", note: "Exports to non-US destinations, customs SA (total minus US): 24,552.5 in July 2026, the highest of the 355 months in the series (starts January 1997). Also a record on the headline BoP basis (25,620.3). Source: StatCan 12-10-0011-01." },
      { phrase: "March's low rode a spike in bullion shipments to the UK", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 exports to the UK, customs NSA: C$7,818.6M in March 2026 (97.4% of the NAPCS 35 total of 8,026.3), against 5,565.0 in April and 4,716.0 in May." },
      { phrase: "precious-metals exports fell by a fifth", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 total exports, customs NSA: 8,577.0 in June to 6,819.5 in July 2026 = -20.5%." },
    ],
```

### Plate 02 (`plate-2`) -- chart FROZEN at May 2025 to May 2026

Title, current:
```
Trade diversification is extremely limited.
```
Title, new (Gate 2 final: 12 words, 62 characters):
```
Gold shipments outside the US barely moved in the year to May.
```

interpretationHtml, current (55 words):
```
Gold still accounts for the clearest non-US export growth, but the surge is fading: total precious-metals exports fell from C$8.0B in March to C$5.6B in May. At the same time, exports to the US rose to C$52.2B, a new high in the refreshed data. Strip out the gold corridor and the pivot still is not there.
```
interpretationHtml, new (Gate 2 final: 19 words, 1 sentence; July clause and the two sentences resting on it cut per Gate 1 F-C):
```
Precious-metals exports to buyers outside the US were C$5.0 billion in May 2026, against C$4.9 billion in May 2025.
```

Indicator (already dated May 2025 to May 2026), plateIndexLabel and source line: unchanged.

```ts
    title: "Gold shipments outside the US barely moved in the year to May.",
    interpretationHtml:
      "Precious-metals exports to buyers outside the US were C$5.0 billion in May 2026, against C$4.9 billion in May 2025.",
    source: "Statistics Canada Table 12-10-0182-01 (NAPCS sub-chapter exports by partner country).",
    data: plate2Data,
    citations: [
      { phrase: "C$5.0 billion in May 2026, against C$4.9 billion in May 2025", source: "derived", note: "NAPCS 35 exports to non-US destinations as drawn in the scatter (total minus US, customs NSA): May 2025 = 5,330.1 - 410.9 = 4,919.2; May 2026 = 5,592.7 - 549.6 = 5,043.1. Change +123.9, the basis for 'barely moved' in the title. The scatter's input (sectoral_exports_latest_yoy.csv) covers May 2025 to May 2026 and was last fetched 2026-07-07; the plate describes that window and that vintage, not the latest month. Source: StatCan 12-10-0182-01." },
    ],
```

### Plate 03 (`plate-3`) -- chart follows data to July 2026

plateIndexLabel, current: `"Gold corridor"` -- banned word. New: `"Gold route"`.

Title, current:
```
London is still buying most of Canada's gold, but the surge is cooling.
```
Title, new (Gate 2 final: 8 words, 49 characters):
```
London still takes most of Canada's gold exports.
```

interpretationHtml, current (64 words):
```
For decades, gold has been mined in Ontario and Quebec and sent straight to London's bullion banks, who store much of it in the Bank of England's vaults. The story is old; what changed was the scale of the flow. Canada sold C$5.6 billion of precious metals in May, down from C$8.0 billion in March, and the UK's share fell to 83% from 97%.
```
interpretationHtml, new (Gate 2 final: 32 words, 2 sentences; history sentence cut per Gate 1 F-D):
```
Canada exported C$6.8 billion of precious metals in July, half again as much as a year earlier, and the UK took 87% of it. Of June's C$8.6 billion, the UK took two-thirds.
```

Callout, current: `value: "83%"`, `delta: "May 2026"`. New: `value: "87%"`, `delta: "July 2026"`. Source line unchanged.

```ts
    plateIndexLabel: "Gold route",
    title: "London still takes most of Canada's gold exports.",
    interpretationHtml:
      "Canada exported C$6.8 billion of precious metals in July, half again as much as a year earlier, and the UK took 87% of it. " +
      "Of June's C$8.6 billion, the UK took two-thirds.",
    callout: {
      value: "87%",
      unitPrefix: "UK share of gold/PGM exports",
      delta: "July 2026",
      direction: "neutral",
    },
    source: "Statistics Canada Table 12-10-0182-01 (NAPCS 35: unwrought gold, silver, and PGM by partner country); Yahoo Finance (gold futures, USD/oz).",
    data: plate3Data,
    citations: [
      { phrase: "C$6.8 billion of precious metals in July", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 total exports, all countries, customs NSA, July 2026: C$6,819.5M." },
      { phrase: "half again as much as a year earlier", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 total exports, customs NSA: 6,819.5 in July 2026 vs 4,413.4 in July 2025 = +54.5%." },
      { phrase: "the UK took 87% of it", source: "derived", note: "UK share of NAPCS 35 exports, July 2026: 5,939.0 / 6,819.5 = 87.1%. Source: StatCan 12-10-0182-01." },
      { phrase: "June's C$8.6 billion", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 total exports, all countries, customs NSA, June 2026: C$8,577.0M." },
      { phrase: "the UK took two-thirds", source: "derived", note: "UK share of NAPCS 35 exports, June 2026: 5,748.5 / 8,577.0 = 67.0%. Source: StatCan 12-10-0182-01." },
    ],
```

The history sentence and its two citations are cut (Gate 1 F-D). The "highest month in the data" superlative is cut from the body as well as the title (Gate 1 F-E: true on the charted series only).

### Plate 04 (`plate-4`) -- chart FROZEN, hardcoded May 2025 vs May 2026 (draws revised May values)

Title, current:
```
Aluminum is the only clear move away from the US.
```
Title, new:
```
Aluminum's May swing away from the US was a one-month spike.
```

interpretationHtml, current (63 words):
```
Of the tariff-exposed sectors charted, aluminum is the only clear move away from the US between May 2025 and May 2026. Its US share fell from 88.7% to 62.9%, while steel, softwood, and autos each moved away by less than five points and copper moved further toward the US. One sector is moving; the rest are still mostly tied to the US market.
```
interpretationHtml, new (Gate 2 final: 68 words, 3 sentences):
```
Aluminum's US share fell to 62.9% in May 2026 from 88.7% a year earlier, the only large move among five export sectors. One month of unusually large shipments to other markets produced it, and the share had recovered to 81.5% by July. From July to July, copper, aluminum, and steel each moved away from the US by roughly 6 to 9 points, while autos and softwood barely shifted.
```

Indicator (already dated May 2025 vs May 2026), plateIndexLabel and source line: unchanged.

```ts
    title: "Aluminum's May swing away from the US was a one-month spike.",
    interpretationHtml:
      "Aluminum's US share fell to 62.9% in May 2026 from 88.7% a year earlier, the only large move among five export sectors. " +
      "One month of unusually large shipments to other markets produced it, and the share had recovered to 81.5% by July. " +
      "From July to July, copper, aluminum, and steel each moved away from the US by roughly 6 to 9 points, while autos and softwood barely shifted.",
    source: "Statistics Canada Table 12-10-0182-01 (NAPCS sub-chapter exports by partner country).",
    data: plate4Data,
    citations: [
      { phrase: "62.9% in May 2026 from 88.7% a year earlier", source: "derived", note: "Aluminum US share of sector exports, customs NSA: May 2025 = 88.69%; May 2026 = 62.94% (912.5 / (912.5 + 537.3)). Change -25.75 points. These are the two points the chart draws. Source: StatCan 12-10-0182-01." },
      { phrase: "the only large move among five export sectors", source: "derived", note: "Five sectors: steel, aluminum, copper, softwood lumber, autos and parts. US share change May 2025 to May 2026: aluminum -25.75; steel 90.94 to 87.04 = -3.90; copper 87.44 to 90.65 = +3.21; autos 90.74 to 88.32 = -2.42; softwood 88.78 to 88.13 = -0.65. Source: StatCan 12-10-0182-01." },
      { phrase: "One month of unusually large shipments to other markets produced it", source: "derived", note: "Aluminum exports to non-US destinations, customs NSA: C$129M in April 2026, C$537.3M in May, C$225.1M in June, C$230.7M in July. Source: StatCan 12-10-0182-01." },
      { phrase: "recovered to 81.5% by July", source: "derived", note: "Aluminum US share: 80.6% in June 2026 (937.1 / (937.1 + 225.1)); 81.52% in July 2026 (1,017.9 / (1,017.9 + 230.7)). Source: StatCan 12-10-0182-01." },
      { phrase: "copper, aluminum, and steel each moved away from the US by roughly 6 to 9 points", source: "derived", note: "US share, July 2025 to July 2026: copper 93.14 to 84.51 = -8.63; aluminum 90.06 to 81.52 = -8.54; steel 89.76 to 84.02 = -5.74. Three sectors. Not drawn on the chart, which is fixed at May. Source: StatCan 12-10-0182-01." },
      { phrase: "autos and softwood barely shifted", source: "derived", note: "US share, July 2025 to July 2026: autos and parts 89.46 to 88.12 = -1.34; softwood 89.17 to 89.43 = +0.26. Source: StatCan 12-10-0182-01." },
    ],
```

---

## Left alone

- Plate 01: `indicator`, `plateIndexLabel`, callout `unitPrefix` and `direction`.
- Plate 02: `indicator`, `plateIndexLabel`, `source`.
- Plate 03: `indicator`; `source`; callout `unitPrefix` and `direction`. (The history sentence and its two citations were cut at Gate 2 per Gate 1 F-D.)
- Plate 04: `indicator`, `plateIndexLabel` ("Tariff-exposed sectors"), `source`.
- `pageDescription` in trade.astro (search copy, not the writer's; still accurate).
- No plate body survived whole: every plate had at least one false or outdated claim.

## Cut and why

- All tariff and trade-policy assertions. The old plate 04 citation note asserted Section 232 and anti-dumping coverage; the new plate 04 prose says "the five export sectors compared" and its notes make no tariff claim. No sentence mentions the trade-agreement review, the February import surcharge, the July-September tariff rounds or any rate.
- "exports to the US rose to C$52.2B, a new high" (false then and now, F2.23).
- "Strip out the gold corridor and the pivot still is not there" (banned word; not checkable for July, F2.24).
- "One sector is moving; the rest are still mostly tied to the US market" (false on July data, F2.19).
- "The story is old; what changed was the scale of the flow" (cut for length).
- Aluminum/copper sentence in the abstract (true only May to May, F2.4).

## Flags

1. Plate 02 mixes two flavours of the precious-metals series: the May figures are the frozen scatter file (F2.24 calls them domestic exports, total 5,592.7 for May 2026), the July figures are the refreshed plate 03 series (total exports). Each comparison is internally consistent; fact-checker should confirm they can sit in adjacent sentences.
2. Plate 02 prose is confined to the one sector the fact pack verified on the frozen window. The scatter draws about 100 sectors; the blurb does not describe the rest. The chart needs re-pointing to the latest month.
3. Plate 03 title "new high in June" is true on the customs series the chart draws; on the seasonally adjusted headline basis the high is March 2026 (F2.16).
4. Plate 03 history sentence and its two `derived` citations carry over unverified (F2.3 note). They cite no card and show no arithmetic.
5. Plate 04's `indicator` and `plateIndexLabel` still say "Tariff-exposed sectors". That label rests on registry cards verified 2026-05-13, not re-fetched today (F4.1, F5.2). Unchanged; editorial-director's call.
6. Plate 01 callout `direction` left at "neutral" as before; switch if the component has a "down" state.
7. Plate bodies run longer than the old ones (82, 61, 72, 73 words vs 47, 55, 64, 63). All are three or four sentences.
8. Abstract take changed from "Not really" to "It has started to, though gold flatters it." This is a framing decision for Jay's veto.
9. "London" in the plate 03 title stands for UK-bound shipments (the data are by country).

## NEW CLAIMS INTRODUCED (all need Gate 1)

Tile line
- surplus $769M in July, from $4.2B (June)
- exports to the US fell (direction, July)

Abstract
- US share 66.6% in July; 6.4 points below a year earlier
- non-US exports up 46% on the year; US-bound exports up more slowly (+7.7%)
- precious metals shipped outside the US more than doubled July to July (2,687.0 to 6,290.2)
- July's share drop owed more to lower US exports than to higher non-US exports

Plate 01
- "close to March's low" (March 2026 = lowest of 355 months since January 1997)
- exports to the US -6.5% in July
- non-US exports at their highest in data back to 1997 (superlative)
- March's low coincided with a spike in UK-bound bullion (C$7.8B)
- precious-metals exports fell by a fifth in July (-20.5%)
- surplus C$769M from C$4.2B
- callout 66.6%, -1.7pp m/m
- title: July's share drop came from weaker US sales, not gold

Plate 02
- non-US precious-metals exports C$4.9B (May 2025) and C$5.0B (May 2026)
- non-US precious-metals exports C$2.7B (July 2025) and C$6.3B (July 2026), more than doubling

Plate 03
- C$6.8B in July; +54.5% on the year ("half again as much")
- UK share 87% in July; callout 87% / July 2026
- June C$8.6B, highest month in the data (superlative)
- UK took two-thirds in June (67.0%)

Plate 04
- aluminum 62.9% (May 2026) from 88.7% (May 2025); only large move among five sectors (countable: five)
- produced by one month of large non-US shipments (C$537M vs C$129M April, C$225M June)
- aluminum share 81.5% by July
- July to July: copper -8.6, aluminum -8.5, steel -5.7 (countable: three sectors); autos -1.3, softwood +0.3
- title: the May swing was a one-month spike

---

## Gate 1 verdict (fact-check, 2026-10-03)

Checked against: working-tree pipeline files (data/raw, data/processed, data/site/panel_data/trade.json generated 2026-10-03T17:22Z), the frozen scatter file (sectoral_exports_latest_yoy.csv, fetched 2026-07-07), PanelSectorPivot.astro, the Statistics Canada Web Data Service (queried today; pipeline values match to the decimal) and The Daily of 2026-09-03 (fetched today). White House fact sheet of 2026-07-20 re-fetched for the tariff label. Nothing under src/ touched.

### Verdict per surface

| Surface | Verdict |
|---|---|
| Stamps | PASS |
| Tile line | PASS |
| Section abstract | PASS with flag (F-A) |
| Plate 01 title, body, callout, source line | PASS with flags (F-A, F-B) |
| Plate 02 title, body | FAIL as written (F-C): May and July figures are not like-for-like |
| Plate 03 title, body, callout | FAIL on the first (history) sentence (F-D); the rest PASS with a flag on the title (F-E) |
| Plate 04 title, body, labels | PASS with note (F-F) |
| Mechanics (all surfaces) | PASS |

### Corrections applied in this file

- Plate 04 word-count note: 73 -> 74 (the build counter's figure). No prose, digit, period, citation phrase or stamp needed correcting.

### Arithmetic (recomputed, C$ millions)

Total and US exports, customs SA (v87008897, v87008898); balance BoP SA (v87008984).

| Month | Total | To US | Non-US | US share | Balance |
|---|---|---|---|---|---|
| Jul 2025 | 62,211.1 | 45,404.1 | 16,807.0 | 72.98% | -3,914.5 |
| Mar 2026 | 68,985.4 | 45,516.7 | 23,468.7 | 65.98% | 1,343.6 |
| Jun 2026 | 76,589.5 | 52,279.6 | 24,309.9 | 68.26% | 4,201.4 |
| Jul 2026 | 73,448.0 | 48,895.5 | 24,552.5 | 66.57% | 769.2 |

- 66.57 - 72.98 = -6.41 points on the year; 66.57 - 68.26 = -1.69 on the month. Verified.
- Non-US on the year: 24,552.5 / 16,807.0 = +46.1%. US on the year: 48,895.5 / 45,404.1 = +7.7%. Verified.
- US on the month: -6.47% (-3,384.1). Non-US on the month: +1.0% (+242.6). Verified.
- March 2026 is the lowest share of 355 months and July 2026 the second lowest; July 2026 non-US exports are the highest of 355 months. Enumerated, verified.
- Headline (BoP SA, v87008955 and v87008956): July 76,137.4 total / 50,517.1 US; June 77,959.1 / 54,094.9. US -6.6%, non-US +7.4% to a record 25,620.3, share 69.39% -> 66.35%. The Daily: surplus "narrowed from $4.2 billion in June to $769 million in July".
- Precious metals (NAPCS 35, customs NSA): total 4,413.4 (Jul 2025), 8,026.3 (Mar 2026), 8,577.0 (Jun 2026), 6,819.5 (Jul 2026). June to July -20.5%; July on July +54.5%. Non-US: 2,687.0 -> 6,290.2, ratio 2.34. UK share 87.1% (July), 67.0% (June). Verified.
- Sector US shares (May 2025 / May 2026 / Jul 2025 / Jul 2026): aluminum 88.69 / 62.94 / 90.06 / 81.52; copper 87.44 / 90.65 / 93.14 / 84.51; steel 90.94 / 87.04 / 89.76 / 84.02; autos 90.74 / 88.32 / 89.46 / 88.12; softwood 88.78 / 88.13 / 89.17 / 89.43. Verified. Five sectors are drawn; three moved 5.7 to 8.6 points July to July.

### Basis consistency (brief item 1)

- Tile line: both numbers are BoP SA (the headline). "Exports to the US fell" is true on both bases (-6.5% customs, -6.6% BoP). No mixing.
- Abstract: every number is customs basis. No sentence mixes bases.
- Plate 01: sentences 1 to 3 are customs (what the right panel draws); sentence 4 is BoP (what the left panel draws). No sentence mixes bases, but the plate as a whole does, as its chart does.
- Each plate quotes numbers its own chart draws, except plate 02 (F-C). The July figures in plates 02 and 04 are labelled as July and are not on the frozen charts.

### Causal and directional claims (brief item 2)

"as exports to the US fell" (tile): true month over month on both bases. The surplus with the US fell 4,363.3, more than the 3,432.2 fall in the total. Holds.

"owed more to weaker US sales than to new buyers" / "came from weaker US sales":

| Basis, June -> July | US | Non-US | Share change | Part due to the US fall |
|---|---|---|---|---|
| Customs SA (charted) | -3,384 (-6.5%) | +243 (+1.0%) | -1.69 | -1.47 (87%) |
| BoP SA (headline) | -3,578 (-6.6%) | +1,756 (+7.4%) | -3.04 | -1.49 (49%) |
| Customs SA less precious metals | -3,022 (-5.9%) | +1,638 (+9.9%) | -2.97 | -1.16 (39%) |
| Customs NSA less precious metals | -4,643 (-8.7%) | +518 (+3.1%) | -2.27 | -1.70 (75%) |

In dollars the US fall is larger than the non-US rise on every basis. As a share of the point change it is 87% on the charted basis, about half on the headline basis, and under half once precious metals are taken out of the seasonally adjusted series (that row subtracts unadjusted metals from adjusted totals, so it is approximate). The claim holds on the basis the page uses, and under the dollar reading everywhere; it is not robust as a share decomposition. See F-A.

"not gold" (plate 01 title): holds on every reading. Non-US precious-metals exports fell 1,396 in July, which pushed the US share up. Without precious metals the share fell further (75.56% -> 72.59%, -2.97) than with them (-1.69).

"It has started to, though gold flatters it": holds. US share excluding precious metals: 75.57% in July 2025 and 72.59% in July 2026, a fall of 2.98 points, so just under half of the 6.41 points survives. (All-unadjusted customs series: 77.20% -> 73.74%, -3.46 of -6.90.) Excluding precious metals, non-US exports still rose 29.3% against 10.7% for the US. Precious metals were 3,603 of the 7,746 rise in non-US exports (47%).

### Superlatives (brief item 3)

- "new high in June": true on the series the chart draws (8,577.0, above March's 8,026.3; highest of 355 months; nominal, unadjusted). On the headline basis (v1566911383) March is the high (10,893.9 against June's 10,071.1). See F-E.
- "London still takes most of them": holds as over half. UK share 87% in July, 67% in June, 85% over the last 12 months, and above half in every month since March 2025.
- "one-month spike": holds for May against its neighbours. Aluminum non-US shipments: 129 (April), 537 (May, the highest month in the series), 225 (June), 231 (July). US share 88.2 / 62.9 / 80.6 / 81.5. See F-F.

### Open flags for a human decision

- F-A (abstract sentence 3; plate 01 title and "edged up"). Not blocking. Statistics Canada's headline says exports to other countries rose 7.4% to a record; the page's customs series says 1.0%. A reader checking the release will see the gap. Smallest fix if wanted: in the abstract, "owed more to weaker US sales than to new buyers" -> "owed as much to weaker US sales as to new buyers", which is true on every row of the table above.
- F-B (plate 01). Not blocking. The 66.6% share is the customs figure; the headline equivalent is 66.3%. Existing page convention; the source line names the table.
- F-C (plate 02). Blocking. The May figures come from the frozen scatter file: domestic exports, 7 July vintage (4,919.2 -> 5,043.1). The July figures are total exports, today's vintage. May 2026 has since been revised: non-US is now about 5,137 on either flavour (domestic 5,869.6 - 732.3; total 5,875.0 - 737.0), so "C$5.0 billion" is no longer the published value. The domestic-versus-total difference is small (July: 2,613.6 -> 6,289.9 domestic against 2,687.0 -> 6,290.2 total); the vintage difference is what breaks the comparison. Recommended: cut "the same comparison for July shows those shipments more than doubling, to C$6.3 billion from C$2.7 billion" and its citation. That leaves the title unsupported, so it needs a writer retitle. Alternative that keeps the take: change "C$5.0 billion" to "C$5.1 billion" and repoint that citation note to the plate 03 series (May 2025 4,920.0; May 2026 5,138.1), putting both comparisons on one series and one vintage; the frozen scatter's gold dot would then be C$94M off on the non-US axis, not visible at chart scale. "Barely moved" and "more than doubling" hold either way. The plate is dated May and does not present May as the latest reading.
- F-D (plate 03 first sentence). Blocking; recommend cutting the sentence and its two citations. The page's own series contradicts "for decades ... sent straight to London": the UK took 0% to 8% of these exports in 1997-2002 (the US took 77% to 96%), passed half only in 2006, and took 30% in 2023. The two citations are tagged "derived" but are not arithmetic; their figures (three-quarters of production, the 1934 listing, 5,000 and 300 tonnes) have no source card and were not verified. Without the sentence the body is 44 words and still passes the gate.
- F-E (plate 03 title). Editorial call. "New high in June" is true only on the charted customs series, and it leads with a month that has been superseded: July fell 20.5%, and on the headline basis the high is March. A reader comparing with the release could be misled. Options: accept as is, or retitle on July (the UK took 87%).
- F-F (plate 04). Title holds, with context the editor should know: aluminum's US share was also between 66% and 77% from August to December 2025, so May 2026 is the lowest reading but not the only low one, and "recovered to 81.5%" is still below April's 88.2%. The label "Tariff-exposed sectors" remains accurate: all five sectors sit under Section 232 rows of the corrected fixture, and the White House fact sheet of 20 July 2026 still lists Section 232 tariffs on "steel, aluminum, copper, trucks and automobiles, timber, lumber". No rewording needed. The plate is dated May and labels its July figures as July.
- Writer flag 8 (the take changing from "Not really" to "It has started to") stays with Jay.

### Mechanics (brief item 7, by script)

- All 34 citation phrases are exact substrings of their prose; none nested or overlapping.
- All source strings are `pipeline:statcan:<table>` or `derived`; none cites a card, so none cites `_pending/`.
- Every token the coverage gate extracts is covered on all six surfaces.
- Tile line: 75 characters, 15 words, 1 sentence (caps 90 / 20 / 1). Abstract: 66 words, 3 sentences (hard caps 105 / 5). Plate bodies: 82 / 61 / 72 / 74 words (hard cap 110; the three over 70 draw a warning that does not fail the build). Titles: 14 / 10 / 15 / 11 words (hard cap 22; the 15 draws a warning).
- No bank economists cited, no placeholder text, no banned "corridor" in the new copy.
- Not done: the precious-metals-excluded share computed above was not added to `editorial/_derived_slot_queue.yaml`, because a queue entry makes the build refuse and this deploy is blocked on the build. Queue it after the unblock if the "gold flatters it" line stays.

---

## Gate 2 verdict (style polish, 2026-10-03)

The body above now holds the final paste-ready text. Nothing under `src/` touched. The writer's "Flags" and "NEW CLAIMS INTRODUCED" sections and the Gate 1 verdict describe the pre-polish draft and are left as the record. Counts below are hand counts (no script was available to this gate); re-run the build counter before paste.

### Required Gate 1 fixes applied

1. Plate 02 (F-C). July clause cut with its citation. The two sentences that rested on it ("Bullion is lumpy and the base month decides the answer", "One month's sector picture is weak evidence of a pivot in either direction") cut too: with July gone they had no support, and the second was a balanced flourish. Retitled on the May text alone.
2. Plate 03 (F-D). History sentence and its two citations cut.
3. Plate 03 title (F-E). Retitled on London's share, the one claim Gate 1 verifies without a basis caveat. The body's "highest month in the data" superlative cut for the same reason the title's was.
4. Abstract (F-A). Final clause now "owed as much to weaker US sales as to new buyers"; citation phrase updated; note states both decompositions (customs 87%, headline 49%).

### Changes, before and after

Tile line: unchanged.

Abstract
- Before: "...as sales to other markets rose 46% and US-bound sales grew far more slowly."
  After: "...as sales to other markets rose 46%, far faster than US-bound sales." (concision; citation phrase now "far faster than US-bound sales")
- Before: "and July's drop in the share owed more to weaker US sales than to new buyers."
  After: "and the share's fall from June owed as much to weaker US sales as to new buyers." (required fix 4; subject reworded because "July's drop" sat one sentence after the year-over-year fall and could be read as either. NON-MECHANICAL, writer to review.)

Plate 01
- Title: unchanged.
- Before: "while sales to other markets edged up to their highest in data back to 1997"
  After: "while sales elsewhere reached their highest in data back to 1997" ("edged up" was the F-A exposure: +1.0% on the charted series, +7.4% on the headline. The record holds on both.)
- Cut: "The goods surplus narrowed to C$769 million from C$4.2 billion in June." and its citation. The sentence did not explain the title; the figure is on the tile line and in the plate's left panel. NON-MECHANICAL, writer to review.

Plate 02
- Title before: "Gold's contribution to non-US exports swings with the month compared."
  After: "Gold shipments outside the US barely moved in the year to May."
- Body before: three sentences, 61 words. After: "Precious-metals exports to buyers outside the US were C$5.0 billion in May 2026, against C$4.9 billion in May 2025." "Barely moved" moved to the title so the body does not repeat it. Two citations merged into one.

Plate 03
- Title before: "Gold exports hit a new high in June, and London still takes most of them."
  After: "London still takes most of Canada's gold exports."
- Body before: three sentences, 72 words. After: "Canada exported C$6.8 billion of precious metals in July, half again as much as a year earlier, and the UK took 87% of it. Of June's C$8.6 billion, the UK took two-thirds."
- Citation "June's C$8.6 billion was the highest month in the data" replaced by "June's C$8.6 billion" (level only).

Plate 04
- Title: unchanged.
- "among the five export sectors compared" -> "among five export sectors".
- "It did not last: one month of..." -> "One month of..." (setup clause cut; citation phrase recapitalized).
- "On a July-to-July comparison" -> "From July to July".
- "roughly six to nine points" -> "roughly 6 to 9 points" (numerals for statistical quantities).

### Final counts

| Surface | Sentences | Words | Characters | Budget | Result |
|---|---|---|---|---|---|
| Tile line | 1 | 15 | 75 | 90 chars | PASS |
| Abstract | 3 | 65 | 346 | 359 chars, 3 to 4 sentences | PASS |
| Plate 01 title | 1 | 14 | 71 | 22 words, 110 chars | PASS |
| Plate 01 body | 3 | 66 | - | target 60, warn 70, cap 110 | PASS (was 82) |
| Plate 02 title | 1 | 12 | 62 | | PASS |
| Plate 02 body | 1 | 19 | - | soft floor 2 sentences, 40 words | PASS on caps; UNDER the soft floor (was 61) |
| Plate 03 title | 1 | 8 | 49 | | PASS |
| Plate 03 body | 2 | 32 | - | soft floor 40 words | PASS on caps; under the soft floor (was 72) |
| Plate 04 title | 1 | 11 | 60 | | PASS |
| Plate 04 body | 3 | 68 | - | target 60, warn 70, cap 110 | PASS (was 74) |

Callouts: plate 01 `unitPrefix` 5 words, `delta` "-1.7pp m/m" 2 tokens; plate 03 `unitPrefix` 5 words, `delta` "July 2026". No verbs. PASS.

Citation entries: abstract 7, tile 3, plate 01 7, plate 02 1, plate 03 5, plate 04 6. Each phrase checked by eye as an exact substring of its final prose.

### Canon checklist

- Header question "Is Canada's trade pivot working?" (confirmed in `src/data/sections.ts`): "It has started to, though gold flatters it." reads as a direct answer. PASS.
- Abstract structure: take / mechanism (non-US sales outgrew US sales) / landing (two reasons to discount). Three grounding numbers (66.6%, 6.4 points, 46%). Synthesis, not a recital. PASS.
- Plate titles: sentence case, terminal period, one verb, no colon or semicolon. PASS all four. Titles 01, 03, 04 name a finding. Title 02 names a level, which is all its one verified fact supports. WEAK.
- Stand-alone: tile, abstract and each title carry their claim alone. PASS. Plate 02 body is the title with the two figures attached, so it fails the title-repetition check; no second beat can be written from verified material (see flags).
- Title/body second beat: 01 PASS, 03 PASS (scale, year-over-year growth, June contrast), 04 PASS.
- No signpost or setup sentences, nothing about method, no source names in prose, no cross-links, no customs-versus-balance-of-payments explanation. PASS.
- Banned words: no "corridor" (plate 03 label is "Gold route"), no "load-bearing", no math symbols, no "per cent". PASS.
- Acronyms: US and UK only in prose. "PGM" appears only in a callout label and a source line, both exempt. PASS.
- Numbers: "6.4 points" kept rather than "6.4pp" for plain reading; consistent across abstract and plates.

### Wording new at Gate 2 that Gate 1 must re-check

No new figure, date or superlative was added. Reworded claims:

1. Abstract: "far faster than US-bound sales" (+46.1% against +7.7%).
2. Abstract: "the share's fall from June owed as much to weaker US sales as to new buyers" (the both-bases form, with "from June" naming the month-over-month window).
3. Plate 01: "sales elsewhere reached their highest in data back to 1997" ("edged up" dropped; same superlative).
4. Plate 02 title: "Gold shipments outside the US barely moved in the year to May." (4,919.2 to 5,043.1 on the frozen file; "gold" stands for the precious-metals group, as elsewhere on the page).
5. Plate 02 body: figure order and dating, "C$5.0 billion in May 2026, against C$4.9 billion in May 2025".
6. Plate 03 title: "London still takes most of Canada's gold exports." (Gate 1: UK share above half in every month since March 2025).
7. Plate 03 body: "Of June's C$8.6 billion, the UK took two-thirds."
8. Plate 04: "the only large move among five export sectors"; "From July to July"; "roughly 6 to 9 points" (5.74, 8.54, 8.63).

### Flags

- F2-1. Plate 02 is one sentence that restates its title with numbers. The frozen chart has one verified fact. A second beat needs a new claim from the writer, or the chart re-pointed to current data. Also still open from Gate 1 F-C: the "C$5.0 billion" the frozen chart draws has since been revised to about C$5.1 billion.
- F2-2. Plate 01 title "came from weaker US sales, not gold" was not in the required fixes and is unchanged, but its first half is the same single-basis claim the abstract was softened for (87% on the charted series, 49% on the headline). "Not gold" holds everywhere. A both-bases title built only from verified text: "The US export share fell in July even as gold shipments dropped." Not applied; editorial call.
- F2-3. Plate 01 no longer mentions the goods surplus its left panel draws. Restoring the cut sentence takes the body to 78 words.
- F2-4. Plate 03 body no longer says June was the highest month on record. It is a real finding on the charted series; restore "June's C$8.6 billion was the highest month in the data" only if the single-basis caveat is accepted.
- F2-5. Plate 03 title alternative leading with the fall, if preferred: "Gold exports fell by a fifth in July, and London still takes most of them." The 20.5% is verified on the charted series only; no headline-basis July figure is in the Gate 1 verdict, so it was not used.
- F2-6. Plates 02 and 03 run under the 40-word soft floor. The length check in `scripts/source_audit.mjs` shows hard caps and over-target warnings only; no minimum was seen to be enforced, but confirm on the build.
- Unchanged from Gate 1: the take ("It has started to") is Jay's call; plate 04 F-F context.

---

## Gate 1 delta verdict (fact-check of Gate 2 changes, 2026-10-03)

Scope: only what Gate 2 changed. Recomputed from data/raw (customs SA v87008897/8, customs NSA v87008868/9, NAPCS 35 gold series), the frozen scatter file, and the Statistics Canada Web Data Service for the headline series (v87008955/6, fetched today). Nothing under src/ touched. No prose, citation or count in the body above needed a mechanical correction; none applied.

### Item 1. The eight rewordings

| # | Wording | Verdict |
|---|---|---|
| 1 | "far faster than US-bound sales" | PASS. July 2025 to July 2026: customs SA non-US +46.1%, US +7.7%. Headline basis +49.8% against +11.2% (62,531.5 / 45,423.9 in July 2025). Customs unadjusted +49.8% against +7.0%. |
| 2 | "the share's fall from June owed as much to weaker US sales as to new buyers" | PASS WITH FLAG (D-1). |
| 3 | "sales elsewhere reached their highest in data back to 1997" | PASS. 24,552.5, highest of 355 months on the charted series; also a record on the headline basis (25,620.3). |
| 4 | Plate 02 title "barely moved in the year to May" | FLAG (D-2). True only as May against May. |
| 5 | Plate 02 body, C$5.0 billion against C$4.9 billion | PASS against the frozen chart as drawn (5,043.1 and 4,919.2). Still open from F-C: May 2026 is now published as 5,138.1. |
| 6 | Plate 03 title "London still takes most of Canada's gold exports" | PASS. UK share 87.1% in July, 84.8% over the last 12 months, above half in every month since March 2025. Over the chart's window (August 2006 on) the UK took 62% and was above half in 171 of 240 months. Context: 30% in calendar 2023, 40% and 30% in January and February 2025. |
| 7 | "Of June's C$8.6 billion, the UK took two-thirds." | PASS. 5,748.5 / 8,577.0 = 67.0%. |
| 8 | Plate 04: "the only large move among five export sectors"; "From July to July"; "roughly 6 to 9 points" | PASS. 5.74, 8.54, 8.63; five sectors drawn. |

Share decomposition, June to July (part of the fall due to the US decline, either ordering):

| Basis | Share change | US part | US, C$M | Non-US, C$M |
|---|---|---|---|---|
| Customs SA (charted) | -1.69 | 87% | -3,384 | +243 |
| Headline (BoP SA) | -3.04 | 48% to 50% | -3,578 | +1,756 |
| Customs unadjusted | -1.30 | about 160% (non-US fell too) | -5,004 | -877 |

### Item 2. Cross-surface consistency

- D-1 (abstract, meaning change, not applied). "As much ... as" is not false on the charted basis if read as "no less than", but read as "equal parts" it understates 87 against 13 and sits oddly beside plate 01's title. Smallest fix: "owed at least as much to weaker US sales as to new buyers" (citation phrase becomes "owed at least as much to weaker US sales as to new buyers"). True at 87% on the charted basis; on the headline basis the split is 48% to 50%, equal within rounding, and the US fall is twice the non-US rise in dollars. With that change plate 01's title ("came from weaker US sales, not gold") is consistent with the abstract. If the abstract stays as is, take Gate 2's alternative title: "The US export share fell in July even as gold shipments dropped."
- D-2 (plate 02 title against the abstract, meaning change, not applied). Both statements are true on their own endpoints: abstract 2,687.0 to 6,290.2 (July on July, total exports, today's vintage, ratio 2.34); plate 02 4,919.2 to 5,043.1 (May on May, domestic exports, 7 July vintage; +2.5%, or +4.4% on today's vintage). A reader will see them as contradictory, and the plate 02 title is the weak one. "In the year to May" also reads as "over those twelve months", and on that reading it is false: monthly non-US shipments ranged from 2,687 to 7,869 inside the window, and the 12 months to May 2026 summed to 58.9 billion against 33.4 billion (up 76%). The May-on-May flatness is a base effect: May 2025 was the highest month of the first half of 2025. The abstract's claim is robust (January to July 2026 against the same months of 2025: 2.08 times; 12 months to July: 1.91 times). Smallest fix, title only: "Gold shipments outside the US were little changed in May from a year earlier." (13 words, 77 characters.) The body and its citation need no change; edit the citation note's "the basis for 'barely moved' in the title" to match. The real remedy is re-pointing the scatter to July.

### Item 3. After the cuts

PASS. No remaining sentence leans on removed text. Plate 01: 7 citations, all phrases present; no surplus citation. Plate 02: 1. Plate 03: 5; the history and superlative citations are gone. Plate 01's source line still names the trade balance, which the left panel draws.

### Item 4. Mechanics (by script)

PASS. All 29 citation phrases are exact substrings of their final prose. All sources are `derived` or `pipeline:statcan:<table>`; nothing cites `_pending/`. The plain and code versions of every surface are identical.

| Surface | Characters | Words | Sentences | Cap | Result |
|---|---|---|---|---|---|
| Tile line | 75 | 15 | 1 | 90 chars, 20 words | PASS |
| Abstract | 346 | 65 | 3 | 105 words, 5 sentences | PASS |
| Plate 01 title / body | 71 | 14 / 66 | 1 / 3 | title 22 words, 110 chars; body 110 words | PASS |
| Plate 02 title / body | 62 | 12 / 19 | 1 / 1 | same | PASS |
| Plate 03 title / body | 49 | 8 / 32 | 1 / 2 | same | PASS |
| Plate 04 title / body | 60 | 11 / 68 | 1 / 3 | same | PASS |

The style editor's hand counts all match. `checkLengthBudget` enforces hard caps and over-target warnings only; the 40-word and two-sentence minimums are not enforced, so plates 02 and 03 will not fail or warn.

### Overall

PASS for paste on numbers and mechanics. Two wording flags for the editor, D-1 (abstract quantifier) and D-2 (plate 02 title); D-2 matters more.

### Addendum: Gate 3 changes (plate 01 retitle, plate 02 hidden, plate 04 asOf)

Plate 01 new title, "The US export share fell in July even as gold shipments dropped.": PASS. Written into the draft body above with one title citation ("gold shipments dropped"). The old title had no citation entry.

- US share fell June to July on every basis: customs SA (charted) 68.26% to 66.57%; headline 69.39% to 66.35%; customs unadjusted 68.89% to 67.59%.
- Precious-metals exports fell June to July on both bases: customs unadjusted (the plate 03 series) 8,577.0 to 6,819.5, -20.5%; headline basis (v1566911383, fetched today) 10,071.1 to 8,752.1, -13.1%.
- "Even as" holds: the gold drop on its own pushed the US share up. Of the 1,757 fall, 1,396 was in shipments outside the US and 362 in shipments to the US. Applying only that change to June's charted totals lifts the share from 68.26% to about 69.4% (approximate: unadjusted metals on adjusted totals). Without precious metals the share fell 2.97 points against 1.69 with them (Gate 1). By-destination metals are not published on the headline basis, but with roughly nine-tenths of the metal going outside the US the direction is the same.
- Body support: the third sentence ("in July precious-metals exports fell by a fifth and the share dropped anyway") states the title's claim; "a fifth" is the charted-basis figure and stays in the body only. All 8 plate 01 citation phrases are exact substrings of title plus body (script). Title: 12 words, 64 characters, 1 sentence.
- The retitle removes the plate 01 half of D-1. The abstract quantifier ("as much" against "at least as much") remains an optional editor call.

Plate 02 hidden: D-2 is moot while the plate is off the page. Nothing in the tile line, the abstract or plates 01, 03 and 04 refers to plate 02, its scatter or its May figures. The abstract's "more than doubled" rests on the plate 03 series (total less US), not the frozen file. Plate numbering and any "four plates" wording are a build matter, not a prose one. If plate 02 returns, D-2 applies.

Plate 04 asOf "May 2026": PASS. PanelSectorPivot.astro hardcodes the 2025-05 and 2026-05 months and labels its columns MAY 2025 and MAY 2026; the body's July figures are labelled as July.
