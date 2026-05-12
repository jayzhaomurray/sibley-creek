# Pillar B: BoC vs. Fed: how far can the divergence run?

Owner: researcher. Fact scaffold for the writer. Every claim that ends
up in deep-dive prose must trace back to a row here. Primary sources
only. NO Big-Six citations.

Tier conventions (same as `methodology_page.md`):
- **CANON** -- grounded in committed project data or a primary-source
  publication that the researcher has fetched and cited inline.
- **INFERRED** -- supplied by analysis or session brief; writer should
  hedge.
- **OPEN** -- needs more legwork or editorial-director decision.

**Editorial premise check (IMPORTANT):** The task brief stated "BoC
overnight 2.25% (cut April 29, 2026)." This is partially wrong. The
Apr 29, 2026 BoC decision **held** the overnight rate at 2.25%. The
2.25% level was reached at the **Oct 29, 2025** decision (25 bp cut
from 2.50%). The rate has been at 2.25% for six straight meetings
(Oct 2025, Dec 2025, Jan 2026, Mar 2026, Apr 2026). Writer should not
say "the April cut"; the canonical phrasing is "BoC has held at 2.25%
since October 2025." Source: `data/raw/overnight_rate_target.csv`
(monthly V39079); BoC Apr 29 2026 press release
(https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/).

---

## 1. Current state of divergence

### 1.1 Policy-rate level

**CANON:**
- **BoC overnight rate target: 2.25%** as of close 2026-05-10. Held
  at this level since 2025-10-29 decision. Bank Rate 2.50%; deposit
  rate 2.20%. (BoC Apr 29 2026 press release; V39079.)
- **Fed funds target: 3.75% (upper bound of 3.50-3.75% target
  range)** as of 2026-05-10. Last move was a 25 bp cut on 2025-12.
  (FRED series DFEDTARU; `data/raw/fed_funds.csv`. Switched from
  midpoint to upper bound 2026-05-11 -- upper bound is the
  headline policy reference the Fed publishes; midpoint is a
  derived synthesis.)
- **Policy-rate spread BoC minus Fed = -1.50 percentage points.**
  (`data/raw/overnight_rate_target.csv` minus
  `data/raw/fed_funds.csv`, latest values.)

### 1.2 Curve-level divergence (2y, 10y)

**CANON** (latest close 2026-05-07 across all four series; daily series
from BoC Valet for GoC, FRED DGS2 / DGS10 for UST):
- 2y GoC: **2.94%**.
- 2y UST: **3.92%**.
- **2y GoC-UST spread: -0.98 pp.**
- 10y GoC: **3.53%**.
- 10y UST: **OPEN** -- `us_10yr` not in current `data/raw/` (only
  `us_2yr.csv` is wired). Writer should treat the 10y-vs-10y leg as
  a research gap; ask backend-engineer to wire FRED DGS10 before
  publish. The Pillar can still run on 2y spreads + policy spread +
  FX; the 10y leg is desirable but not load-bearing for the
  "transmission channels that bind" argument.

### 1.3 Historical context (percentile of post-2001 daily
distribution for 2y; post-1996 monthly distribution for policy
spread)

**CANON** (derived from full project data; see
`analyses/boc_fed_divergence_2026_05_11.py` -- TO BE WRITTEN; the
spread calcs were run inline this session and printed values are
quoted below):

- **2y GoC-UST spread: -0.98 pp** sits at the **5.0th percentile** of
  the post-2001 daily distribution. The all-time min is **-1.70 pp
  on 2025-02-03**; all-time max **+2.26 pp on 2003-04-01**. Today is
  near the historical floor but not at it.
- **BoC-Fed policy-rate spread: -1.375 pp** sits at the **8.2nd
  percentile** of the post-1996 monthly distribution. Min ever
  **-2.51 pp in April 1997**; max **+2.03 pp in June 2003**.
- **Reading:** The 2y spread is in the bottom 5% of recorded history;
  the policy spread is in the bottom 8%. This is a deep-divergence
  episode, but not unprecedented -- 1997 ran wider, and the curve
  was wider in early 2025.

### 1.4 USDCAD level

**CANON** (`data/raw/usdcad.csv`; latest 2026-05-01 spot 1.3575):
- USDCAD at the **67.3rd percentile** of the post-1990 daily
  distribution. (Run of
  `analyses/usdcad_percentile_2026_05_11.py`.)
- The CAD has **strengthened** through spring 2026; the spot rate
  moved from above 1.40 earlier in the cycle down to ~1.36. This
  pattern is inconsistent with the naive "wider divergence -> weaker
  CAD" story and is the most interesting fact in the dataset for
  the Pillar.
- **INFERRED:** That CAD has held / strengthened despite a -138 bp
  policy spread means the FX channel is not binding right now. The
  loonie is being supported by something other than rate
  differentials -- candidates: commodity terms-of-trade (WTI level),
  USD weakness against majors broadly, or current-account dynamics.
  Writer should flag this paradox, not paper over it.

---

## 2. Path divergence (next 4 meetings)

**OPEN.** Project data does not currently wire OIS-implied paths or
Fed dot-plot data. To answer the brief's "path divergence" question
strictly we would need:
- BoC-implied OIS path for next 4 meetings (Jun 10, Jul 15, Sep 2,
  Oct 28). Source: Bloomberg WIRP or CanDeal -- NOT currently in
  pipeline.
- Fed dot plot from the March 2026 SEP and FOMC implied path. Source:
  https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

**INFERRED FROM CONTEXT** (forward-look without paid feeds):
- The BoC Apr 29 statement said it "stands ready to respond as
  needed" and noted CPI is expected to "rise further in April to
  about 3%" before declining back toward 2% early 2027 -- a hawkish
  tilt that points to **hold-and-watch**, not further cuts. (BoC Apr
  29 2026 press release.)
- The Fed has cut 175 bp from its 2024 peak (5.50% -> 3.75%, upper
  bound) and the FOMC has not signalled further cuts in recent
  communication.
  **OPEN:** verify against latest FOMC minutes before writer drafts.

**Writer guidance:** Treat the path divergence section as a known gap
and write around it. The bullet to make is structural: "the spread
will widen further only if the Fed cuts and the BoC holds, or the BoC
cuts again while the Fed holds." Then say what would force each.

---

## 3. Transmission channels that bind

### 3.1 FX channel

**CANON:**
- USDCAD currently 1.3575 (2026-05-01), 67.3rd percentile post-1990.
  Has strengthened through spring 2026 despite the -138 bp policy
  spread.
- BoC's most-cited primary research on exchange-rate pass-through to
  import prices: **Devereux, Dong, Tomlin (2015), "Exchange Rate
  Pass-Through, Currency of Invoicing and Market Share," BoC Working
  Paper 2015-31.** Headline finding: a 1% CAD depreciation is
  associated with a **0.59% rise in Canadian import prices**.
  Apparel pass-through ~82%; vegetables ~21%. Goods invoiced in USD
  show substantially higher pass-through than CAD-invoiced goods.
  Source: https://www.bankofcanada.ca/wp-content/uploads/2015/08/wp2015-31.pdf
- **From import-price pass-through to CPI**: the BoC's standard
  rule of thumb (`MPR` references over multiple cycles) is that a
  10% sustained CAD depreciation lifts headline CPI by roughly
  0.5-0.7 pp over two years. **OPEN:** locate a single MPR box that
  states this number canonically; the 2015 WP gives import-price
  pass-through, not the import-to-CPI step. Writer should not quote
  a precise "10% CAD = X% CPI" number without an MPR citation.
- BoC Apr 29 statement: "The Canada-US exchange rate has been
  relatively stable" -- the Bank itself is not flagging FX as
  binding right now.

### 3.2 Credit channel

**OPEN.** Project data does not currently wire:
- Canadian IG / HY corporate spreads (need a CDX or Bloomberg
  Canadian credit index, or BoC FSR appendix data).
- Bank funding spreads (CDOR-GoC, CD spreads).
- Mortgage-GoC spreads.

US IG/HY OAS (BAMLC0A0CM, BAMLH0A0HYM2) are listed in
`data/SOURCES.md` as wired through FRED but not visible in
`data/raw/`. **Ask backend-engineer:** are these actually fetched
currently? If yes, writer can use US HY OAS as a proxy for global
credit conditions.

**Writer guidance:** Treat the credit channel as a structural box
(what would tighten if it bound) rather than a quantified channel
in this draft. Re-research before Pillar B v2.

### 3.3 Term-premium channel

**CANON:**
- 10y GoC sits at 3.53% (2026-05-07); 10y UST not currently in
  project data.
- 10y-2y GoC slope: 3.53 - 2.94 = **+0.59 pp** (positive, modestly
  steep, consistent with normal-cycle term structure).
- **INFERRED:** With BoC at 2.25% and the 10y at 3.53%, the long end
  is pricing a meaningful term premium / expected-policy reversion
  above neutral. If divergence widened further (e.g. BoC cuts again
  while Fed holds), the question is whether the GoC long end **rises
  on imported US-Treasury beta** rather than on Canadian fundamentals
  -- a perverse outcome where BoC easing tightens financial
  conditions through the long end.

**OPEN:** Source a BoC FSR or working paper on GoC-UST long-end
co-movement / "import" of US term premium. Plausible candidates:
- BoC Staff Discussion Paper on the Canadian term premium (search
  bankofcanada.ca for "term premium decomposition Canada").
- BoC FSR 2024 box on long-end repricing under divergence.
Writer should not assert a numeric long-end import without a
citation.

---

## 4. Historical breakpoints

**CANON** (post-1996 BoC-Fed policy spread; from
`data/raw/overnight_rate_target.csv` and `data/raw/fed_funds.csv`):

The BoC-Fed policy spread has gone substantially negative four times
post-1996. Each is a candidate prior episode:

1. **1996-1998: spread bottomed at -2.51 pp in April 1997.** BoC held
   below Fed throughout the 1997-98 cycle. Resolution: BoC raised
   100 bp on 1998-08-27 (the famous "loonie defence" intermeeting
   hike) when CAD broke 1.50 -- a FX-channel capitulation. Source
   for the hike: BoC press release Aug 27 1998
   (https://www.bankofcanada.ca/1998/08/press-release-1998-08-27/) --
   OPEN, writer should verify this URL works before publish.
2. **2015-2017: BoC cut twice in 2015 (Jan, Jul) on the oil shock**
   while the Fed lifted off zero in Dec 2015. Policy spread reached
   roughly -75 to -100 bp. Resolution: BoC waited; CAD weakened to
   ~1.45 but did not crisis; the divergence resolved through Fed
   pauses in 2016. (Source: BoC Jan 21 2015 statement; FRED
   DFEDTARU.)
3. **2024-2025: BoC cut to 3.25% before the Fed and ran ahead.** The
   2y GoC-UST spread hit its post-2001 minimum of **-1.70 pp on
   2025-02-03** -- this is the binding precedent. CAD ran to ~1.45+
   intraday in late Q1 2025. Resolution: Fed began cutting in late
   2025; spread closed to current ~-100 bp. (Source: full
   `data/raw/` daily files.)

**Open question for writer:** of the three episodes, which is the
closest structural analogue today? Researcher's view (INFERRED):
2024-2025 is the right analogue, because (a) BoC was again ahead of
the Fed on cuts, (b) CAD held in the 1.40-1.45 range without forcing
a back-off, and (c) the breakpoint was Fed convergence, not BoC
capitulation. The 1997-98 analogue would be invoked only if CAD
broke 1.45+ decisively, which it has not.

---

## 5. What would force a BoC back-off

**Researcher's stack-ranked candidates, with evidence:**

1. **CAD breaking 1.45+ and holding.** The 1998 precedent (1.50
   trigger) and the 2025 precedent (1.45+ without forcing capitulation)
   bracket the threshold. **OPEN:** locate Tiff Macklem or Carolyn
   Rogers public remarks in 2025 that named a level or pace, if any.
2. **Inflation expectations breaking.**
   - **CANON:** Consumer 1y expectations: 3.98% in 2026Q1 (down
     from 4.10% in 2025Q4 and 4.0% in 2025Q3). Source: BoC CSCE,
     `data/raw/infl_exp_consumer_1y.csv`.
   - **CANON:** Consumer 5y expectations: 3.02% in 2026Q1 (down
     from 3.09% in 2025Q4 and 3.67% in 2025Q3). Source: BoC CSCE,
     `data/raw/infl_exp_consumer_5y.csv`.
   - **CANON:** BOS firms expecting CPI above 3%: 11% in 2026Q1
     (down from 16% in 2025Q4 and 18% in 2025Q3). Source: BoC BOS,
     `data/raw/bos_dist_above3.csv`.
   - **Reading:** Expectations are moderating, NOT breaking. This
     is the strongest argument that BoC has runway to hold at 2.25%
     and tolerate the spread.
3. **Headline CPI re-accelerating.** Latest headline CPI YoY: 2.32%
   in March 2026 (StatCan; `data/raw/cpi_all_items_sa.csv` derived
   YoY). BoC itself expects April to print "about 3%" on gasoline,
   then decline. If April prints above 3% and **doesn't decline**,
   that forces a re-think.
4. **GoC 10y rising to 4%+** on imported term premium -- tightens
   financial conditions despite BoC standing pat, removes optionality
   to cut further. Currently 3.53%, so headroom of ~50 bp before this
   binds.
5. **Credit conditions tightening.** Cannot quantify with current
   project data. **OPEN.**

**Writer's load-bearing claim opportunity:** the binding constraint
right now is **NOT** the policy-rate spread or USDCAD level
mechanically -- it is the inflation-expectations chain. As long as
1y and 5y consumer expectations are moving toward 2%, BoC can hold
at 2.25% indefinitely.

---

## 6. The CAD-specific feedback loop

**CANON pass-through estimates:**
- **Import-price pass-through: ~0.59 (Devereux, Dong, Tomlin 2015,
  BoC WP 2015-31).** A 1% CAD depreciation -> 0.59% rise in import
  prices.
- **Import-price to CPI step: OPEN.** A typical BoC MPR rule of thumb
  cited across cycles is that a 10% sustained CAD depreciation lifts
  headline CPI by ~0.5-0.7 pp over two years, of which roughly
  half lands in year one. **Writer should not assert a numeric
  pass-through to CPI without locating the exact MPR box or
  staff-paper source.**

**Goods vs services share** (CANON, StatCan basket 18-10-0007-01):
- The Canadian CPI basket is roughly 47% goods, 53% services
  (2024 basket). Imported component is concentrated in goods,
  particularly clothing, vehicles, recreation, household furnishings.
  **OPEN:** pull the exact basket weights from
  `data/raw/cpi_basket_weight_goods.csv` for a precise share.

**Feedback-loop sketch (INFERRED, structural):**
- CAD -10% over a year -> import prices +~6% (0.59 pass-through) ->
  goods CPI lifts by share of imported goods x ~6% -> headline CPI
  rises by maybe 0.6-0.7 pp over two years.
- For the loop to BIND, you need a CAD move of size **and** durable.
  Today's CAD is roughly flat YTD; the feedback loop is not active.

---

## 7. Claim ladder

Five candidate load-bearing claims, ordered by (data support) x
(editorial weight):

1. **"The 2y GoC-UST spread sits at the 5th percentile of recorded
   history, and the policy spread at the 8th -- but USDCAD is at
   the 67th. The FX channel is not binding."**
   Data: 5/5. Editorial weight: 5/5. This is THE claim.
2. **"The 2024-2025 episode is the operating precedent, not 1997-98.
   BoC ran the spread to -1.70 pp at the 2y, CAD touched 1.45+, and
   the resolution came from Fed convergence, not BoC capitulation."**
   Data: 4/5. Editorial weight: 5/5.
3. **"What forces a BoC back-off is the inflation-expectations chain,
   not the FX level. Consumer 1y and 5y expectations and BOS firms
   are all moving toward 2%. Until that reverses, BoC has runway."**
   Data: 5/5 on the expectations data; 3/5 on the causal claim (the
   writer must hedge "until that reverses"). Editorial weight: 5/5.
4. **"A 10% CAD depreciation translates to ~6% import-price inflation
   (BoC WP 2015-31) and roughly 0.6 pp headline CPI over two years
   -- material but not catastrophic. Today's CAD is flat. The loop
   is dormant."**
   Data: 4/5 on the pass-through; 3/5 on the CPI step (needs an MPR
   citation). Editorial weight: 4/5.
5. **"If divergence widens further, the binding constraint flips to
   the GoC long end. 10y GoC at 3.53% has ~50 bp of headroom before
   it tightens financial conditions enough to undo BoC's stance."**
   Data: 3/5 (we have the level but not a clean BoC source on
   imported term premium). Editorial weight: 4/5. INFERRED, hedge.

---

## 8. Chart specifications (writer commissions chart-builder)

### Chart B1 -- Policy-rate divergence, four decades

- **Title:** "BoC and Fed: when they break the same way, and when
  they don't."
- **Data:** `data/raw/overnight_rate_target.csv` (BoC overnight
  target) AND `data/raw/fed_funds.csv` (Fed funds effective). Plot
  both. Add a bottom panel of the spread.
- **Cadence:** Monthly (last value of month).
- **Window:** 1996-01 through latest available.
- **Visual:** Top panel two-line overlay (BoC line A; Fed line B);
  bottom panel area chart of (BoC - Fed) shaded above/below zero.
  Highlight three episodes with annotation: 1997-98 (-2.51 pp
  trough), 2015-17 oil-shock divergence, 2024-25 current.
- **Answers framework question:** 1, 4.

### Chart B2 -- The 2y curve spread is at its post-2001 floor

- **Title:** "2y GoC minus 2y UST."
- **Data:** `data/raw/yield_2yr.csv` minus `data/raw/us_2yr.csv`,
  computed daily on common dates.
- **Cadence:** Daily.
- **Window:** 2001-01 through latest.
- **Visual:** Single-line chart with horizontal dashes at the
  post-2001 5th, 50th, 95th percentile. Annotate the 2025-02-03
  trough (-1.70 pp) and current value.
- **Answers framework question:** 1, 4.

### Chart B3 -- USDCAD has strengthened despite divergence

- **Title:** "Divergence widened, the loonie held."
- **Data:** Top panel `data/raw/usdcad.csv`; bottom panel the same
  spread series as Chart B2.
- **Cadence:** Daily.
- **Window:** 2024-01 through latest.
- **Visual:** Dual-panel: USDCAD top (single line), 2y spread bottom
  (single line). The visual point: the two are NOT moving together
  through Q1-Q2 2026. Add a single annotation at 2026-04-29 (BoC
  hold).
- **Answers framework question:** 1, 3a, 6.

### Chart B4 -- Inflation expectations are moderating, not breaking

- **Title:** "What anchors the BoC's runway."
- **Data:** Three series from BoC CSCE (1y, 5y) and BOS:
  `infl_exp_consumer_1y`, `infl_exp_consumer_5y`,
  `bos_dist_above3` (% of firms expecting CPI > 3%).
- **Cadence:** Quarterly.
- **Window:** 2021-Q1 through 2026-Q1.
- **Visual:** Three-line overlay (left-axis for the two consumer
  series in %; right-axis for the BOS share in %). Annotate the
  recent peak (2024 mid-cycle) and the current value.
- **Answers framework question:** 5.

### Chart B5 -- Pass-through cascade

- **Title:** "If CAD slips 10%, headline CPI lifts ~0.6 pp over two
  years."
- **Data:** Constructed (not series). Build a small horizontal-bar
  cascade: (a) 10% CAD depreciation, (b) 5.9% import-price rise
  (Devereux et al 0.59 pass-through), (c) goods-CPI lift = 5.9% x
  (imported share of CPI goods basket; OPEN, ~25-30%), (d) headline
  CPI lift ~0.6 pp over 24 months.
- **Cadence:** Static schematic.
- **Window:** N/A.
- **Visual:** Four stacked horizontal bars with annotation arrows
  between them. Source line: "Devereux, Dong, Tomlin (BoC WP
  2015-31); StatCan basket weights; researcher estimate."
- **Answers framework question:** 3a, 6.

### Chart B6 -- The 2024-25 precedent

- **Title:** "How the last episode resolved."
- **Data:** `data/raw/overnight_rate_target.csv`,
  `data/raw/fed_funds.csv`, `data/raw/usdcad.csv` all on a single
  panel, dual-axis (rates left, FX right).
- **Cadence:** Monthly for rates, daily for FX (resampled).
- **Window:** 2024-01 through 2026-05.
- **Visual:** Three-line overlay. Annotate (a) BoC's first cut Jun
  2024, (b) Fed's first cut Sep 2024, (c) BoC 2.25% reached Oct 2025,
  (d) Fed convergence into Dec 2025. The visual point: BoC cut first
  and farther; the spread compressed when the Fed caught up, not
  when BoC reversed.
- **Answers framework question:** 4.

---

## 9. Open questions for the writer / editorial-director

- **Chart B5 import-share lookup.** OPEN. Pull
  `data/raw/cpi_basket_weight_goods.csv` and the StatCan
  imported-components share. If editorial-director wants a
  full-precision pass-through cascade, researcher needs ~30 min.
- **MPR canonical pass-through statement.** OPEN. Locate the BoC
  MPR box / staff paper that gives the "10% CAD = X pp CPI" number.
  Without it, writer must hedge claim 4.
- **10y UST not in pipeline.** OPEN. Ask backend-engineer to wire
  FRED DGS10 so the 10y-vs-10y leg can be quoted.
- **Credit-spread series not in pipeline.** OPEN. Confirm with
  backend-engineer whether FRED BAMLC0A0CM and BAMLH0A0HYM2 are
  actually fetched; they are listed in `data/SOURCES.md`.
- **OIS-implied path / Fed dot plot.** OPEN. Without paid feeds the
  Pillar cannot quantify the 4-meeting forward spread. Writer should
  argue structurally around this gap, not numerically.
- **The CAD-strengthening paradox.** This is the analytic puzzle of
  the Pillar. Researcher's working hypothesis: USD weakness against
  majors broadly + commodity terms-of-trade are dominating the rate-
  differential channel through spring 2026. Writer should treat this
  as the lede, not bury it.

---

End of Pillar B insight base. Researcher updates this file as the
OPEN items resolve.
