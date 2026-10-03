# Monetary section redraft -- build unblock 2026-10-03

Writer draft. Nothing under `src/` was edited. Fact source: `claude-ref/build_unblock_2026-10-03/monetary_facts.md` only
(fact IDs like F4.2 refer to that pack). All values are 2026-10-01 closes unless stated; balance-sheet values are the
2026-09-30 weekly print (the latest in the pipeline; moved from the 2026-09-23 print at Gate 1, see the verdict at the
end of this file). Re-read as-of dates if another refresh lands before ship.

Character counts were counted by hand; confirm with the build's length gate.

---

## A. `src/data/sections.ts` -- `slug: "monetary"` block

### A1. Code comment + `updatedAt` (lines 455-457)

CURRENT
```ts
    // Jul 15 rate decision is the primary event; daily yields refresh
    // continuously but the policy stance is anchored to the rate decision.
    updatedAt: Date.UTC(2026, 6, 15, 13, 45),
```
NEW
```ts
    // Sep 2 rate decision is the primary event; daily yields refresh
    // continuously but the policy stance is anchored to the rate decision.
    updatedAt: Date.UTC(2026, 8, 2, 13, 45),
```

### A2. `heroKicker` (line 459)

CURRENT `heroKicker: "July rate decision",`
NEW `heroKicker: "September rate decision",`

### A3. `latestReleaseDateOverride` (line 467)

CURRENT `latestReleaseDateOverride: "Jul 15, 2026",`
NEW `latestReleaseDateOverride: "Sep 2, 2026",`

### A4. `tileLine` + `tileLineCitations` (lines 468-474)

CURRENT (81 characters)
```
BoC stayed at 2.25%; 2y GoCs are near 3.02% and the Canada-US spread is -117 bps.
```
NEW (78 characters, 17 words; polished at Gate 2)
```
BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point above.
```
Paste-ready:
```ts
    tileLine:
      "BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point above.",
    tileLineCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate 2.25% as of 2026-10-01, unchanged at the September 2 2026 FAD decision, via Valet V39079." },
      { phrase: "a seventh time", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 7, note: "Enumerated FAD holds since the Oct 29, 2025 cut: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10, Jul 15, Sep 2. Next decision Oct 28, 2026." },
      { phrase: "3.27%", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, October 1 2026 daily close = 3.27%." },
      { phrase: "a full point above", source: "derived", note: "GoC 2y 3.27% minus overnight target 2.25% = 1.02 pp = 102 bps, October 1 2026." },
    ],
```

### A5. `blurb` (lines 516-521) + `abstractCitations` (lines 522-530)

CURRENT body (340 characters)
```
On hold. The Bank of Canada has stayed at 2.25% through six straight decisions, still at the floor of its 2.25 to 3.25% neutral range, and now calls the rate appropriate. Markets see it the same way: the 2-year GoC yield sits at 3.02%, 77 bps above the overnight rate, while the Canada-US 2-year spread is still deeply negative at -117 bps.
```
NEW body (291 characters, 51 words, 3 sentences; polished at Gate 2)
```
On hold, with the pressure pointing up. The Bank of Canada has held at 2.25%, the floor of its neutral range, through seven straight decisions, but says upside risks to inflation have increased. Bond markets lean the same way: the 2-year GoC yield is 3.27%, 102 bps above the overnight rate.
```
Paste-ready:
```ts
    blurb: {
      kind: "last",
      date: "Oct 3, 2026",
      body:
        "On hold, with the pressure pointing up. The Bank of Canada has held at 2.25%, the floor of its neutral range, through seven straight decisions, but says upside risks to inflation have increased. Bond markets lean the same way: the 2-year GoC yield is 3.27%, 102 bps above the overnight rate.",
    },
    abstractCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate 2.25% as of 2026-10-01, unchanged at the September 2 2026 FAD decision, via Valet V39079." },
      { phrase: "seven straight decisions", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 7, note: "Enumerated FAD holds since the Oct 29, 2025 cut: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10, Jul 15, Sep 2. No decision between Sep 2 and Oct 3; next is Oct 28, 2026." },
      { phrase: "floor of its neutral range", source: "card:boc_mpr_neutral_range", note: "BoC nominal neutral range 2.25% to 3.25% (April 2026 MPR appendix, reaffirmed in the July 2026 MPR); the 2.25% target equals the lower bound." },
      { phrase: "upside risks to inflation have increased", source: "card:boc_fad_2026_09_02_inflation_risks", note: "BoC September 2 2026 press release, verbatim: 'However, the upside risks to inflation have increased, while new tariffs make growth prospects more uncertain.'" },
      { phrase: "2-year GoC yield is 3.27%", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, October 1 2026 daily close = 3.27%." },
      { phrase: "102 bps above the overnight rate", source: "derived", note: "GoC 2y 3.27% minus overnight target 2.25% = 1.02 pp = 102 bps, October 1 2026. Up from 77 bps on August 20 and 86 bps at the September 2 close." },
    ],
```
`blurb.date`: set to the redraft date (Oct 3). The old value (Aug 20) matched both its write date and its data date; if the
field is meant as the data as-of date, use "Oct 1, 2026" instead.

---

## B. `src/pages/monetary.astro` -- plates

All five plates are redrafted. None could be left untouched: each asserted a value or stance the fact pack shows has moved.

### Plate 1 (lines 38-61)

CURRENT
- asOf: `Jul 15, 2026 (rate decision)`
- title: `Six holds in, and the Bank now calls the rate appropriate.`
- body: "The Bank held the overnight rate at 2.25% on July 15, the sixth consecutive hold since the 25 bps cut on October 29, 2025 — and retired June's “dilemma” framing, calling the rate “appropriate to sustain the economic recovery and bring inflation back to the 2% target.” From the floor of the neutral range, the Bank still flags the same two risks — the Middle East war and US trade policy — but on the trade side, more businesses report finding ways to navigate the uncertainty."
- delta: `Sixth consecutive hold, Jul 15 decision`

NEW (paste-ready; `callout.value`, `unit`, `direction`, `source`, `chartKey`, `data` unchanged)
```ts
    asOf: "Sep 2, 2026 (rate decision)",
    title: "Seven holds in, the Bank now sees inflation risks tilting up.",
    interpretationHtml:
      "The Bank held at 2.25% on September 2, the seventh consecutive hold since the 25 bps cut on October 29, 2025, leaving the overnight rate at the floor of the neutral range. " +
      "Governing Council said “the upside risks to inflation have increased, while new tariffs make growth prospects more uncertain,” and that it “is prepared to adjust monetary policy as needed.” " +
      "The next decision, on October 28, comes with a new Monetary Policy Report.",
    callout: {
      value: "2.25%",
      unit: "BoC overnight rate target",
      delta: "Seventh consecutive hold, Sep 2 decision",
      direction: "neutral",
    },
    citations: [
      { phrase: "2.25% on September 2", source: "card:boc_fad_press_release_2026_09_02", note: "BoC September 2 2026 press release, verbatim: 'The Bank of Canada today held its target for the overnight rate at 2.25%, with the Bank Rate at 2.5% and the deposit rate at 2.20%.' Matches Valet V39079." },
      { phrase: "seventh consecutive hold", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 7, note: "Enumerated FAD holds since the Oct 29, 2025 cut: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10, Jul 15, Sep 2. Card carries the authoritative list; build fails if length drifts from expected_count." },
      { phrase: "Seven holds in", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 7, note: "Title restates the enumerated hold count from the card." },
      { phrase: "inflation risks tilting up", source: "card:boc_fad_2026_09_02_inflation_risks", note: "Title paraphrases the BoC September 2 2026 press release: 'However, the upside risks to inflation have increased, while new tariffs make growth prospects more uncertain.'" },
      { phrase: "25 bps cut on October 29, 2025", source: "pipeline:boc:V39079", note: "BoC rate table anchor row: October 29, 2025, target 2.25, change -0.25. Held at 2.25% at every decision since, through 2026-10-01 per Valet V39079." },
      { phrase: "the upside risks to inflation have increased, while new tariffs make growth prospects more uncertain", source: "card:boc_fad_2026_09_02_inflation_risks", note: "Verbatim, BoC September 2 2026 press release, final paragraph." },
      { phrase: "is prepared to adjust monetary policy as needed", source: "card:boc_fad_2026_09_02_guidance", note: "Verbatim, BoC September 2 2026 press release: 'Governing Council will assess the sustainability of the economic rebound and the outlook for inflation, and is prepared to adjust monetary policy as needed.'" },
      { phrase: "floor of the neutral range", source: "card:boc_mpr_neutral_range", note: "BoC stated nominal neutral range 2.25% to 3.25%; the 2.25% setting equals the lower bound." },
      { phrase: "on October 28, comes with a new Monetary Policy Report", source: "card:boc_fad_press_release_2026_09_02", note: "BoC September 2 2026 press release: 'The next scheduled date for announcing the overnight rate target is October 28, 2026. The Bank's next MPR will be released at the same time.' (Recorded in the card's notes; the card excerpt is the decision sentence.)" },
    ],
```

### Plate 2 (lines 68-86)

CURRENT
- asOf: `Jun 2026`
- title: `The BoC-Fed policy gap is narrowing from a generational depth.`
- body: "The BoC-Fed gap stands at -150 bps, narrowest since February 2025 and 25 bps off the -175 trough sustained from March through November 2025, when the BoC out-cut a Fed already a full point into its own easing. One December Fed cut has done the closing work; the BoC has held since October."

NEW (paste-ready; `source`, `chartKey`, `data` unchanged)
```ts
    asOf: "Oct 1, 2026",
    title: "The Fed is widening the policy gap while the Bank holds.",
    interpretationHtml:
      "The BoC-Fed policy gap stands at -175 bps, 25 bps wider than in August. " +
      "The Fed raised its target range to 3.75 to 4.00% on September 16, its first change since a cut in December 2025, while the BoC held at 2.25% for a seventh straight decision. " +
      "The Canada-US 2-year spread has widened too, to -151 bps on October 1; before this September it had not been that wide since March 2025.",
    citations: [
      { phrase: "-175 bps", source: "derived", note: "BoC target 2.25% minus top of the Fed target range 4.00% = -1.75 pp = -175 bps, as of 2026-10-01. Inputs: data/raw/overnight_rate_daily.csv and data/raw/fed_funds.csv (daily). Matches the panel series boc_fed_spread_monthly, whose latest point (2026-09-01) is -175 bps, up from -150 bps at 2026-08-01." },
      { phrase: "25 bps wider than in August", source: "derived", note: "Gap was -150 bps on 2026-08-20 (2.25% minus 3.75%); -175 minus -150 = 25 bps wider." },
      { phrase: "raised its target range to 3.75 to 4.00% on September 16", source: "card:fomc_statement_2026_09_16", note: "FOMC statement, September 16 2026, verbatim: 'The Committee decided to raise the target range for the federal funds rate by 1/4 percentage point to 3-3/4 to 4 percent'. Effective September 17 per the Federal Reserve open market operations table, which is where data/raw/fed_funds.csv steps from 3.75 to 4.00." },
      { phrase: "its first change since a cut in December 2025", source: "derived", note: "Federal Reserve open market operations table: the only 2026 row is the September 17 increase; the previous row is a 25 bps decrease effective December 11, 2025. data/raw/fed_funds.csv shows the same two steps." },
      { phrase: "held at 2.25% for a seventh straight decision", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 7, note: "Enumerated FAD holds since the Oct 29, 2025 cut to 2.25%: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10, Jul 15, Sep 2." },
      { phrase: "-151 bps on October 1", source: "derived", note: "Canada-US 2y spread, October 1 2026: GoC 2y 3.27% minus UST 2y 4.78% = -1.51 pp = -151 bps (data/processed/goc_ust_spread_2y.csv)." },
      { phrase: "before this September it had not been that wide since March 2025", source: "derived", note: "From data/processed/goc_ust_spread_2y.csv: before September 2026 the last reading at -151 bps or wider was 2025-03-17 (-151). Within the current episode the trough is -155 bps on 2026-09-28." },
    ],
```

### Plate 3 (lines 93-106)

CURRENT
- title: `The market still isn't pricing a near-term cut.`
- body: "The 2-year Government of Canada yield closed at 2.88% on July 13, up 6 bps on the latest close, and holds roughly 60 bps above the 2.25% overnight target. That gap leaves the market priced for the Bank to stay put — the implied path edges higher into late 2026, not lower — even as the Bank's own triggers point both ways."

NEW (paste-ready; `chartKey`, `data` unchanged; `source` line replaced at Gate 2)
```ts
    title: "The 2-year yield has pulled a full point above the policy rate.",
    interpretationHtml:
      "The 2-year GoC yield closed at 3.27% on October 1, 102 bps above the 2.25% overnight target: a bond market leaning toward a higher policy rate. " +
      "Before this September the gap had not been that wide since October 2022, during the hiking cycle; it was 17 bps on October 30, 2025, the day after the Bank's last cut. " +
      "The yield reached 3.40% on September 23, its highest close since July 2024.",
    source: "Bank of Canada Valet (2-year benchmark yield; overnight rate target).",
    citations: [
      { phrase: "3.27% on October 1", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, daily close October 1 2026 = 3.27%, via BoC Valet BD.CDN.2YR.DQ.YLD." },
      { phrase: "a full point above the policy rate", source: "derived", note: "Title: 3.27% (GoC 2y) minus 2.25% (overnight target) = 1.02 pp, October 1 2026." },
      { phrase: "102 bps above", source: "derived", note: "3.27% (GoC 2y) minus 2.25% (overnight target) = 1.02 pp = 102 bps, October 1 2026." },
      { phrase: "2.25% overnight target", source: "pipeline:boc:V39079", note: "BoC overnight target rate, 2.25% as of 2026-10-01, via Valet V39079." },
      { phrase: "had not been that wide since October 2022", source: "derived", note: "From data/raw/yield_2yr.csv and data/raw/overnight_rate_daily.csv: before September 2026, the last day the GoC 2y sat 102 bps or more above the overnight target was 2022-10-20 (103 bps). Peak of the current episode: 115 bps on 2026-09-23." },
      { phrase: "17 bps on October 30, 2025", source: "derived", note: "GoC 2y minus overnight target on 2025-10-30, the first day after the October 29, 2025 cut took effect = 17 bps." },
      { phrase: "3.40% on September 23", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, daily close September 23 2026 = 3.40%." },
      { phrase: "its highest close since July 2024", source: "derived", note: "From data/raw/yield_2yr.csv: 3.40% on 2026-09-23 is the highest close since 2024-07-31 (3.46%)." },
    ],
```

### Plate 4 (lines 113-133)

CURRENT
- title: `Government bonds anchor the post-QT balance sheet.`
- body: "The asset side has settled into a shape defined by what's left of the pandemic-era bond-purchase programme. Government of Canada bonds account for $146.0 billion of $220.0 billion in total assets — about 66% — easing lower as the portfolio matures while the total holds steady. Quantitative tightening is complete; repos run in a roughly $15 to 40 billion range as the operating margin of the floor system."
- callout: value `66%`, delta `$146.0 bn of $220.0 bn total`

NEW (paste-ready; `callout.unit`, `direction`, `source`, `chartKey`, `data` unchanged)
```ts
    title: "Repos, not bonds, are now moving the balance sheet.",
    interpretationHtml:
      "Repos rose $18.4 billion to $65.9 billion in the two weeks to September 30, nearly all of the $18.6 billion rise in total assets. " +
      "Government of Canada bonds are still the largest asset, at $135.6 billion of $242.6 billion in total, about 56%, and have held near that level since a $9.0 billion step down in the week to September 2.",
    callout: {
      value: "56%",
      unit: "GoC bonds, share of BoC assets",
      delta: "$135.6 bn of $242.6 bn total",
      direction: "neutral",
    },
    citations: [
      { phrase: "$135.6 billion of $242.6 billion in total", source: "pipeline:boc:boc_goc_bonds", note: "BoC weekly statement, September 30 2026 vintage (latest in pipeline): GoC bonds (V36613) = $135.645bn; total assets (V36610) = $242.555bn." },
      { phrase: "about 56%", source: "derived", note: "135.645 / 242.555 = 55.9%, rounds to 56%." },
      { phrase: "$9.0 billion step down in the week to September 2", source: "pipeline:boc:boc_goc_bonds", note: "GoC bonds fell from $145.700bn (Aug 26) to $136.660bn (Sep 2) = -$9.04bn; then $136.187bn (Sep 9), $135.757bn (Sep 16), $135.777bn (Sep 23) and $135.645bn (Sep 30)." },
      { phrase: "rose $18.4 billion to $65.9 billion in the two weeks to September 30", source: "pipeline:boc:boc_repos", note: "BoC repos (V44201362): $47.482bn (Sep 16) to $59.407bn (Sep 23) to $65.929bn (Sep 30) = +$18.447bn over two weeks." },
      { phrase: "$18.6 billion rise in total assets", source: "derived", note: "Total assets $224.001bn (Sep 16) to $242.555bn (Sep 30) = +$18.554bn, rounds to $18.6bn. Repos account for $18.447bn of it (99%)." },
    ],
```

### Plate 5 (lines 140-163)

CURRENT
- title: `The overnight rate is now the only active policy lever.`
- body: "Banknotes carry $123.9 billion of $220.0 billion in total liabilities — about 56% — drifting up only $30 billion over six years as a passive function of currency demand. Settlement balances sit at $64.3 billion, inside the $50 to 70 billion operating range and a small fraction of the near-$400 billion peak in early 2021. Reverse repos are at zero — none of it is doing policy work."
- callout: value `$64.3 bn`, delta `Inside Jan-2025 $50-70 bn range`

NEW (paste-ready; `callout.unit`, `direction`, `source`, `chartKey`, `data` unchanged)
```ts
    title: "Settlement balances have jumped above the Bank's operating range.",
    interpretationHtml:
      "Settlement balances rose $20.4 billion to $83.4 billion in the two weeks to September 30, above the $50 to 70 billion operating range that held them at $63.1 billion on September 16. " +
      "The Canadian Overnight Repo Rate Average, a measure of overnight funding costs, has been 3 to 6 bps above the 2.25% target every day since September 1, after sitting exactly on target in late August.",
    callout: {
      value: "$83.4 bn",
      unit: "Settlement balances",
      delta: "Above Jan-2025 $50-70 bn range",
      direction: "neutral",
    },
    citations: [
      { phrase: "rose $20.4 billion to $83.4 billion in the two weeks to September 30", source: "pipeline:boc:boc_settlement_balances", note: "Settlement balances (V36636): $63.059bn (Sep 16) to $78.082bn (Sep 23) to $83.440bn (Sep 30) = +$20.381bn over two weeks. September 30 is the latest weekly print in the pipeline." },
      { phrase: "$50 to 70 billion operating range", source: "card:boc_floor_system_operating_range", note: "Range set in Deputy Governor Gravelle's January 16 2025 speech ('we have revised the range upward to between $50 billion and $70 billion'). Still current: Gravelle, September 29 2026, 'Repo markets and monetary policy implementation', verbatim: 'our best estimate of steady-state demand for reserves, which remains $50 billion to $70 billion. But keeping the supply of reserves within this range is not an objective in itself.'" },
      { phrase: "at $63.1 billion on September 16", source: "pipeline:boc:boc_settlement_balances", note: "Settlement balances, September 16 2026 weekly print = $63.059bn, inside the $50-70bn range." },
      { phrase: "3 to 6 bps above the 2.25% target every day since September 1", source: "derived", note: "CORRA minus overnight target, data/processed/corra_overnight_spread_bps.csv (panel-4.extras7), current to 2026-10-01: 3 to 6 bps above target every day from 2026-09-01; 5 bps on 2026-10-01 (CORRA 2.30%), 6 bps on 2026-09-29. Cite the processed spread file, not data/raw/corra_daily.csv (stale)." },
      { phrase: "exactly on target in late August", source: "derived", note: "CORRA minus target = 0 bps on every day from 2026-08-20 through 2026-08-28 (same processed file)." },
    ],
```

---

## Flags for the dispatcher

1. **Fed hike has no source card (plate 2).** The September 17 increase to 3.75-4.00% is verified in the pack against the
   repo file and the Federal Reserve's rate table (F5.1), but the pack says a card is needed before the hike is named in
   prose, and `fomc_target_rate` is stale. Plate 2 names the hike and cites it `derived`. Either create the card and
   repoint that citation, or cut the clause "the Fed raised its target range to 3.75 to 4.00% on September 17, its first
   change since a cut in December 2025, while" (the -175 bps gap then stands alone).
2. **Plate 2 chart will lag its prose.** The panel series `boc_fed_spread_monthly` stops at 2026-08-01 with -150 bps, so
   the chart does not yet show the -175 bps the prose states.
3. **Plate 3 `source` line and chart.** The source line still reads "MPR market-implied curve, latest vintage" and the
   chart may draw an implied path from futures data last fetched 2026-06-08. The new prose makes no implied-path claim.
   Chart-builder should check whether a stale implied curve is still drawn.
4. **Interpretive sentences (writer's read, not Bank statements).** "Bond markets lean the same way" (abstract), "a bond
   market leaning toward a higher policy rate, not a lower one" (plate 3), "an adjustment made to contain inflation would
   be a move up" (plate 1), and the opener "with the pressure pointing up". None says the Bank has a tightening bias or
   that markets price a hike; the hard fact under each is the 102 bps gap or the verbatim statement.
5. **Balance-sheet vintage (plates 4, 5).** Prose uses the September 23 prints, the latest in the pipeline. The
   September 30 print exists on Valet (repos $65.9bn, settlement balances $83.4bn, total assets $242.6bn) and will
   outdate these numbers when the pipeline picks it up. No cause is asserted for the repo and settlement-balance jump.
6. **Cut for lack of verified data (plate 5).** The banknotes sentence ($123.9bn of $220.0bn, about 56%, $30bn drift)
   and "Reverse repos are at zero" were dropped: the pack has no current banknote, total-liability or reverse-repo values.
   The old title ("The overnight rate is now the only active policy lever.") was replaced because settlement balances are
   no longer inside the operating range. Also cut from plate 4: "Quantitative tightening is complete" and the "$15 to 40
   billion" repo range (now false). `card:boc_qt_end_2025_01` loses its only citation on this page; the orphan check may
   report it.
7. **Carry-over claim.** "near-$400 billion peak in early 2021" (plate 5) is retained from the prior copy with its
   existing citation; it is historical and not in the pack.
8. **CORRA citation location.** The CORRA spread is panel-4 data (extras7) but is cited in plate 5 prose, as `derived`.
9. **Superlative wording.** The 2-year spread and the 2-year-over-target gap were both wider on days in late September
   than on October 1, so the prose says "before this September it had not been that wide since ..." rather than
   "widest since ...".
10. **`callout.direction`** left as "neutral" on plates 4 and 5; change if the component supports an "up" state.

## NEW CLAIMS INTRODUCED (all re-enter Gate 1)

Tile line: seventh hold; 2y at 3.27%; a full point above the policy rate.
Abstract: seven straight decisions; floor of the neutral range; upside risks to inflation have increased; prepared to
adjust policy as needed; 2y 3.27%; 102 bps above the overnight rate.
Plate 1: 2.25% on September 2; seventh consecutive hold; both verbatim quotes; next decision October 28 with an MPR.
Plate 2: -175 bps; 25 bps wider than in August; Fed range 3.75 to 4.00% on September 17; first Fed change since a
December 2025 cut; seventh straight hold; 2-year spread -151 bps on October 1; not that wide before this September since
March 2025.
Plate 3: 3.27% on October 1; 102 bps; not that wide before this September since October 2022; 17 bps on October 30, 2025;
up 16 bps since the September 2 decision; 3.40% on September 23; highest close since July 2024.
Plate 4: $135.8bn of $236.0bn; about 58%; $9.0bn step down in the week to September 2; repos +$11.9bn to $59.4bn in the
week to September 23; total assets +$12.0bn that week.
Plate 5: settlement balances +$15.0bn to $78.1bn in the week to September 23; $63.1bn a week earlier; above the $50 to 70
billion range; CORRA 3 to 6 bps above target every day since September 1; on target in late August.
(Writer's list as drafted. Plates 2, 4 and 5 were corrected at Gate 1; see below for the current values.)

---

## Gate 1 verdict (fact-check, 2026-10-03)

Checked against: repo series in the working tree (today's refresh; `data/site/panel_data/monetary.json` generated
2026-10-03T16:51Z), BoC Valet (V39079, BD.CDN.2YR.DQ.YLD, AVG.INTWO, V36636, V36610, V36613, V44201362; every value
matches the repo), the BoC September 2 2026 press release and key-interest-rate table (raw HTML, string-matched), the
FOMC statement of September 16 2026 and the Federal Reserve open market operations table (raw HTML), and
`editorial/source_cards/registry.yaml`.

### Verdict per surface

| Surface | Verdict | Note |
|---|---|---|
| Stamps (updatedAt, heroKicker, latestReleaseDateOverride, plate 1 asOf) | PASS | Sep 2, 2026 decision; 13:45 UTC = 9:45 ET. |
| Tile line | PASS | 2.25%, seventh hold, 3.27%, 102 bps all verified. |
| Section abstract | PASS with flag | Numbers and both quotations verified; see open flag 1 on the opener. |
| Plate 1 | PASS with flag | Both quotations verbatim; October 28 with MPR verbatim; see open flag 2. |
| Plate 2 | PASS after correction | Fed date corrected, card added; chart now agrees with prose. |
| Plate 3 | PASS with flag | All values and since-comparisons verified on the full daily series; see open flags 3 and 4. |
| Plate 4 | PASS after correction | Moved to the September 30 print. |
| Plate 5 | PASS after correction | Moved to the September 30 print; 2021 peak verified; see open flags 5 to 7. |

Overall: PASS, conditional on the corrections below (already applied in this file).

### Independent checks

- Seven holds, enumerated from the Bank's own rate table rather than the card: Dec 10 2025, Jan 28, Mar 18, Apr 29,
  Jun 10, Jul 15, Sep 2 2026, each "2.25, ---"; anchor row Oct 29 2025 "2.25, -0.25". Count = 7. The card enumeration
  has 7 entries, so every `expected_count: 7` resolves.
- BoC quotations: the decision sentence, the risk sentence, the guidance sentence and the next-date note are all present
  verbatim in the September 2 release. The word "appropriate" does not appear in it.
- 2-year yield minus overnight target: 102 bps on Oct 1; at or above 102 bps on 13 trading days in September, the first being Sep 10; peak 115 bps on
  Sep 23; last earlier reading that wide 2022-10-20 (103 bps). "Before this September ... since October 2022" holds,
  including the late-September days.
- Canada-US 2-year spread: -151 bps on Oct 1; -155 on Sep 28 and -152 on Sep 29; last earlier reading that wide
  2025-03-17 (-151). "Before this September ... since March 2025" holds.
- 3.40% on Sep 23 is the highest 2-year close since 2024-07-31 (3.46%). 17 bps on 2025-10-30 verified. 3.27 minus 3.11
  (Sep 2 close) = 16 bps.
- CORRA minus target: 3 to 6 bps on every day from Sep 1 (4) to Oct 1 (5); 0 bps on Aug 20 through Aug 28.
- Settlement balances peak: $394.126bn on 2021-03-03 (the carried-over plate 5 claim). Verified.
- Citation mechanics: every `phrase` is an exact substring of its title or body; every `source` is `pipeline:boc:<key>`
  with a key already used on the site, `card:<id>` present in the registry at Tier A, or `derived`; no citable token is
  left uncovered under the tokenizer in `scripts/check_citation_coverage.mjs`. Checked with a re-implementation of the
  gate's rules against this file, not by running the build (the copy is not in `src/` yet).
- Length budgets (`scripts/source_audit.mjs`): no hard-cap overruns. Soft-target warnings only, which do not block the
  build: tile line 18 words (target 16; 81 characters against a 90 cap); plate bodies 99, 85, 97, 72 and 80 words
  (target 70, hard cap 110). Abstract 60 words, 3 sentences, inside target.

### Corrections applied

1. Plate 2, Fed date: "on September 17" changed to "on September 16". The FOMC statement is dated September 16, 2026;
   September 17 is the effective date in the Federal Reserve's table and the day the repo series steps. The draft dates
   Bank of Canada moves by announcement day (October 29, not October 30), so the Fed move now follows the same
   convention. Citation phrase updated to match.
2. Plate 2, Fed citation: `derived` replaced with `card:fomc_statement_2026_09_16`. New card added to
   `editorial/source_cards/registry.yaml` after `fomc_statement_2025_12_17`, Tier A, excerpt fetched today:
   "The Committee decided to raise the target range for the federal funds rate by 1/4 percentage point to 3-3/4 to 4
   percent". Registry parses; 43 cards, no duplicate ids.
3. Plate 2, citation notes: the "-175 bps" note said the panel series stops at August with -150 bps. Today's refresh
   added the September point at -175 bps; note corrected. The "first change since" note now cites the Fed table.
4. Plate 4, vintage: the pipeline now carries the September 30 weekly print, so the September 23 figures were stale
   against the chart. Was: "$135.8 billion of $236.0 billion in total, about 58%" and "rose $11.9 billion in the week to
   September 23 to $59.4 billion and account for nearly all of that week's $12.0 billion rise in total assets". Now:
   "$135.6 billion of $242.6 billion in total, about 56%" and "rose $18.4 billion in the two weeks to September 30 to
   $65.9 billion and account for nearly all of the $18.6 billion rise in total assets over those weeks". Callout now
   56%, "$135.6 bn of $242.6 bn total". Citations and notes updated. Title and take unchanged.
5. Plate 5, vintage: same reason. Was: "rose $15.0 billion in the week to September 23 to $78.1 billion ... that held
   them a week earlier at $63.1 billion". Now: "rose $20.4 billion in the two weeks to September 30 to $83.4 billion ...
   that held them on September 16 at $63.1 billion". Callout now "$83.4 bn". Citations and notes updated. Title and
   take unchanged.
6. Plate 5, carried-over claim: the 2021 peak note no longer says "not re-verified"; it is verified.
7. Header of this file: balance-sheet as-of date updated to 2026-09-30.

Corrections 4 and 5 reword two sentences (one week became two weeks). If the dispatcher prefers the writer's original
one-week sentences, the originals are quoted above; the September 23 statements remain true as dated, but the callouts
would then disagree with the chart's latest point.

### Writer flags now closed

- Writer flag 1 (no Fed card): closed by corrections 1 and 2. The cut-the-clause fallback is not needed.
- Writer flag 2 (plate 2 chart lags): closed. The chart (`Panel7PolicyRateDivergence.astro`) reads
  `data/raw/overnight_rate.csv` and `data/raw/fed_funds.csv` directly; its latest joined month is September 2026 at
  -175 bps. Prose and chart agree. No wording fix needed.
- Writer flag 3 (plate 3 implied path): the chart (`Panel2MarketPath.astro`) draws only the 2-year yield and the
  overnight rate. No implied path is drawn, so prose and chart agree. Only the `source` line is wrong; see open flag 4.
- Writer flag 5 (balance-sheet vintage): closed by corrections 4 and 5.
- Writer flag 7 (2021 peak): verified; keep.

### Open flags (framing; not rewritten)

1. Abstract opener "with the pressure pointing up" and "Bond markets lean the same way". Defensible: the Bank said
   upside inflation risks have increased, and a 2-year yield 102 bps over the policy rate is conventionally read as
   expecting a higher rate. Two cautions for the editor. The Bank's sentence pairs the inflation risk with "new tariffs
   make growth prospects more uncertain", which the abstract leaves out; and the gap is 13 bps off its September 23 peak
   after a 10 bps fall in the yield on the latest close. Neither makes the sentence false. Recommend keeping.
2. Plate 1, "The policy rate sits at the floor of the neutral range, so an adjustment made to contain inflation would be
   a move up." The second half is true by definition; it does not follow from the first half, because a move to contain
   inflation is a rise wherever the rate sits. Recommended fix: replace ", so" with a semicolon, or cut the sentence.
3. Plate 3, "up 16 bps since the September 2 decision" measures from the close on decision day. Ten of the 26 bps since
   the September 1 close came on decision day itself. True under the close-of-day reading; a reader could take it as
   "since before the announcement". Recommended fix if the editor wants it tight: "up 16 bps since the close on
   September 2". The plate 3 sentence "a bond market leaning toward a higher policy rate, not a lower one" is a
   conventional reading and passes; there is no current futures data behind it, and the draft rightly does not say a
   rise is priced.
4. Plate 3 `source` line still reads "BoC Valet (rates); MPR market-implied curve, latest vintage." No implied curve is
   on the chart or in the prose. Recommended: `source: "BoC Valet (rates)."` Separately, the plate 2 `source` line
   (unchanged by the draft) says "FRED DFF (fed funds effective ...)" and "Canada-US 2y spread derived in chart"; the
   chart plots the top of the Fed target range and does not draw the 2-year spread. The third sentence of the plate 2
   body (2-year spread at -151 bps) is therefore not visible on that plate's chart. Not false; flagged for surface fit.
5. Plate 5, "a small fraction of the near-$400 billion peak": balances are now 21% of the peak (they were 16% when the
   phrase was written). Still defensible; "about a fifth of" is the verifiable form.
6. Plate 5 title and callout treat $50 to 70 billion as the Bank's current operating range. The source is a January
   2025 speech (excerpt re-fetched today and still on the page). I did not search for a later revision of the range.
   Balances were also above $70 billion on August 19 (70.4) and August 26 (74.2) before returning inside it, so this is
   a second crossing, not the first. "Jumped above" still describes the move from 63.1 to 83.4.
7. Plate 5, "exactly on target in late August": true for August 20 through 28; August 31 set 2 bps above. Passes; the
   tight form is "through August 28".
8. `blurb.date`: "Oct 3, 2026" is the redraft date; the data in the abstract is as of October 1. Dispatcher's choice,
   as the writer noted.

### Outside this draft (not fixed)

- `fomc_target_rate` card still records 3.50-3.75% from the April 29 statement; it is cited on `src/pages/policy.astro`
  plate 7 and is now out of date.
- `fomc_statement_2025_12_17` card: its URL returns 404, and the Federal Reserve's table dates that cut December 11
  2025 (effective), with the statement at `monetary20251210a.htm` dated December 10. The card id, date and URL look
  wrong. It is cited only by the boc-fed-divergence research sidecar.
- The four `expected_count: 6` citations in `src/` listed in the fact pack fail the build until this draft is pasted.
- No derived-slot queue entry was added for the 2-year-minus-overnight gap or the daily Canada-US 2-year spread, since
  a pending entry stops the build. Both were computed ad hoc again today; they should be materialized after the deploy.
- `card:boc_qt_end_2025_01` loses its citation on this page (writer flag 6); it remains cited on the policy page per
  its `cited_in`.

(The Gate 1 section above describes the text as it stood before Gate 2. The body of this file now holds the Gate 2
text; quotations of prose in the Gate 1 section are the pre-polish wording.)

---

## Gate 2 verdict (style polish, 2026-10-03)

Voice and concision only. No number, date or quotation was changed or added. Three cited phrases were cut with their
citation entries; four citation phrases were reworded and their `phrase` strings updated to stay exact substrings.
Counts below are by hand (no script was run); characters include spaces and terminal punctuation. Confirm with the
build's length gate on paste.

Overall: PASS after polish. Both fact-checker flags resolved. Two rewordings and four cuts are marked for the writer
and for the Gate 1 delta check (see "Flags").

### Changes (before and after)

**Tile line** (mechanical)
- Before: "BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point above it."
- After: "BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point above."
- Citation phrase "a full point above it" updated to "a full point above".

**Abstract** (one mechanical fix, one marked cut)
- Before: "The Bank of Canada has held at 2.25% through seven straight decisions, the floor of its neutral range, but says
  upside risks to inflation have increased and it is prepared to adjust policy as needed."
- After: "The Bank of Canada has held at 2.25%, the floor of its neutral range, through seven straight decisions, but
  says upside risks to inflation have increased."
- Why: "the floor of its neutral range" was attached to "decisions" instead of to 2.25% (misplaced modifier). MARKED:
  "and it is prepared to adjust policy as needed" cut as a direction-neutral formula that does not explain the take;
  its citation entry (`card:boc_fad_2026_09_02_guidance`) removed from `abstractCitations`. The verbatim quotation
  stays on plate 1. First and third sentences unchanged.

**Plate 1 body** (fact-checker flag 2 resolved by cut)
- Before, sentence 1: "The Bank held the overnight rate at 2.25% on September 2, the seventh consecutive hold since the
  25 bps cut on October 29, 2025."
- After, sentence 1: "The Bank held at 2.25% on September 2, the seventh consecutive hold since the 25 bps cut on
  October 29, 2025, leaving the overnight rate at the floor of the neutral range."
- Cut: "The rate has not moved, but the risk assessment has:" (balanced setup line; the quotations that follow say it).
- Cut: "The policy rate sits at the floor of the neutral range, so an adjustment made to contain inflation would be a
  move up." The neutral-range fact moved into sentence 1; the second half was true by definition and is gone. No claim
  added. Citation phrase "floor of the neutral range" still matches.
- Title, quotations and final sentence unchanged.

**Plate 2 title** (MARKED, changes construction)
- Before: "The Fed, not the Bank, is widening the policy gap."
- After: "The Fed is widening the policy gap while the Bank holds."
- Why: plates 2 and 4 both used the "X, not Y," construction on one page; plate 4 keeps it.

**Plate 2 body**
- Cut: "All of the widening came from the US side:" (restates the title; the sentence it introduced makes the point).
- Before: "Shorter-term yields moved the same way, with the Canada-US 2-year spread at -151 bps on October 1; ..."
- After: "The Canada-US 2-year spread has widened too, to -151 bps on October 1; ..."
- Why: "shorter-term" had no referent (the comparison is with overnight rates). MARKED for Gate 1: "has widened too"
  replaces "moved the same way"; same claim, different words.

**Plate 3 body** (MARKED, restructured) and `source`
- Before: four sentences; the read came third ("A 2-year rate that far above the overnight rate is a bond market
  leaning toward a higher policy rate, not a lower one.") and the first sentence paraphrased the title.
- After, sentence 1: "The 2-year GoC yield closed at 3.27% on October 1, 102 bps above the 2.25% overnight target: a bond
  market leaning toward a higher policy rate."
- "Government of Canada" shortened to "GoC" (spoken acronym). ", not a lower one" cut (balanced tail).
- Cut: "is up 16 bps since the September 2 decision and"; citation entry removed. This also disposes of fact-checker
  open flag 3 (the ambiguous start point). The September 23 high stays as its own sentence.
- `source` (fact-checker flag 4 resolved): now "Bank of Canada Valet (2-year benchmark yield; overnight rate target)."
  This follows plate 2's form ("Bank of Canada Valet (overnight rate target, monthly); ..."); the implied-curve
  reference is gone. The line is now in the paste-ready block.

**Plate 4 body** (MARKED, sentence order swapped)
- Before: bonds sentence first, then "The movement is in repos, which rose $18.4 billion in the two weeks to September
  30 to $65.9 billion and account for nearly all of the $18.6 billion rise in total assets over those weeks."
- After: "Repos rose $18.4 billion to $65.9 billion in the two weeks to September 30, nearly all of the $18.6 billion
  rise in total assets." first, then the bonds sentence unchanged.
- Why: the claim leads; "The movement is in repos" and "over those weeks" were surplus. Repo citation phrase updated.

**Plate 5 body**
- Before, sentence 1: "... rose $20.4 billion in the two weeks to September 30 to $83.4 billion, above the $50 to 70
  billion operating range that held them on September 16 at $63.1 billion."
- After, sentence 1: "... rose $20.4 billion to $83.4 billion in the two weeks to September 30, above the $50 to 70
  billion operating range that held them at $63.1 billion on September 16." Two citation phrases updated.
- Before, sentence 2: "Overnight funding has also run firm: the Canadian Overnight Repo Rate Average has set 3 to 6 bps
  above ..."
- After, sentence 2: "The Canadian Overnight Repo Rate Average, a measure of overnight funding costs, has been 3 to 6
  bps above ..." Why: "run firm" and "has set" are desk shorthand. MARKED for Gate 1: the appositive is a plain-English
  gloss built from the writer's own "overnight funding" framing.
- MARKED cut: "Balances remain a small fraction of the near-$400 billion peak in early 2021." At 21% of the peak
  "small fraction" is loose (fact-checker open flag 5), and the cut brings the body to target. Citation entry removed.
  If the writer wants the scale line back, the verified form is "about a fifth of the near-$400 billion peak".

Unchanged: plate 1, 3, 4 and 5 titles; all callouts; all stamps.

### Final counts

| Surface | Characters | Words | Sentences | Limit | Before |
|---|---|---|---|---|---|
| Tile line | 78 | 17 | 1 | 90 chars; 16-word target, 20-word hard cap | 81 chars, 18 words |
| Abstract body | 291 | 51 | 3 | 340 chars; 45-75 word target | 336 chars, 60 words |
| Plate 1 title | 61 | 11 | 1 | 110 chars, 14-word target | same |
| Plate 2 title | 56 | 11 | 1 | as above | 50 chars, 10 words |
| Plate 3 title | 63 | 12 | 1 | as above | same |
| Plate 4 title | 51 | 9 | 1 | as above | same |
| Plate 5 title | 65 | 9 | 1 | as above | same |
| Plate 1 body | 436 | 74 | 3 | 70-word target, 110-word hard cap | 99 words |
| Plate 2 body | 382 | 72 | 3 | as above | 85 words |
| Plate 3 body | 387 | 71 | 3 | as above | 97 words |
| Plate 4 body | 331 | 61 | 2 | as above | 72 words |
| Plate 5 body | 382 | 67 | 2 | as above | 80 words |

`scripts/source_audit.mjs` limits (`LENGTH_BUDGETS`): plate blurb 40-70 words soft, 110 words and 6 sentences hard, no
character cap; plate title 14 words soft, 22 words and 110 characters hard; tile line 16 words soft, 20 words and 90
characters hard; section abstract 45-75 words soft, 105 words and 5 sentences hard. No hard cap is exceeded. Soft-target
warnings will still print for the tile line (17 words) and plates 1 to 3 (74, 72, 71 words); they do not block the
build. Plate 1 cannot reach 70 without cutting into a verbatim quotation (29 of its 74 words) or dropping the next
decision date. The tile line cannot reach 16 without losing "but" or "full". Every body is shorter than it was.

### Checklist (editorial/writing-style.md)

- Section 4.1 plate titles: PASS x5. Sentence case, terminal period, no colon or semicolon, each names a finding.
- Section 4.1b / 4.1i abstract: PASS. Take ("On hold, with the pressure pointing up."), mechanism (held at the floor
  of neutral through seven decisions while the Bank says upside inflation risks have increased), landing (the 2-year
  yield 102 bps above the overnight rate). Answers the header question; two anchoring numbers plus the hold count.
- Section 4.1f-2 stand-alone: PASS for tile line, abstract and all five titles. Plate 5 body passes narrowly: its first
  sentence is the title with numbers, and the second beat is the overnight repo rate, not a cause (the fact pack
  asserts none).
- Title repetition: plate 3 FAIL before polish, PASS after (first sentence now carries the read).
- Section 4.1 source attribution in prose: PASS. "Governing Council said" and "says" attribute a statement, not data.
- Institutional paraphrase as our read: PASS. Plate 1 quotes verbatim with attribution; the abstract attributes.
- Section 4.1h superlatives: the "before this September it had not been that wide since ..." form (plates 2, 3) is not
  the standard "widest since" form. Left as written: the writer's flag 9 and Gate 1 show the standard form would be
  false, because late-September readings were wider.
- Section 4.1f-3 deep-dive links: PASS, none.
- Section 6 acronyms: PASS. Canadian Overnight Repo Rate Average and Monetary Policy Report spelled out; BoC, GoC, Fed
  are spoken. "Repos" is unglossed, as in the copy it replaces.
- Banned vocabulary ("corridor", the L-B compound, clipped words, "per cent", math symbols): PASS, none.
- Signpost, method or flourish sentences: three cut (plates 1, 2, 4), one tail cut (plate 3).
- Section 4.1e slot binding (flag, not fail): the `pipeline:boc:*` citations use literal `phrase` strings and will
  need hand updates at each refresh.

### Flags

1. For the Gate 1 delta check: two rewordings, "has widened too" (plate 2) and "a measure of overnight funding costs"
   (plate 5). Neither is meant as a new claim.
2. For the writer: four cuts of verified material, each reversible from the "before" text above: the guidance clause
   in the abstract, the 16 bps clause in plate 3, the 2021-peak sentence in plate 5, and the "move up" sentence in
   plate 1. With plate 5's cut, `pipeline:boc:boc_settlement_balances` is still cited twice on that plate.
3. For Gate 3: plate 2's third sentence (the 2-year spread) is not drawn on that plate's chart, and plate 2's `source`
   line names a series the chart does not plot (fact-checker open flag 4, second half). Not touched here.
4. Open from Gate 1 and unchanged by this pass: the abstract leaves out the tariff half of the Bank's sentence;
   `blurb.date`; the age of the $50 to 70 billion range (plate 5 title and callout).

---

## Gate 1 delta verdict (fact-check of Gate 2 changes, 2026-10-03)

Scope: only what Gate 2 changed, plus the plate 5 range and a re-read of `data/site/panel_data/monetary.json`
(generated 2026-10-03T17:03Z, later than the file Gate 1 read). Nothing under `src/` was edited.

Overall: PASS, with one framing flag on plate 5 for the writer and editor.

| Item | Verdict | Note |
|---|---|---|
| 1. Reworded sentences | PASS | See below. |
| 2. Dependencies and orphans after cuts | PASS | No remaining sentence leans on a cut one; no citation entry without its phrase. |
| 3. $50 to 70 billion range | PASS, still current | Reaffirmed by the Bank on September 29, 2026. Citation note added. Framing flag below. |
| 4. Script checks | PASS | All 44 citation phrases are exact substrings; all five hold-count citations carry `expected_count: 7`. |
| 5. Values against panel data | PASS | Every quoted value matches at its stated as-of date. |

### Item 1, reworded text

- Plate 2 "has widened too, to -151 bps on October 1": the Canada-US 2-year spread was -124 to -133 bps in the last
  week of August, -132 bps on September 15 (the day before the Fed decision) and -151 bps on October 1. It widened,
  as the policy gap did. Supported.
- Plate 2 title "The Fed is widening the policy gap while the Bank holds.": the gap went from -150 to -175 bps in
  September; the whole move is the Fed's September 16 increase; the Bank held on September 2. Direction matches the
  data. Supported.
- Plate 5 "a measure of overnight funding costs": the Canadian Overnight Repo Rate Average measures the cost of
  overnight general-collateral funding in Canadian dollars. Fair gloss, no new claim.
- Plate 1 "leaving the overnight rate at the floor of the neutral range": 2.25% equals the lower bound of the Bank's
  2.25 to 3.25% range. Supported. The cut "move up" sentence leaves nothing behind that depended on it.
- Tile line: 3.27 minus 2.25 = 1.02 points = 102 bps on October 1. "A full point above" is supported; with "it"
  dropped the referent is still the 2.25% in the same sentence.
- Abstract: 2.25%, seven decisions, the floor of the range, the Bank's risk sentence and the 102 bps gap all stand.
  The moved modifier now attaches to 2.25%, which is what the source card supports.
- Plate 3 first sentence and plate 4 reordering: same numbers, same dates, no change in meaning. In plate 4 "nearly
  all of the $18.6 billion rise in total assets" now takes its two-week window from the first clause; 18.447 of
  18.554 is 99%.

### Item 2, after the cuts

- Abstract: the guidance citation is gone with its clause; the guidance card is still cited on plate 1.
- Plate 3: "the gap" in the second sentence refers to the 102 bps in the first. The 16 bps citation is gone.
- Plate 5: the 2021-peak sentence and its citation are gone; the callout does not depend on it.
- Stale text in this file only (not reader copy): writer flag 4 quotes two phrases that were cut ("not a lower one",
  "would be a move up"); writer flag 7 and the "NEW CLAIMS" list refer to the cut 2021-peak and 16 bps claims; the
  header line "counted by hand" is superseded by the script counts below.
- `card:boc_qt_end_2025_01` loses its citation on this page, as the writer and Gate 1 already noted.

### Item 3, the settlement-balance range

Checked on bankofcanada.ca today: the January 16, 2025 speech (excerpt still on the page), the speeches list, the
market-notices list back to March 2026, the framework page for market operations, and the September 29, 2026 joint
notice with OSFI on the Standing Liquidity Facility (no mention of the range). The site search page returned an
error, so the check was by listing pages, not keyword; notices from 2025 were not listed and were not checked.

The range is unchanged. Deputy Governor Gravelle, "Repo markets and monetary policy implementation", September 29,
2026 (raw page text, string-matched): "Using two-week term repos more actively can impact our reserves. It could mean
they sometimes exceed our best estimate of steady-state demand for reserves, which remains $50 billion to $70
billion. But keeping the supply of reserves within this range is not an objective in itself. What matters most is
deploying our operations as needed to control our policy rate when imbalances in the repo market shift and push repo
rates up or down, even if doing so temporarily pushes reserves outside the range."

Fix applied: the plate 5 range citation now carries a note with both speeches. No figure changed. The callout
"Above Jan-2025 $50-70 bn range" stays true (set January 2025, reaffirmed September 2026).

Recommended, outside this file: add the September 29, 2026 speech to the `boc_floor_system_operating_range` card and
refresh its `verified_at` (currently 2026-05-13).

### Item 4, script output

Phrase match: tile 4 of 4, abstract 6 of 6, plate 1 9 of 9, plate 2 7 of 7, plate 3 8 of 8, plate 4 5 of 5, plate 5
5 of 5. `expected_count: 7` present on all five citations of `card:boc_fad_holds_post_oct_2025_cut` (tile, abstract,
plate 1 twice, plate 2).

| Surface | Characters | Words | Hard cap |
|---|---|---|---|
| Tile line | 78 | 17 | 90 characters, 20 words |
| Abstract | 291 | 51 | 340 characters, 105 words |
| Plate 1 body | 436 | 74 | 110 words |
| Plate 2 body | 382 | 72 | 110 words |
| Plate 3 body | 387 | 71 | 110 words |
| Plate 4 body | 331 | 61 | 110 words |
| Plate 5 body | 382 | 67 | 110 words |

Titles: 61, 56, 63, 51 and 65 characters (cap 110). Gate 2's hand counts were all correct. Counted with a
whitespace split on the prose strings in this file, not by running `scripts/source_audit.mjs`.

### Item 5, values re-read

- 2-year yield 3.27% on 2026-10-01; 3.40% on 2026-09-23; overnight target 2.25% on both. There is no September 30
  yield row, so October 1 is the latest close.
- Policy gap series: -150 bps at 2026-08-01, -175 bps at 2026-09-01.
- Canada-US 2-year spread: -151 bps on 2026-10-01 (`data/processed/goc_ust_spread_2y.csv`).
- Weekly print 2026-09-30: settlement balances 83.440 (63.059 on September 16, +20.381); repos 65.929 (47.482,
  +18.447); total assets 242.555 (224.001, +18.554); Government of Canada bonds 135.645, 55.9% of assets; bonds
  145.700 on August 26 and 136.660 on September 2, a fall of 9.04.
- Overnight repo rate minus target: 3 to 6 bps on every day from September 1 to October 1; 0 bps August 20 to 28.

### Open flags (meaning; not rewritten)

1. Plate 5 framing. The title and callout are true, but the Bank explained this kind of move the day before the
   print: it now enlarges its two-week repo operations ahead of quarter-end, expects reserves to "sometimes exceed"
   the range as a result, and says staying inside the range "is not an objective in itself". September 30 is a
   quarter-end. Read cold, "jumped above the Bank's operating range" next to a repo rate above target suggests
   strain; the Bank's own account is that such an excess is deliberate and temporary. The draft asserts no cause, so
   nothing is false, and the speech does not name the September prints specifically. For the writer and editor:
   consider saying the Bank has said balances can exceed the range when it adds two-week repos around quarter-end.
   That would be a new attributed claim and would need a card for the September 29 speech.
2. Plate 5 label. The Bank calls $50 to 70 billion its "best estimate of steady-state demand for reserves", not a
   target. "Operating range" is carried over from the old copy and is defensible as shorthand; "the Bank's $50 to
   70 billion estimate of steady demand" is the stricter form.
3. Plate 5 "that held them at $63.1 billion on September 16": balances were also above $70 billion on August 5
   (71.6), August 19 (70.4) and August 26 (74.2). True as dated; extends Gate 1 open flag 6.
4. Plate 4 title "Repos, not bonds, are now moving the balance sheet." is consistent with the same speech. No change
   needed.
5. Unchanged from earlier gates: the abstract leaves out the tariff half of the Bank's sentence; `blurb.date`.
