# All-prose style sweep 2026-05-11

Gate 2 (style-editor) retroactive sweep against `editorial/writing-style.md`
Section 1 (voice), Section 8b (hero last), Section 9 (working notes), and the
concision discipline.

Hard rule applied: when uncertain, cut.

---

## PRIORITY 1 — never style-polished

### `src/pages/chart-improvements.astro`
- Word count: ~410 -> ~360 (-50)
- Edits: cut "the editorial argument directly", "the editorial title finally
  matches", "ships two parallel rising level lines" -> "plots". Tightened
  every description (8 pairs) — removed "two parallel" repetitions, replaced
  "narrative becomes visible" with "drift becomes visible", normalized
  "with honest labelling" prose. Lede: removed "Originals are tagged in
  their frontmatter; deletion is your call." (internal process detail; not
  reader value). Footer: shortened "production behaviour has changed" ->
  "Production unchanged".
- Flagged for ED: none.

### `src/pages/chart-alternatives.astro`
- Word count: ~840 -> ~810 (-30)
- Edits: lede tightened ("review, keep" -> "Keep what survives"). 22 of 28
  `whatDifferent`/`whyBetter` strings touched: removed all-caps emphasis
  ("IS the editorial signal" -> "is"), "Bay Street trades" -> "The basis
  trades" (voice principle on bank-as-authority surfaces apply here too,
  even though this is reviewer-facing). Tightened phrasing across all four
  GDP alts, all four inflation alts, three of four labour alts, three of
  four policy alts, three of four markets alts, three of four trade alts,
  all four housing alts. Smart-quoted "75% to US".
- Flagged for ED: none. The page is non-production (URL-accessed only),
  but the user requested coverage.

---

## PRIORITY 2 — light polish

### `src/data/sections.ts` blurb bodies
- Word count: ~430 -> ~420 (-10)
- Edits applied to all seven section blurbs:
  - GDP: "still well below the run of 1.5-2.0% readings that ran through
    last summer" -> "still well below the 1.5 to 2.0% run that held through
    last summer" (per Section 2: "to" in prose for ranges).
  - Inflation: "so the underlying signal is steadier than the headline
    suggests" -> "; the underlying signal is steadier than the headline."
    Split at semicolon for crispness. "consecutive print" -> "straight
    print" twice.
  - Labour: "The unemployment rate climbed" -> "Unemployment climbed"
    (start with the noun). "on a year-over-year basis" -> "Y/Y" (Section 2).
  - Policy: "held its overnight rate" -> "held the overnight rate".
  - Markets: "second consecutive month" -> "second straight month".
  - Trade: "the continuation of a year-long drift down from the 76-80%
    range" -> "a continuation of the year-long drift down from the 76 to
    80% range".
  - Housing: "consecutive negative reading" -> "straight negative
    reading"; "half a percentage point easier" -> "half a point easier".
- Flagged for ED: none.

### `src/components/home/TitleStatement.astro` hero abstract
- Word count: 96 -> 90 (-6)
- Edits: "written from primary sources and read in declarative prose" ->
  "written from primary sources in declarative prose" (cut the
  "and read" that didn't earn its place). "in May 2026 is loosening"
  -> "is loosening" (the date stamp above the abstract carries May 2026;
  repeating it inside the prose is redundant per Section 8b: load-bearing
  facts only). Restructured the three-clause cycle list with em-dashes
  around "half a percentage point below neutral" so the four moves read
  in parallel (unemployment / output gap / rate / CPI) rather than three
  + one. "The data come from" -> "Data come from".
- Flagged for ED: none. Hero is published, declarative, no hedging
  remained.

---

## PRIORITY 3 — sanity check only

### `editorial/published/mortgage-renewal-wall.md`
- Spot-checked head; voice intact, dates accurate, prose tight.
- No edits.

### `editorial/published/boc-fed-divergence.md`, `per-capita-output.md`, `us-tariff-repricing.md`
- Spot-checked; prior style passes hold.
- No edits.

### `src/pages/about.astro`, `src/pages/methodology.astro`
- Already reduced. Prose tight, voice on-register, no TKs.
- No edits.

---

## PRIORITY 4 — quick passes

### Section-page `lede` constants
- Found that gdp / inflation / labour / housing / markets / policy / trade
  page ledes had already been tightened in a prior pass (confirmed via
  grep: no "There are X plates that trace..." pattern; the noun leads).
  No further edits.

### `src/pages/404.astro`
- "This page is not part of the publication." — already minimal.
- No edits.

### `src/pages/og-preview/index.astro`
- Tagline: "Canadian macroeconomic indicators and analysis, in one place,
  on a single page." — slightly redundant ("in one place" + "on a single
  page" are the same idea twice). FLAGGED for editorial-director: this
  text is anchored to OG-card layout and a cross-surface brand string;
  prefer the ED's call before cutting. Suggested edit: drop "in one
  place," and keep "on a single page" — but defer to ED.

### `src/components/home/VignelliColophon.astro`
- Notes line: "Reported values match the most recently published release
  vintage; revisions are not reconciled across releases." — declarative,
  earns its place.
- Sources block intro: just the label "Sources" — fine.
- No edits.

---

## Escalations

### To fact-checker / writer
The seven section chartbook pages (`gdp.astro`, `inflation.astro`,
`labour.astro`, `policy.astro`, `markets.astro`, `trade.astro`,
`housing.astro`) carry plate `title` and `interpretationHtml` strings
loaded with literal "TK" markers (e.g., "Monthly GDP rose <strong>TK</strong>
in TK"). These render as reader-facing prose. Per task rules ("NO TKs left
anywhere"): I cannot style-fix these without fabricating facts. These need
either:
1. The auto-blurb pipeline to fire with live release-day data and replace,
   or
2. Writer to author placeholder prose without TKs (e.g., "Plate awaiting
   the next release print"), or
3. Editorial-director to gate-3-cut the per-plate interpretation slots
   until the pipeline runs.

Estimated TK count surfaced to readers across the seven section pages:
roughly 130 occurrences inside `title`/`interpretation`/`callout` fields.
This is the highest-priority follow-up.

### To editorial-director
- `og-preview/index.astro` tagline duplication noted above — ED call.
- Reader-visible TKs on every section page (above) need gate-3 decision:
  keep, replace, or hide the slot until the pipeline lands.

---

## Total words cut: ~100 across writer-controlled surfaces

(The TK-laden section pages are excluded from this count; their resolution
is out of style-editor scope.)
