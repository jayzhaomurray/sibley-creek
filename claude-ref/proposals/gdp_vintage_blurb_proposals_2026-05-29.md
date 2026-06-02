# GDP vintage blurb proposals - 2026-05-29

**New vintage (from the day's commentary, PDF at `public/research/commentaries/gdp-march-q1-2026.pdf`):**

- Q1 2026 real GDP: -0.1% annualized (a -C$893M move on a 2017-price basis; a rounding error in level terms)
- Monthly GDP, March 2026: -0.1% m/m
- Monthly GDP, March 2026 Y/Y: +0.4%
- Q1 composition: surge in imports the main drag; inventories rebounded as an offset
- Household consumption: +1.5% annualized (held up)
- Government consumption: -1% annualized; government investment: nearly -10% annualized
- Residential structures investment: nearly -8% annualized, a second straight quarterly drop (followed -9.4% in Q4 2025)
- March industry split: goods sector -0.8% m/m, services +0.1%; mining/quarrying/oil and gas -2.1% m/m
- March breadth: 8 of 20 industries declined

**Commentary take (already live, by-line Jay Zhao-Murray):**

> Sounding the alarm on a so-called "technical recession" is premature, but further economic weakness this year could force the Bank of Canada back into easing mode.

The take's spine:
1. The Q1 print is weak but is not a recession signal.
2. The risk is forward, not realized - if household spending rolls over next quarter, the recession conversation becomes legitimate.
3. The conditional rate-path read: weaker growth from here would re-open the BoC easing case.

**Important caveat for fact-check Gate 1.** The pipeline payload at `data/site/panel_data/output.json` and `data/site/sections.json` STILL shows the prior vintage (monthly Feb 2026 m/m +0.2%, Y/Y +1.0%; quarterly Q4 2025). The new monthly March print and Q1 quarterly print are NOT yet ingested into the panel data files as of this proposal's authoring. **Every replacement below cites the commentary PDF (gdp-march-q1-2026.pdf, published 2026-05-29) as the canonical primary source**, but the on-site text gate will need either (a) the pipeline to re-ingest the StatCan release before the new text ships, or (b) the new claims to be tagged with `card:gdp_march_q1_2026_commentary` so the build doesn't reject them. Flag for Jay before applying any of the proposed text.

---

## Surfaces requiring update

### Surface 1: Output section blurb body (`src/data/sections.ts` lines 280-285)

**Current text:**
> Slowly, and mostly in the resource patch. Real GDP is running near 1% Y/Y, just below the Bank of Canada's 1.2% estimate of near-term potential growth. Oil and gas are doing the heavy lifting while manufacturing is in deep recession. Services growth is trundling along. Even that 1% pace relies on population growth more than anything - on a per capita basis, output is scarcely higher than it was before the pandemic.

**Why this is drifted:**
The "near 1% Y/Y" anchor is now stale - March prints at +0.4% Y/Y. "Oil and gas doing the heavy lifting" inverts March's reality, where mining/quarrying/oil and gas led the goods-sector decline at -2.1% m/m. The blurb's editorial frame (modest growth, resource-led) no longer fits a Q1 that printed -0.1% annualized.

**Proposed replacement:**
> Stalled. Real GDP edged down 0.1% annualized in Q1 and slipped another 0.1% in March, leaving year-over-year growth at just 0.4%. Households kept spending - consumption rose 1.5% annualized - but a second straight deep drop in residential investment and a broad March pullback across 8 of 20 industries say the economy has lost its margin for error. Calls of a technical recession remain premature; another soft quarter would make them harder to dismiss, and would reopen the case for the Bank of Canada to resume cutting.

**Why this works:**
~70 words, take-mechanism-land: "Stalled" is the answer to the header question; mechanism cites Q1 -0.1% + March -0.1% + 0.4% Y/Y + the consumption-vs-residential split + 8-of-20 breadth; land restates Jay's published take (technical recession premature, BoC easing risk if weakness extends). Synthesizes rather than recites. No banned vocab. No deep-dive cross-link. Header question is "How fast is Canada's economy growing?" - answer "Stalled" is on scope.

---

### Surface 2: Output `tileLine` (`src/data/sections.ts` line 238-239)

**Current text:**
> February GDP came in soft on goods-producing industries; services held up.

**Why this is drifted:**
References February, not March/Q1. The new vintage has the same goods-soft / services-up character at the March monthly level, but the bigger story is the Q1 stall - which the tile should name.

**Proposed replacement:**
> Q1 GDP edged down 0.1% annualized; March slipped 0.1% m/m on broad goods weakness.

**Why this works:**
84 characters - inside the 85-char hard cap for the tileLine slot (see comment block at `src/data/sections.ts` line 200-212). One sentence, names the primary print, declarative. Sibling-compares cleanly to the other section tiles (inflation, labour, etc.) on length and register.

---

### Surface 3: Output section `heroKicker` and `latestReleasePrefix` derivation (`src/data/sections.ts` line 235-237)

**Current text:**
```
heroKicker: "February GDP",
heroKickerPrefix: "GDP",
latestReleasePrefix: "Monthly GDP by industry",
```

**Why this is drifted:**
`heroKicker` is the editorial fallback when the pipeline-derived date isn't available; it currently says "February GDP." The new vintage is March monthly + Q1 quarterly. Both `heroKickerPrefix: "GDP"` and `latestReleasePrefix: "Monthly GDP by industry"` are still correct as templates - the derived date pulled from the pipeline payload will update once the new vintage is ingested.

**Proposed replacement:**
```
heroKicker: "March GDP, Q1 print",
heroKickerPrefix: "GDP",
latestReleasePrefix: "Monthly GDP by industry",
```

**Why this works:**
Names the dual release (the monthly-and-quarterly day - StatCan publishes both on the same release, and the Q1 print is the bigger story). Keeps the prefix slots unchanged. Once the pipeline re-runs and `prints[0].asOf` becomes "Mar 2026", the hero kicker auto-derives to "GDP Mar 2026" and the static fallback above becomes a backup only.

Optional alternative: keep `heroKicker: "March GDP"` if Jay wants the kicker to track the monthly cadence only and let the page lede carry the Q1 framing. Flag for editorial call.

---

### Surface 4: Output plate 1 title (`src/pages/output.astro` line 63)

**Current text:**
> Headline growth is running near 1%, just below potential.

**Why this is drifted:**
"Near 1%" was the Y/Y read against the Feb 2026 monthly print (+1.0% Y/Y, +0.2% m/m). The March print sits at +0.4% Y/Y, with monthly -0.1%. The "near 1%" anchor and the "just below potential" framing both miss.

**Proposed replacement:**
> Headline growth has stalled near zero, well below potential.

**Why this works:**
Sentence-form with terminal period (per chart-plate title canon). Names the finding without microscale numbers (the +0.4% Y/Y and -0.1% m/m live in the interpretation paragraph below). "Stalled" pairs to the section blurb above for consistent voice. "Well below potential" remains true: BoC's 1.2% potential estimate sits 0.8pp above the 0.4% Y/Y print - a wider gap than the previous "two-tenths" framing.

---

### Surface 5: Output plate 1 interpretation (`src/pages/output.astro` lines 64-67)

**Current text:**
> Monthly real GDP edged up 0.2% in February, leaving the year-over-year pace at 1.0%. That sits roughly two-tenths of a point under the Bank of Canada's 1.2% estimate of near-term potential growth - close to trend, not at it. Growth is positive; it is not fast.

**Why this is drifted:**
Every number drifts. February prints replaced by March; +0.2% m/m replaced by -0.1%; +1.0% Y/Y replaced by +0.4%; the "two-tenths under potential" arithmetic no longer holds (0.4% vs 1.2% potential = roughly 0.8pp gap). The closing assertion "growth is positive; it is not fast" is now wrong - growth is not positive.

**Proposed replacement:**
> Monthly real GDP slipped 0.1% in March, dragging the year-over-year pace down to 0.4%. That now sits nearly a full point below the Bank of Canada's 1.2% estimate of near-term potential growth - well wide of trend. The quarter as a whole printed a -0.1% annualized contraction, a rounding error in level terms but a clean break from the modest expansion that preceded it.

**Why this works:**
Mirrors the original three-sentence structure (monthly print + potential-growth benchmark + framing line). Numbers anchor to the new vintage. The closing line lands the take from Jay's commentary - "rounding error in level terms but a clean break" preserves the published framing that a technical recession is premature without softening the directional read. Carries forward the existing `card:boc_mpr_potential_growth` citation for the 1.2% potential anchor.

---

### Surface 6: Output plate 2 title and interpretation (`src/pages/output.astro` lines 89-93)

**Current text (title):**
> Inventories drag the Q4 headline below the underlying pulse.

**Current text (body):**
> Real GDP contracted at a 0.6% annualized pace in Q4 2025, but the underlying composition is more constructive than the headline. Final domestic demand added 2.3 percentage points and net trade another 1.5, while a 4.2-point destocking did the damage. The quarter's weakness is more about how much was produced for the shelf than how much was sold.

**Why this is drifted:**
The plate is about Q4 2025 contributions. With Q1 2026 now the latest quarter and the chart wired to pull the latest contributions data, both the title and the body need to refresh to the Q1 print. The Q1 story is different in shape: imports (a negative trade contribution) and government drag are the headline weights; inventories swung the other way (a rebound from Q4's destocking). The "more constructive than the headline" framing was Q4-specific and is now misleading - Q1's headline (-0.1%) and underlying composition both read soft.

**Note:** I do NOT have the Q1 expenditure-side contributions in percentage-point form in the commentary (the commentary references "a surge in imports" and "inventories provided an offset" qualitatively). The replacement below uses the commentary's qualitative framing and the household / government / residential numbers that ARE in the commentary. For a proper quantitative replacement (e.g., "imports subtracted X pp, inventories added Y pp"), the StatCan 36-10-0104-01 Q1 contributions release needs to be pulled into the panel and a fact-checker pass run.

**Proposed replacement (title):**
> A surge in imports was the chief drag on Q1; housing investment compounded it.

**Proposed replacement (body):**
> Real GDP edged down 0.1% annualized in Q1 2026, with a jump in imports the main weight on the headline and a rebound in inventories providing the offset. Household consumption held up at 1.5% annualized; the cracks were elsewhere. Residential structures investment fell nearly 8% annualized, a second consecutive deep quarterly drop following a 9.4% decline in Q4, and government spending turned outright contractionary on both consumption and capital sides.

**Why this works:**
Sentence-form title with terminal period; names the finding (imports the chief drag, housing compounded). Body uses the commentary's qualitative imports / inventories framing without inventing percentage-point contributions that aren't yet in the panel data. Quantifies the load-bearing composition story (consumption +1.5%, residential -8%, prior -9.4%) since those numbers ARE in the commentary. The closing beat (government spending) is the under-the-hood beat that the chart can support visually.

**Flagged claim for fact-checker:** "government spending turned outright contractionary on both consumption and capital sides" - the commentary cites government consumption -1% annualized and government investment "nearly -10% annualized," which supports the framing. Verify on apply.

---

### Surface 7: Splash hero abstract (`src/data/sections.ts` lines 1075-1086)

**Current text:**
> Stuck below its potential, on two fronts at once. Cyclically, growth is running at 1% as the job market slackens and inflation continues to settle. Structurally, immigration reforms and tariffs are forcing a realignment. Population growth has levelled off, which is showing up clearly in the housing market, while new exports are narrowly redirecting away from the US.

**Why this is drifted:**
"Cyclically, growth is running at 1%" was true against the Feb 2026 +1.0% Y/Y print. With March at +0.4% Y/Y and Q1 outright contracting, the cyclical claim now understates the slowdown. The rest of the abstract (job market slackening, inflation settling, structural realignment via immigration and tariffs, population, exports) all hold against the broader picture.

**Proposed replacement:**
> Stalling, and on two fronts at once. Cyclically, growth has flatlined - Q1 contracted slightly and year-over-year output is running at 0.4% as the job market slackens and inflation continues to settle. Structurally, immigration reforms and tariffs are forcing a realignment. Population growth has levelled off, which is showing up clearly in the housing market, while new exports are narrowly redirecting away from the US.

**Why this works:**
Preserves the dual-front cyclical/structural architecture and the existing structural beats (immigration, tariffs, population, exports). Updates only the cyclical sentence to reflect the new vintage. Stays inside the section-abstract length budget (per writing-style.md Sec 8b, the hero matches the section abstract). The opener "Stalling" coheres with the Output section blurb's "Stalled" - hero-vs-section agreement per the section-abstract-synthesis rule.

**Note on citations:** Replacing "running at 1%" with "running at 0.4%" plus the new "Q1 contracted slightly" claim introduces two new countable claims that the existing splash hero citation block doesn't cover. New citations needed:

- `phrase: "Q1 contracted slightly"`, `source: "card:gdp_march_q1_2026_commentary"` (or `pipeline:statcan:36-10-0104-01` if the Q1 quarterly print is in the panel by the time the change ships).
- `phrase: "0.4%"`, source: `pipeline:statcan:36-10-0434-01` (or the same commentary card).

Existing citations for job market, inflation, immigration, tariffs, population, exports remain valid.

---

## Surfaces inspected and CLEAN (no drift)

- **Splash front page (`src/pages/index.astro`)**: No inline GDP-specific copy. Showcase 03 auto-rotates via `latestCommentary()` from `src/data/sections.ts` line 980, which already points at `gdp-march-q1-2026` (the new commentary is the most recent `publishedAt`). The "Read the latest note" link auto-resolves to the new PDF. No edit needed on `index.astro`.
- **Output plate 3 (`src/pages/output.astro` lines 110-137, "Resources have outrun factories by 18 percentage points")**: The plate is anchored to Jan 2023 as the indexed baseline and runs through Feb 2026 - it's a 38-month structural-divergence story. The March monthly print does not change the 18-point cumulative split. The plate's blurb may want a one-line freshening on the next regular pass to extend the anchor through March 2026, but no claim in the current copy is drifted.
- **Output plate 4 (`src/pages/output.astro` lines 138-163, "The output gap reopened to 1% in Q4")**: BoC MPR output gap is a separate BoC publication (next print at the July MPR). Not refreshed by today's StatCan release. Clean.
- **Output plate 5 (`src/pages/output.astro` lines 164-191, "Total vs per-capita real GDP")**: Indexed-to-Q4-2019 structural framing. The Q1 2026 quarterly print may want to be pulled in once the panel data updates, but the "10-point wedge / 3.8 million people" structural arc is undisturbed by one quarter's noise. Clean for this refresh cycle.
- **`/overview/` page (`src/pages/overview.astro`)**: No inline GDP-specific copy in the page itself. The Output panel renders from `enrichedSections` which composes `sections.ts` editorial canon plus pipeline data; updating the Output entry in `sections.ts` (Surfaces 1, 2, 3 above) is what flows through to the overview tile. No separate `/overview/` edit required.
- **`splashHero` citation block** (lines 1078-1086 of `sections.ts`): keep the existing citations except for the GDP one (Surface 7 above). The labour, inflation, immigration, tariffs, population, and exports citations remain valid against this vintage.
- **`/monetary/` and `/fiscal/` cross-references**: Grepped `sections.ts` blurbs and abstract citations for monetary and fiscal. Neither blurb references current-quarter GDP. Monetary blurb mentions "activity is softening" (still true; arguably truer than before) - no rewrite required. Fiscal blurb is about deficit / GDP shares and the PBO reclassification - unaffected by today's print. Both clean.
- **Output `prints[]` placeholder canon (lines 240-279 of `sections.ts`)**: All four print rows carry `value: "TK"` etc. as scaffold; pipeline overwrites these at build time. No edit needed - this is canon scaffold, not user-facing text. Pipeline regeneration is what refreshes the rendered numbers.
- **`commentaries[]` entry for `gdp-march-q1-2026` (lines 914-922)**: Already added with correct slug, title, publishedAt (2026-05-29), PDF path, and excerpt. The excerpt matches the published commentary's THE TAKE block. Clean.

---

## Suggested apply order if Jay greenlights

1. Surface 7 (splash hero) - the highest-traffic surface, lands the new tone publication-wide.
2. Surface 1 (Output section blurb) - feeds the `/overview/` Output tile and the `/output/` lede.
3. Surface 2 (`tileLine`) - same file edit as Surface 1; while you're in the block.
4. Surface 3 (heroKicker) - one-line edit.
5. Surfaces 4-6 (`/output/` plate titles + bodies) - require fact-checker pass on the Q1 contributions claim flagged in Surface 6.

Before any of (1)-(7) ship: confirm the pipeline has re-ingested the StatCan release OR confirm that new countable claims will be tagged against a `card:gdp_march_q1_2026_commentary` source-card (Jay to authorize; researcher to register).
