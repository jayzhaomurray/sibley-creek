# Writing Style Guide: macro-research-department

Authored by style-editor. First-session deliverable.
The voice principles in `dashboard_purpose.md` Section 7 are the
bearings. This document is the working compass.

Defaults: Canadian English, ASCII-friendly, numerate, declarative.
Reference style desks: Financial Times, The Economist, Globe and Mail
Report on Business, Canadian Press. The Bank of Canada's MPR is the
local exemplar for declarative numerate prose; we write closer to that
register than to a bank morning note.

When this guide and an individual writer's instinct disagree, default
to this guide and flag the friction to style-editor. When this guide
and `dashboard_purpose.md` Section 7 appear to disagree, Section 7
wins and this document is wrong.

---

## 1. Voice

### What the dashboard sounds like

**Formal but not stiff.** A CPP Investments PM reading us before 7am
should recognize the register of an FT lead note or a BoC MPR box --
short sentences, concrete nouns, declarative verbs, no throat-clearing.
Not a textbook. Not a bank flash. Not a substack.

**Declarative, with calibrated uncertainty.** State what is true. When
the data are ambiguous, say so plainly and name what would resolve it.
"The data are consistent with both stories" is a finished sentence.
"It is perhaps possible that the data may, in some interpretations,
suggest" is not a sentence we publish.

**Numerate, not number-spammy.** Every number in prose earns its place.
If a chart shows it, the prose does not also recite it; the prose
points to what the chart cannot say. The job of a paragraph next to a
chart is to tell the reader what to notice, not to read the y-axis
back to them.

**Plain English, technical where it must be.** "Term premium" stays.
"Core-trim," "core-median," "neutral band," "shelter ex-mortgage
interest" stay. "Optionality," "constructive," "wait-and-see," "the
setup," "the tape" do not. If a term carries weight in the argument
and is not in the reader's working vocabulary, define it once on first
use; do not patronize.

**Confident without breathlessness.** Cycles are long. Most days
nothing changes. Say so. A print that comes in 0.1pp off consensus is
not a "shock." A 25bp cut that was 80% priced is not a "pivot."

**Canadian, first and finally.** The frame is always: so what for
Canada. US developments enter through the BoC reaction function,
through Canadian export demand, through Canadian exporter margins, or
not at all. If a sentence could run unchanged in a US shop, rewrite or
cut.

### The two registers we actually write

The dashboard supports two prose registers. They share spelling,
punctuation, and numerate discipline. They differ in cadence,
sentence length, and how much editorial voice is allowed.

See Section 7 below for the full distinction. In one line:

- **Automated event-blurb voice** -- terse, primary-source, no
  editorializing. The CPI / LFS / GDP / rate-decision basics blurbs.
- **Deep-dive voice** -- chief-economist prose. Argument-bearing,
  willing to take a side, willing to say "we do not yet know."

---

## 2. Conventions

### Numbers

- Comma thousands separator, period decimal: `1,247` and `2.4`.
- Decimals: as many as the source publishes, no more. CPI to one
  decimal (`2.4%`); the unemployment rate to one decimal (`6.8%`);
  GDP growth to one decimal in headline prose (`Q/Q SAAR 1.4%`),
  two only when the second decimal carries the call.
- Spell out zero through nine in non-statistical prose ("three
  provinces," "five deep dives"); use numerals for ten and up, and
  always for statistical or economic quantities ("4 of the 10
  provinces" is fine when the contrast matters).
- Million / billion are spelled out in prose (`$42 billion`), not
  abbreviated (`$42B`) in running prose. In chart titles and table
  headers, `$bn` and `$mn` are acceptable for space.
- Negative numbers use a minus sign or "negative" in prose, not
  parentheses. Parentheses are for tables.
- Use "to" for ranges in prose (`2.4 to 2.7%`), an en-dash in tables
  and chart titles (`2.4-2.7%` with hyphen as the ASCII stand-in --
  see Section 3).

### Percentages and basis points

- Percent: `2.4%`, no space, no "per cent." Globe house style allows
  "per cent"; we choose `%` for density. Consistency matters more
  than the choice; do not mix within a piece.
- Percentage points: `pp`. `Core-trim rose 0.2pp to 2.9%.`
- Basis points: `bps`, lower case, space before, no period. `25 bps`.
  Never `bp` (singular), never `BPS`. In a chart axis you may use
  `bps` or `bp` consistently; the prose default is `bps`.
- A rate move is `cut 25 bps` or `cut by 25 bps`, not `lowered
  rates 0.25%`. The unit "basis points" is what the desk speaks.

### Currency

- CAD is the default. A plain dollar sign means CAD: `$42 billion`.
- USD is always labelled: `US$310 billion` or `USD 310 billion`.
  First reference in any piece that uses both: `C$` and `US$` once,
  then `$` for CAD thereafter if no ambiguity remains. If a paragraph
  mixes both, keep the prefix on every figure.
- Mixed-currency tables note the unit per column.
- Other currencies labelled in full or by ISO code: `EUR 5 billion`,
  `JPY 200 billion`.

### Dates

- Long-form in prose: `May 10, 2026`. The comma after the year is
  required when the sentence continues (`May 10, 2026, was the day
  the print landed`).
- ISO in machine-adjacent contexts, version stamps, footnotes, and
  data-vintage notes: `2026-05-10`.
- Never US short form (`5/10/26`). Never UK short form (`10/5/26`).
  Ambiguous to half our readers, wrong to the other half.
- Quarters: `Q1 2026`, `Q4 2025`. Not `2026Q1`, not `1Q26`.
- Fiscal years (federal Canada, Apr 1 - Mar 31): `FY2025-26` or
  `fiscal 2025-26`. The hyphenated span is the convention.
- Months: spell out in prose (`October 2024 IRCC plan`). Abbreviate
  only in tables (`Oct 2024`), three-letter, no period.
- Time of day: rarely needed; when it is, `9:30 a.m. ET`.

### Units and other quantities

- Index points: `the CEER fell 1.2 points to 117.3`.
- Annualization: `3-month annualized` or `3M AR` (the abbreviation is
  acceptable on second reference and in chart titles). `Q/Q SAAR` is
  the convention for GDP.
- Year-over-year: `Y/Y` in prose; spell out on first use if the
  piece's audience may include P3 readers unfamiliar with the
  shorthand.
- Population and persons: `4.2 million temporary residents`, not
  `4.2M`. Persons are not basis points.
- Tonnes, barrels, cubic metres: SI / metric. `bbl/d` is acceptable
  for oil flows on second reference.

### Chart-plate titles

**Voice canon (the GDP page is the live reference).** A chart-plate
title is a finished editorial sentence — not a description of the
chart, not a recitation of the data, not a question. **The title
carries the takeaway; the chart carries the data.** If a reader can
get the title's content by glancing at the chart for two seconds, the
title is doing nothing.

Specifically: do NOT recite what the chart already shows
("Wage measures spanned 3.1% to 4.8%"). DO state what the data MEANS
("Wage growth is no longer the binding inflation risk."). Numbers in
the title earn their place only when they ARE the takeaway (a
threshold crossing, a regime shift, a record level).

Rules:

- **Sentence case, not title case.** Capitalize only the first word and
  proper nouns.
- **Terminal period.** Every chart-plate title ends with a period.
  The period is the signal that this is a finished editorial
  sentence, not a headline fragment.
- **One declarative verb, present or past.** "Output gap widened to
  -1.0% in Q4 2025, doubling the Q3 shortfall." "Aggregate growth
  has run well ahead of per-capita output since 2019."
- **Names the finding, not just the level.** "Productivity growth
  decelerated sharply into year-end." beats "Productivity 0.3% Y/Y."
- **One clause preferred; one extending clause OK.** Use a comma or
  em-dash to extend; avoid semicolons (they push toward compound-
  headline register and away from a single declarative sentence).
- **Observation — interpretation pattern is valid.** When the
  finding has a two-step structure (a data observation that needs
  one beat of interpretation to land), an em-dash can join two
  independent clauses: *"Finding rates have softened more than
  separations have risen — rising unemployment is a hiring-side
  story."* The observation half stays plain; the interpretation
  half names the read. The em-dash is the gate: anything past it
  is the interpretive payoff, not a second observation.
- **No colons.** Colons are headline-style ("Breadth widens: a
  quarter of the basket back above 3%"); we want a sentence.

Examples (GDP page, live):

- "An inventory drawdown swamped a positive domestic profile in
  Q4." — takeaway only. The -0.6% headline is in the chart and the
  callout. The title names the read: the headline misrepresents the
  underlying picture.
- "Aggregate growth has run well ahead of per-capita output since
  2019." — takeaway only. No numbers. The chart shows the gap;
  the title says why it matters.
- "Productivity growth decelerated sharply into year-end." —
  takeaway only.
- "Output gap widened to -1.0% in Q4 2025, doubling the Q3
  shortfall." — number-in-title format OK here: the threshold (-1%)
  is itself a regime read, and "doubling" is the takeaway.

Counter-examples (drift to fix — data recitation, no takeaway):

- BAD: "Wage measures spanned 3.1% to 4.8%, with the composition-
  adjusted reading sitting at the bottom." — pure description of
  what's on the chart.
  FIX: "Wage growth is no longer the binding inflation risk."
  (Or whatever the actual editorial read is.)
- BAD: "Settlement balances held near $64 billion as the floor-
  maintenance phase continued." — describes the level.
  FIX: "The Bank's balance sheet has settled into a stable
  floor-maintenance regime."
- BAD: "Capacity utilization sat at 78.5% in Q4, well below its
  post-1996 average." — describes the level + reference.
  FIX: "Capacity utilization remains consistent with a negative
  output gap."
- BAD: "Foreign direct investment by sector, inward and outward,
  awaits ingestion." — describes the slot state.
  FIX: keep as a passive descriptive line ONLY because the slot is
  in-progress; flag the plate as data-pending so the canon doesn't
  apply.

The test: read the title without the chart. Does the reader learn
something they couldn't get from a 2-second glance at the chart
itself? If no, the title needs to be rewritten until yes.
- Chart subtitles carry the unit and the date: `Per cent, monthly,
  to March 2026`.
- Sources line, every chart: `Source: Statistics Canada Table
  14-10-0287-01. Author calculations.` Primary source first; "Author
  calculations" appended when the series is constructed.

### Paragraph length and rhythm

- Short paragraphs. Two to five sentences is the target. A paragraph
  that runs eight sentences should split.
- Lead with the sentence that carries the claim. Subordinate clauses
  last, not first.
- One idea per paragraph. If the paragraph has a "but" in the middle
  that pivots to a different idea, break the paragraph at the "but."
- Vary sentence length. A paragraph of seven 22-word sentences reads
  as a wall. A paragraph of seven 6-word sentences reads as a tic.

---

## 3. Punctuation

### Em-dash

- Style: em-dash with **no surrounding spaces** for parenthetical
  interruption. Globe / FT convention: `the BoC cut 25 bps--the third
  consecutive move--ahead of the September pause`.
- The build environment is ASCII-only where the toolchain requires
  it. Where the renderer cannot produce a true em-dash, use a
  double-hyphen `--` as the stand-in. Where it can, use the em-dash
  glyph. Either is acceptable; consistency within a piece is required.
- Do not use em-dashes as a substitute for a colon or a full stop
  more than once a paragraph. They lose their force.
- Never use a single space-hyphen-space ` - ` as a parenthetical
  break. That is a typo, not punctuation.

### En-dash

- Used for numeric and date ranges: `2020-21`, `2.4-2.7%`, `pages
  12-18`. In ASCII contexts, the hyphen stands in -- defend the
  spirit (range) not the glyph.
- Never `2020--21` (that is a TeX habit, not English typography).
- For approximate ranges in prose, prefer "to": `2.4 to 2.7%`.

### Hyphen

- Compound modifiers before a noun: `rate-sensitive sector`,
  `mortgage-renewal wall`, `per-capita output`, `five-year fixed`.
- Not after the noun: `the sector is rate sensitive`.
- "Core-trim" and "core-median" are hyphenated; they are the BoC's
  registered names of the measures.
- "Year-over-year" hyphenated as an adjective; spelled out without
  hyphens when used as a noun phrase is rare and avoidable.
- Compound numbers spelled out: `twenty-five`, `forty-second`.

### Comma

- Oxford comma: yes. `RBC, TD, BMO, Scotia, CIBC, and National
  Bank.` This is also Canadian Press practice when ambiguity would
  otherwise result; we apply it universally for consistency.
- Commas inside quotation marks when the quoted material ends a
  clause: Canadian Press convention. `The MPR called it
  "broadly balanced," which is the standard formula.`

### Colon and semicolon

- Colon introduces a list or a payoff. The clause before a colon
  should be a complete sentence.
- Semicolon for two independent clauses that belong tightly together.
  Use sparingly. If you can replace with a full stop, do.

### Quotation marks

- Double quotes for direct quotation and for scare quotes used
  sparingly. Single quotes only inside a double-quoted passage.
- Curly quotes are aesthetically preferred but the build is
  ASCII-friendly: straight quotes `"like this"` are acceptable and
  often required by the toolchain. Pick one per piece.

### Apostrophes

- Possessive of singular nouns ending in `s`: `StatCan's`,
  `Scotia's`, `Brookings's` (Globe practice). Plurals: `the banks'
  PCL builds`.
- Decade abbreviations: `the 1990s`, `the '90s`, never `the 1990's`.

---

## 4. Institution-name conventions

Spell out on first reference. Abbreviate after. Never use casual
short forms.

| First reference | After |
|---|---|
| Bank of Canada | BoC |
| Statistics Canada | StatCan |
| Office of the Superintendent of Financial Institutions | OSFI |
| Canada Mortgage and Housing Corporation | CMHC |
| Department of Finance Canada | DoF (or "Finance" if context is clear) |
| Parliamentary Budget Officer | PBO |
| Canada Revenue Agency | CRA |
| Canada Border Services Agency | CBSA |
| Immigration, Refugees and Citizenship Canada | IRCC |
| Employment and Social Development Canada | ESDC |
| Innovation, Science and Economic Development Canada | ISED |
| Crown-Indigenous Relations and Northern Affairs Canada | CIRNAC |
| Canadian Real Estate Association | CREA |
| Canadian Bankers Association | CBA |
| C.D. Howe Institute | C.D. Howe (the periods stay) |
| Institute for Research on Public Policy | IRPP |
| Macdonald-Laurier Institute | MLI |
| International Monetary Fund | IMF |
| Organisation for Economic Co-operation and Development | OECD |
| Bank for International Settlements | BIS |
| US Federal Reserve | the Fed |
| US Trade Representative | USTR |
| Federal Open Market Committee | FOMC |
| Monetary Policy Report | MPR |
| Financial System Review | FSR |
| Labour Force Survey | LFS |
| Survey of Employment, Payrolls and Hours | SEPH |
| Job Vacancy and Wage Survey | JVWS |
| Canadian Survey of Consumer Expectations | CSCE |
| Business Outlook Survey | BOS |
| Fall Economic Statement | FES |

**Forms we do not use, ever.**

- "Stats Can." Never. It is "StatCan" or "Statistics Canada."
- "BOC" (all caps). Always "BoC."
- "the Bank" without prior context. The first reference establishes
  which bank; thereafter "the Bank" is acceptable in a piece
  exclusively about monetary policy.
- "OFSI." It is "OSFI." Memorize.
- "CMHC Canada." Redundant.
- "the central bank" as a substitute for "BoC" in a Canadian piece.
  We name it.

**Big-Six bank names.** RBC, TD, BMO, Scotia, CIBC, National Bank
(or NBC where space is tight). These appear in prose as competitors
to measure against, not as cited sources -- see Section 8 below for
how to phrase. When we name them as institutions (capital flows,
PCL builds, CET1 ratios), they are institutions and the convention
above holds.

**Provincial finance ministries.** First reference: `Ontario's
Ministry of Finance` or `the Ontario Ministry of Finance`. After:
`Ontario Finance` is acceptable. Same pattern for QC, AB, BC.

**Plans and programmes.** IRCC's "Immigration Levels Plan" is
capitalized as a proper noun; "the levels plan" lower-cased on
later reference. `OAS`, `GIS`, `CPP`, `QPP` are acceptable on first
reference without spelling out -- the audience knows.

### 4.1 Source attribution in chart blurbs

**Chart blurbs name the finding, not the source.** The plate's
`source:` field and the canvas source line carry the citation. The
blurb does not repeat them.

- No "per Statistics Canada."
- No "per the Bank of Canada."
- No "the Statistics Canada Labour Force Survey."
- No "released by IRCC."

The reader sees the citation directly below the chart; the blurb's
job is to name what the picture means.

**Narrow exception — series disambiguation.** When a chart shows two
or more series and the prose would be ambiguous without identifying
which one, the **bare series label** may appear. The publisher /
org name still does not.

- Good (two series on the same plate): "LFS-Micro prints 3.1% Y/Y in
  March while all-hourly-wages run 4.5% in April."
- Bad: "The BoC's LFS-Micro series prints 3.1% Y/Y in March, per
  Statistics Canada."

The disambiguation exception is for the SERIES NAME ("LFS-Micro",
"all-hourly-wages", "CPI median", "CPI common"), not the publisher.

### 4.1b Section abstracts under a question header — synthesize, don't recite

**When a section page opens with a question (the page-header headline
question), the blurb directly beneath it answers the question.** The
blurb is a take, not a recitation of the day's prints.

The structure of the page makes the contract explicit: question →
synthesis. The reader sees the question; they expect the next thing to
be the answer, not a three-fact recap of indicators they're about to
see in the plates anyway.

**Banned in section abstracts (the under-question blurb):**

- Three-fact lists where each sentence recites one indicator's latest
  print ("UR climbed to X. Aggregate hours turned Y. Wage growth
  printed Z.").
- "On the data" / "Per the latest releases" / "Recent indicators
  show" openings — they signal a recitation is coming.
- Numbers without an editorial frame around them. Numbers carry the
  argument, but the argument is what they're for, not what they are.

**The form to use instead:**

A 2-3 sentence synthesis that:
1. Answers the question the header asked. (If the question is "how
   tight is the labour market?", the answer is "loose, and loosening
   on the intensive margin first" — not "UR is 6.9%, hours are -0.5%,
   wages are 3.1%.")
2. Names the editorial finding — the take. The reader can disagree
   with a take; they can't disagree with a list of facts.
3. Cites 1-2 numbers that ground the take. Not three. Two at most.
   The supporting numbers re-appear in plates anyway.

**Example pattern:**

> Header question: "How tight is the labour market?"
>
> Bad (three-fact recitation): "Unemployment climbed to 6.9% in April,
> a 0.2pp move that returns the rate to the high end of the recent
> range. Aggregate hours worked turned year-over-year negative at
> -0.5%, the deepest sub-zero reading this cycle. Composition-adjusted
> wage growth printed 3.1% Y/Y in March, up 0.5pp."
>
> Good (synthesis): "Loose, and loosening on the intensive margin
> before headcount. The hours-employment Y/Y spread has been negative
> for more than a year; the UR has crept back up to 6.9% with the
> wage adjustment lagging at 3.1% on the cleaner LFS-Micro series.
> The next BoC move sits on this read."

**Scope:** This rule applies to every section page that opens with a
question header (Labour, Inflation, Housing, Policy, GDP, Markets,
Trade). It applies to the splash hero abstract (Section 8b) by
extension — the splash hero answers an implicit "what's going on?"
question for the whole site. It does NOT apply to plate-level blurbs
(those name plate-specific findings — Section 4.2 below).

### 4.1c Hardcoded benchmark constants need a source-card

**Any benchmark number typed as a literal — in chart-component code or
in prose — that is cited as a fact (the BoC's potential output growth
estimate, neutral range, the Fed funds target, an inflation control
band, a NAIRU estimate, a productivity-growth assumption) must carry
an explicit source citation alongside the value.**

A literal like `const POTENTIAL_GROWTH_PCT = 1.7;` with a comment that
says "confirm later" is not a source-card. It is a placeholder
masquerading as canon. If the number is good enough to ship on a chart
reference rule or in a blurb sentence, it is good enough to source.

The source-card carries, at minimum:

1. **Publication** (e.g., "BoC Monetary Policy Report, April 2026").
2. **URL** to the published PDF or page.
3. **Page / section reference** so a verifier can find the exact line.
4. **Verbatim excerpt** of the source language supporting the value.
5. **Vintage date** of the source (the report's publication date).
6. **Re-verification cadence** — how often the constant must be
   re-checked (typically each new MPR / quarterly statement / each
   FOMC meeting; pin it to the source's release rhythm).

For chart-component constants, the source-card lives as a comment
block immediately above the `const` declaration. Example:

```ts
// POTENTIAL_GROWTH_PCT — BoC near-term potential output growth estimate.
// Source: BoC Monetary Policy Report, April 2026, Technical Box 1, p. 24.
// URL: https://www.bankofcanada.ca/2026/04/mpr-2026-04-23/
// Excerpt: "Potential output is projected to grow by X.X% in 2026..."
// Re-verify: each new MPR (quarterly).
const POTENTIAL_GROWTH_PCT = 1.7;
```

For prose-only benchmarks (no chart constant), the source-card lives
in the plate's `source:` field alongside the StatCan/BoC table number,
in the same sentence — not in a separate field readers don't see.

**The redraft re-gate rule applies to source-card values, not just
pipeline data.** When a writer redrafts prose that cites a source-card
number, the fact-checker re-verifies the constant against its
source-card source — not against the constant in code (the gate
verifies the constant against the published reality).

### 4.1d Every citation source must be registered

**Three citation source types, no others:**

1. `pipeline:<provider>:<key>` — value flows through the data pipeline.
2. `card:<id>` — primary source registered in `editorial/source_cards/registry.yaml`.
3. `derived` — arithmetic from other tagged claims on the same surface (show the math in the note).

`other:<freeform note>` is BANNED. A freeform note is not a
verifiable source; it's an unaudited assertion in a metadata field.
Past practice used `other:` as the escape valve for sources that
should have been registered, and the result was ~136 claims pointing
at unverifiable freeform descriptions. Every one of those is being
migrated to `card:` (with url + verbatim excerpt + verified_at) or
to `pipeline:` / `derived` where applicable.

Authoring discipline: when you cite a primary source for the first
time, promote it to a registered card BEFORE you reference it.
Adding a registry entry costs about a minute (url, excerpt, dates);
the cost compounds across every future citation of the same source.

The build-time gate refuses `other:` source IDs. The audit pages
flag any non-registry citation in red.

### 4.1e Pipeline citations use slot binding, not hardcoded phrases

For `pipeline:*` and `derived` citations, **do not hardcode the prose
phrase in the citation entry**. Use slot binding instead so the
citation auto-tracks the live pipeline value through every refresh.

**Old pattern (drifts on every refresh — band-aid):**
```js
{ phrase: "2.3% in March", source: "pipeline:statcan:18-10-0004-01", note: "..." }
```

**New pattern (single source of truth — pipeline IS the value):**
```js
{ slot: "cpi_all_items_yoy",
  at: "latest",                       // or "T-1", "T-2", "YYYY-MM"
  value_format: "{0.1}%",              // formatting rule
  context: "in {month}",               // {month}/{year}/{quarter} auto-fill from obs date
  source: "pipeline:statcan:18-10-0004-01",
  note: "Headline CPI Y/Y, latest print." }
```

The build resolves `cpi_all_items_yoy@latest` from
`data/site/panel_data/<section>.json`, formats per `value_format`,
appends `context` (with date-token substitution), and the resulting
phrase ("2.3% in March") is what the audit annotator looks for in
prose. When the pipeline refreshes to April, the phrase auto-becomes
"2.4% in April" — the only thing the author updates is the **prose
number**.

**For derived arithmetic, use `compute:`:**
```js
{ compute: "cpi_all_items_yoy@latest - cpi_all_items_yoy@T-1",
  value_format: "{0.1}-point",
  context: "jump",
  source: "derived",
  note: "Latest vs prior headline Y/Y month-over-month change." }
```

The compute DSL accepts `<slot_key>@<atSpec>` references and basic
arithmetic (`+ - * / ( )`). Anything else is rejected.

**When to keep a literal `phrase:`:**

- Static facts (BoC mandate, historical episode names) — `card:` cited.
- Methodology constants ("rising faster than 3%", "above two thirds of
  the basket") that don't change across refreshes.
- Phrases the author wants to anchor verbatim regardless of pipeline state.

**The reverse-lookup gate** scans uncovered prose tokens against every
slot in `panel_data.json`. If you write "2.3%" in prose but forget to
cite a slot that currently equals "2.3%", the audit flags it with a
suggestion to add the slot binding. This catches "we have a pipeline
that's not currently used by any text" — the inverse drift problem.

### 4.1f-3 Deep-dive cross-links are off limits in blurbs (current rule)

**Current rule (status quo as of 2026-05-13):** no cross-links from
section blurbs, plate blurbs, section abstracts, splash hero, or tile
lines to research deep dives. The blurb makes its macro point itself.
If the point won't fit, cut to a smaller point or rewrite the angle —
never punt to a cross-link.

**Why this rule is in force:** the deep dives currently live as
AI-generated drafts that have not been walked to the user's editorial
standard. Citing them in blurbs would route readers to material the
publication doesn't yet stand behind. Until the dives pass user review,
they don't exist for cross-link purposes.

**Future relaxation (deferred — not in force yet):** when dives are
user-approved and live, the cross-link pattern is likely to be a
single `(Read more →)` link at the END of the blurb, not threaded
into the prose. The blurb still delivers a complete take; the
"read more" affords depth without becoming the argument. The exact
phrasing and placement will be decided then.

**Build-side enforcement (to add):** the audit gate should refuse a
blurb containing an `/research/<slug>/` href when the dive is in
`_holding` / has no live `publishedPath` in `sections.ts`. Until then,
the style and surface-fit gates catch deep-dive references in any
form and fail the surface.

### 4.1f-2 The three-surface stand-alone test

Every plate has three surfaces a reader could land on: the **title**
(plate hed), the **chart** (the visual), and the **blurb**
(`interpretationHtml`). Each one must work on its own.

**The test:** if a reader only saw the heds across the page, would
they walk away with a pretty good understanding of the section? If
they only saw the charts? If they only read the blurbs? All three
yes.

**Implications:**

1. **The blurb is not a caption.** It does not exist to describe the
   chart, count its bars, or label its axes — those are the chart's
   job. The blurb is an independent synthesis that argues the SAME
   underlying claim the chart shows, in prose. A reader who can't see
   the chart still gets the take.
2. **The chart is not just an inventory.** Its layout, labels, and
   annotations should make the editorial argument visible at a glance,
   so a reader who skips the blurb still gets the take.
3. **The title is not a description of the chart.** It names the
   finding so a reader who only scans the heds across a page still
   gets the section's overall story.

**Consequence for multi-panel charts (the small-multiples case — BoC
balance sheet panels, CPI sub-aggregate breakdown, industry GDP split,
etc.):** the blurb selects what to argue, the chart inventories what
exists, and they reinforce each other. The blurb is not delinquent for
omitting components the chart shows; that's the chart's job. The blurb
IS delinquent if it lists components instead of arguing the signal.

**Four common signal patterns for multi-panel selection:**

- **Dominant component** — one item is the story (a structural anchor,
  the source of change). Name it; the rest are silent or absorbed.
  Example: "Government bonds carry the balance sheet; the rest is
  operating margin."
- **Active mover** — one component changed materially; others held.
  Name what moved. Example: "Food and energy now carry the inflation
  overshoot that shelter used to."
- **Rotation** — two components flipped roles. Name the rotation.
- **Regime** — all components share a state (everything at a floor;
  everything above trend). Name the regime, not the inventory.

**The selection is a judgment call**, and the judgment changes by
cycle. The discipline isn't a fixed rule about which numbers belong;
it's: before drafting, ask "if the reader only saw my blurb, what's
the single thing they walk away with?" That's the take. Ground with
1-2 numbers; let the chart carry the inventory.

### 4.1i Take-mechanism-land: the structural pattern of a working blurb

Every blurb on Sibley Creek — section abstract, plate blurb, splash hero — follows a three-beat argumentative structure. The user's working blurbs (output, inflation, labour) all share it. The pattern that fails (policy round 1) is the inversion: opener + list of facts + free-floating close.

**The pattern:**

- **Sentence 1 — the take.** A single declarative claim that answers the page-header question. Names the regime, the turn, the tension. Reader can disagree; reader cannot mistake what's being argued.
- **Sentences 2 to 3 — the mechanism.** Explain WHY the take is true. Composition, sequence, anchor, contrast. NOT new adjacent facts about the same topic. The middle is in service of the opener.
- **Optional close — the landing.** A short sentence that either extends the argument (one implication, one anchor) or lands it with finality. Earns its place by saying something the middle hasn't.

**Working exemplars** (live blurbs as of 2026-05-13):

> Labour: *"Yes, and the intensive margin is leading. Hours worked are running negative year-over-year while the unemployment rate has drifted up to 6.9%, the pattern of a market that is shedding work before it sheds workers — and one where a population surge is being absorbed straight into not-in-labour-force rather than into jobs. Wages are the lagging piece, with composition-adjusted growth at 3.1% still above where the Bank of Canada wants it, but the cyclical direction is no longer in doubt."*

> Inflation: *"Headline CPI sits at 2.3% — a hair above target, with food and energy now carrying the overshoot that shelter used to. Core-trim and core-median, the measures the Bank of Canada actually reacts to, are back at 2.2-2.3%. And consumer and firm expectations have moderated together: the anchor is holding while the composition rotates."*

> Output: *"Slowly, and mostly in the resource patch. Real GDP is running near 1% Y/Y, just below the Bank of Canada's 1.2% estimate of near-term potential growth. Oil and gas are doing the heavy lifting while manufacturing is in deep recession. Services growth is trundling along. Even that 1% pace relies on population growth more than anything — on a per capita basis, output is scarcely higher than it was before the pandemic."*

In each: the opener is a take. The middle explains the take (intensive-margin mechanism / composition rotation / resource-patch concentration). The close lands (direction no longer in doubt / anchor holding while composition rotates / per-capita scarcely above pre-pandemic).

**The failing pattern (anti-exemplar):** a contested or weak opener; the middle inventories related facts rather than supporting the opener; the close is a reasonable claim disconnected from what came before. Reads as a status report dressed as an argument.

**The diagnostic test:** read sentences 2-3 out loud. Do they say WHY the opener is true (mechanism, composition, anchor)? Or do they say WHAT ELSE is true about the topic (related facts, level descriptions, adjacent prints)? If "what else," the body is recitation — the blurb has an opener and a close but no middle.

This structure isn't a stylistic preference; it's how readers process editorial argument. A blurb without it isn't a blurb — it's a paragraph of facts with a headline.

### 4.1g The take is at the scope of the header question — synthesis, not enumeration

When the page-header question spans multiple sub-domains, the
abstract's **take** must be at the scope of the question. That is
not a license to enumerate — §4.1b still bans recitation. The take
synthesizes the sub-domains into a single editorial argument.

**Three patterns by how the sub-domains relate:**

1. **Sub-domains agree** → the take IS the shared direction.
2. **One sub-domain dominates the story** → that sub-story IS the take;
   the rest are silent or absorbed.
3. **Sub-domains diverge meaningfully** → the divergence itself IS the
   take, named explicitly.

**Example — policy ("What is Canada's policy stance?"):** policy
covers monetary AND fiscal. If both are accommodative, take = "policy
is accommodative across both levers." If monetary is at neutral and
fiscal is the active mover, take = "fiscal carries the policy story
while monetary holds." If they're leaning against each other, take =
"monetary tightening, fiscal easing — leaning against each other."

**Example — output ("How is the Canadian economy growing?"):** the
question reads on headline GDP, per-capita, industry mix, and the
output gap. If headline is +1.5% Y/Y but per-capita is flat and
manufacturing is in recession, the take is "Canada is growing by
adding people, not by getting more productive" — a take at the full
scope, synthesized from per-capita + industry, with headline as the
contrasting backdrop. Not "headline GDP rose 1.5%; per-capita flat;
manufacturing -6%; output gap -1.0%."

**Anti-pattern — enumeration disguised as synthesis:** "Headline
growth is X, the labour market is Y, inflation is Z, policy is W"
strung together with "and" is still a recitation. A genuine
synthesis names a regime, a tension, or a turn that ALL of those
indicators are facing into.

**Numbers:** 1-2 anchor the synthesis — the ones that best ground
the take. Not one number per sub-domain. The supporting numbers
re-appear in plates anyway.

**Rule:** before drafting, ask "what's the take at the scope of the
question?" — not "what's true in each sub-domain?" If you can't name
the take in one sentence, you don't have one yet.

### 4.1h Comparisons use true superlatives

When a comparison is needed ("widest gap," "deepest decline,"
"largest move"), the phrasing is always a **true superlative**:
"deepest since [year / episode]."

Compute the prior episode by scanning back until you find a reading
that was equal or worse than the current one. That episode anchors
the "since." If the current reading is -150 bps and the most recent
prior reading of -150 or deeper is in 2003, the phrasing is "deepest
since 2003."

**When a recent distortion needs to be excluded:** if the actual
most-recent prior is a brief, named episode the author argues should
be set aside (the pandemic is the canonical case; a temporary spike
in an otherwise stable regime is another), the construction is:

> "deepest since [longer-ago year], excluding [named distortion]"

The "since" still names a true superlative; the carve-out specifies
what window the superlative holds over. Always name what's excluded.

**Never use a "second-X" construction.** Not "second-deepest," not
"second-widest," not "second-largest." If a comparison can only be
expressed as second-place, scan further back for a prior reading
that makes the current a true superlative — or use the carve-out
form with an explicit exclusion.

**Why the no-second-X rule:** "Deepest since X" carries an editorial
argument the reader can dispute or update. "Second-deepest after X"
reads as hedging — concedes the take to the prior episode without
making a claim of its own. The carve-out preserves the superlative
form while staying honest about the recent distortion.

**Example:** if the current BoC-Fed spread is -150 bps and a brief
2025 deepening hit -175 bps before retracing, and 1996-97 ran -251
bps: "deepest since 1996-97, excluding the brief 2025 deepening" —
NOT "second-deepest after the 2025 episode."

### 4.1f Countable claims — pipeline-derived or enumeration-card-validated

Phrases like "fourth consecutive hold," "deepest since Q2 2021,"
"three straight months above 3%" carry counts or "first since" claims
that can't be checked by phrase matching alone. Two anchoring patterns:

**Pattern B — auto-derive from pipeline series** (cardinal form):
```js
{ compute: "count_consecutive_at_latest(overnight_rate)",
  value_format: "{int}",
  context: "consecutive months at the current rate",
  source: "pipeline:boc:overnight_rate",
  note: "..." }
```
Primitives available in the compute DSL:

- `count_consecutive_at_latest(slot)` — successive obs from end equal to latest
- `count_consecutive_above(slot, threshold)` — from end while value > threshold
- `count_consecutive_below(slot, threshold)` — from end while value < threshold
- `prior_above(slot, threshold)` — earliest prior obs date above threshold
- `prior_below(slot, threshold)` — earliest prior obs date below threshold
- `count_enumeration(card_id, after=date?, before=date?)` — count entries
  in a registered card's `enumeration:` list within an optional window

Results are numbers (for counts) or ISO dates (for `prior_*`). The
formatter handles both — `{int}` for counts, `{quarter}`/`{month_year}`
for dates.

**Pattern A — enumeration card + expected_count** (ordinal form, named episodes):
```js
{ phrase: "fourth consecutive hold",
  source: "card:boc_fad_holds_post_oct_2025_cut",
  expected_count: 4,
  note: "..." }
```
The card carries an authoritative list:
```yaml
- id: boc_fad_holds_post_oct_2025_cut
  enumeration:
    - "2025-12-10"
    - "2026-01-28"
    - "2026-03-18"
    - "2026-04-29"
```
The gate validates `card.enumeration.length === citation.expected_count`.
Catches ordinal drift: if a fifth hold is added to the card without
updating prose ("fourth" → "fifth") and `expected_count`, build fails.

**When to use which:**

- B for cardinal counts auto-derivable from a time series — "four
  consecutive holds," "deepest since," "first since"
- A for ordinal counts ("fourth hold," "third straight") OR curated
  lists not in any pipeline series (named recession episodes, election
  dates, FAD calendar windows)

Both eliminate the worst class of bug — fact-checker missing that
"six straight" was actually four — by validating the count at build
time against the underlying data, not by trusting the author's count.

### 4.1k Forecast-language rule — tense and attribution for forward-looking claims

**A forward-looking outcome never appears in bare present indicative as if it were observed fact.** The dividing line is the data vintage: a printed Fiscal Monitor figure is indicative; a budget projection or a PBO outlook endpoint is attributed.

Three acceptable markers:

- **(a) Attribution** — name the source as actor: "Ottawa's plan holds it flat," "the watchdog projects that share climbing to 13%," "the forecast closes the gap," "on the government's plan."
- **(b) Set-to / is-projected constructions** — "was set to reach," "is projected flat," "is on track to" (only when the source itself projects the outcome).
- **(c) Horizon framing inside an already-attributed clause** — "by 2030-31" or "through the decade" alone is NOT sufficient; a year-stamp is not a marker. It must be paired with (a) or (b), or sit inside a clause already marked as a forecast.

Observed/actual data keeps the bare indicative. The rule does not apply to historical prints.

**DO:**

- "Ottawa's plan keeps the ratio flat near 41% through the decade." — (a) marker; "Ottawa's plan" is the actor.
- "The forecast closes the gap from the spending side, returning program expenses below revenue by decade's end." — (a) marker; "the forecast" is the actor.
- "Under the borrowing plan, gross issuance was set to reach near $612 billion in FY2025-26." — (b) marker + absolute FY label; closed-year plan, outturn not yet published.
- "The debt ratio is projected flat, and the watchdog agrees it is." — (b) marker; both Ottawa and the PBO project flatness, neither observes it.

**DON'T:**

- "Issuance drives to a record near $612 billion." — bare indicative on a closed-year plan figure, outturn unpublished. FIX: "was set to reach a record near $612 billion under the FY2025-26 borrowing plan."
- "The trajectory is flat near 41%." — bare indicative on a projected path. FIX: "Ottawa's plan keeps it flat near 41%."
- "By 2030-31, the deficit narrows." — horizon stamp alone is not a marker. FIX: "The forecast narrows the deficit to X by 2030-31."

**Relative time references** ("this year," "this fiscal year") must resolve correctly against the publication date. Federal fiscal years close March 31; a piece published in April or later cannot say "this year" for a figure that belongs to the year just ended. Use absolute FY labels (`FY2025-26`) for fiscal-year data. A closed year's plan figure is past-tense plan ("was set to reach"), never present indicative (the outturn may not yet be published).

**Superlatives on plan figures** are plan-attributed until the outturn confirms: "a planned record," not "a record." If the outturn publishes and confirms, the superlative loses the qualifier.

Note: the countable-claim and citation-binding rules at §4.1e and §4.1f apply to forecast claims identically. A "first since" or "record" on a projection must be anchored via compute DSL or enumeration card — not the author's count against a draft projection table.

### 4.1e Research deep-dive titles — thesis statements, not questions

**A deep-dive title is the piece's thesis, asserted in a declarative
sentence.** It is not a question. It is not a topic label. It is the
finding the dive defends.

The trade dive is the live reference: *"The reorientation has already
happened."* That title tells the reader, before they click, what the
dive is going to argue. The body delivers the evidence.

Rules:

- **Declarative, not interrogative.** "The mortgage renewal wall has
  peaked." Not "Has the renewal wall peaked?"
- **Names the finding.** A title that could front any article on the
  topic is not doing the work. The thesis should be specific enough
  that another writer would arrive at a different one if they read
  the same data and reached a different conclusion.
- **Sentence case.** Capitalize first word + proper nouns only.
- **No terminal period** (unlike chart-plate titles). Deep-dive
  titles read as article headlines in a magazine, not finished
  sentences in a chartbook.
- **Topic anchor + thesis OK** when the thesis benefits from being
  scoped. *"The BoC-Fed divergence is wide, but FX is not binding"* —
  the topic ("BoC-Fed divergence") anchors; the comma-separated thesis
  carries the take.
- **The deck below the title carries the supporting frame.** The deck
  is allowed to be more discursive; the title is not.

Counter-examples to fix on sight:

- BAD: "Mortgage renewal wall: has it peaked?" — question form.
- BAD: "Per-capita output: deceleration or weakness?" — either-or
  framing dodges the thesis.
- BAD: "The Canadian housing market in 2026" — topic label, no take.

The test: read the title aloud. Would a peer hear it as "an
argument" or as "a starting point"? Argument wins.

### 4.2 Methodology in chart blurbs

**The blurb names the finding; the canvas tells the rest.** Do not
describe how to read the chart. The reader can see the chart.

Banned in chart blurbs:
- "Bars show the monthly change in employment (left axis, thousands
  of persons); the line traces the unemployment rate (right axis)."
- "The right panel shows the signed spread each month."
- "Positive bars mean the province is running above the national
  rate; negative bars mean below."
- "The red dot marks the latest print."
- "The three panels show the three buckets the working-age population
  sits in."

What the blurb says instead: the finding the reader is supposed to
take away. "Aggregate hours turned negative Y/Y in April; headcount
is still positive." The picture handles the rest.

---

## 5. Date conventions (consolidated)

- Long-form prose: `May 10, 2026`.
- ISO for data-vintage stamps, file names, footnotes:
  `(vintage: 2026-05-10)`.
- Quarter: `Q1 2026`. Year first elsewhere only in ISO contexts.
- Fiscal year: `FY2025-26` or `fiscal 2025-26`.
- Never `5/10/26`. Never `10/5/26`. The slash-form is banned in
  prose, headlines, chart titles, and table cells.
- Release-cadence phrases: `mid-month CPI`, `first-Friday LFS`,
  `~60-day-lagged monthly GDP`. These are house shorthand; use them.

---

## 6. Common edits to avoid

### Clichés to cut, with no exceptions

- "the everything bubble"
- "this changes everything"
- "shocking," "stunning," "jaw-dropping," "eye-watering"
- "Canada's Lehman moment"
- "the wheels are coming off"
- "the elephant in the room"
- "kicking the can down the road"
- "the perfect storm"
- "uncharted territory"
- "new normal"
- "soft landing" (overused; if we mean it, define what we mean by it
  -- per-capita GDP, unemployment, CPI -- and then it is allowed,
  once, with the definition)
- "hawkish hold" / "dovish hold" (jargon shorthand; describe what
  the BoC actually did)
- "the consumer is resilient" / "the consumer is cracking" (the
  consumer is not a person; describe the actual variable -- retail
  sales volumes, real disposable income, the saving rate)
- "Bay Street says" as a substitute for naming the source. Either we
  cite (and we do not, for banks), or we triangulate the aggregate
  forecaster median -- see Section 8.

### Hedging tics, banned

- "Arguably." If you have an argument, make it. If you do not,
  delete the sentence.
- "Some would say."
- "It could be argued."
- "In some sense."
- "It is perhaps worth noting."
- "Interestingly." If it is interesting, the reader will find it so
  without being told.
- "Of course." Either it is of course, in which case cut the
  sentence, or it is not, in which case do not pretend.
- "Needless to say." Same.
- Stacked qualifiers: `may potentially possibly suggest`. Pick one
  qualifier or none.

### The difference between hedging and calibrated uncertainty

Hedging covers the writer. Calibrated uncertainty informs the
reader. The difference is whether the reader leaves with a sharper
view.

- Hedging: `Inflation may possibly be on a path that could perhaps
  be consistent with target by year-end.`
- Calibrated: `Headline CPI is on track to hold within 2.0-2.5%
  through year-end if shelter momentum follows the BoC's April MPR
  path; a wage-growth re-acceleration above 4.5% Y/Y is the most
  likely upside risk.`

The second is longer, but every clause does work.

### Acronyms and initialisms

**The test: do peers SAY the acronym out loud, or only write it?**
If the acronym is how people actually talk to each other, it earns
a free pass. If it's written-only shorthand, expand it in reader
prose (it can still ride in labels, citations, and tight chart
slots where space is the constraint).

**Free pass (use in reader prose, no expansion needed):**

- CPI, GDP, EI, USDCAD — said out loud, recognized broadly.
- BoC, Fed, StatCan, OSFI, CMHC, CREA, IMF, OECD, PBO, CBA, FRED,
  ECB, BoE, BoJ — proper-noun institutions; these ARE the names
  people use.

**Always expand in reader prose** (OK as labels / citations / tight
chart slots):

- HPI -> "home prices" (the HPI is the measurement tool; "home
  prices" is the concept the reader thinks about). "MLS HPI" is
  fine as a citation suffix.
- SAAR -> "annualized" or "Q/Q annualized." "SAAR" is fine in a
  chart-axis subtitle or a callout unit.
- SNLR -> "sales-to-new-listings."
- FCI -> "financial conditions" (or "financial conditions index"
  when that distinction matters).
- OAS -> "spreads" or "credit spreads."
- NPR -> "net non-permanent residents" (do not let "NPR" stand
  alone; ambiguous with National Public Radio).
- RMIR / RMS -> describe the data ("CMHC's residential mortgage
  industry report" / "CMHC Rental Market Survey").
- MIC -> "mortgage interest cost."
- V/U -> "vacancy-to-unemployment ratio."
- CET1 -> "common-equity tier-1 ratio" on first use.
- IG / HY (corporate spreads) -> "investment-grade" /
  "high-yield" in prose; IG / HY OK in chart axes.

**Audience-dependent (expand on first reader-facing use, then OK
as shorthand inside a single piece):**

- LFS -> "Labour Force Survey" on first use.
- MPR -> "Monetary Policy Report" on first use.
- BOS -> "Business Outlook Survey" on first use.
- CSCE -> "Canadian Survey of Consumer Expectations" on first use.
- FES -> "Fall Economic Statement" on first use.
- DSB (OSFI) -> "Domestic Stability Buffer" on first use.

**Where the rule does NOT apply:**
- The `indicator` field on a section-page plate (tight label).
- Source citations ("Source: CREA MLS HPI" stays as the proper
  series name).
- `chartSeriesKey` and other internal data shapes.
- Y-axis units / chart-axis subtitles where space is constrained.
- Pipeline code, design docs, internal markdown drafts.

### Clipped abbreviations — write the full word

**Don't truncate words mid-syllable in prose.** "Reaccel" for
reacceleration, "decel" for deceleration, "infl" for inflation
read as trader-desk shorthand, not editorial prose. The full word
is two extra characters and ships finished work.

This applies to reader prose, chart blurbs, plate titles, decks.
It does NOT apply to chart-axis labels or tight slot text where
space is the binding constraint.

Examples:
- BAD: "Cores are showing signs of reaccel."
- GOOD: "Cores are showing signs of reacceleration."
- BAD: "The decel into Q4 looked real."
- GOOD: "The deceleration into Q4 looked real."

### Inflation-measure naming

**"Core measures"** is the canonical umbrella term for the BoC's
trimmed-mean (CPI-trim), weighted-median (CPI-median), and common-
component (CPI-common) measures. "Core trio" works when all three
are charted.

**Do NOT** call the pair (trim + median) "trimmed-mean cores" or
"the trimmed cores" — CPI-median is a weighted-median measure, not
a trimmed mean. The label is factually inaccurate.

Correct usage:
- "Core measures held above the 2% midpoint..."
- "CPI-trim and CPI-median both ran at 2.8%..."
- "The trimmed-mean measure stepped up to 2.9%..." (referring
  specifically to CPI-trim alone)

### Jargon-as-armor, cut

- "Optionality" (in any prose context that is not a derivatives
  primer)
- "Constructive" (used as a euphemism for "we are not sure but
  leaning bullish")
- "Cautiously optimistic"
- "Wait-and-see"
- "Watching closely"
- "On our radar"
- "We continue to monitor" (then do, and write when you have
  something to say)
- "The setup" / "the tape" / "the tape is constructive"
- "Risk-on" / "risk-off"
- "Bid for duration"
- "Goldilocks"
- "Soft data" vs. "hard data" (sometimes useful; if used, define
  what falls in each)
- **The L-B compound** (the word *load* joined by hyphen to the word
  *bearing*). Banned across the project — reader copy, internal
  canon, agent files, code comments. The phrase became a tic and lost
  its meaning through overuse. Substitute the plain phrase
  that fits the sentence: **the central claim** / **the claim that
  carries the argument** / **the anchor claim** for a claim; **the
  central fact** / **the key fact** / **the fact this turns on** for
  a fact; **the read** / **the signal** / **the actual story** for a
  read; **the variable that matters** / **the binding variable** for
  a variable; **the primary chart** / **the chart this section turns
  on** / **the anchor chart** for a chart; **the central question** /
  **the question that anchors** for a question; **the central print**
  / **the anchor print** / **the print that matters** for a print.
  If a sentence reads poorly after substitution, rewrite the
  surrounding clause; do not preserve the phrase by quoting or
  italicizing it.

### Constructions to rewrite

- Passive when an actor exists: `Rates were raised` -> `The BoC
  raised the overnight rate.` Passive is fine when the actor is
  unknown or the variable is the subject of the sentence (`Rents
  rose 4.2% Y/Y`).
- Nominalizations: `provided an indication of` -> `indicated`.
  `Performed an assessment of` -> `assessed`. `Made a determination
  that` -> `determined.` Cut the noun, use the verb.
- "There is" / "there are" openings: `There are three sources of
  upside risk` -> `Three sources of upside risk stand out.`
- "Going forward." Cut. It almost always means "in the future,"
  which a verb tense already provides.
- "At the end of the day." Cut. Always.
- "In terms of." Almost always replaceable with "on" or "for."
  `In terms of inflation` -> `On inflation`.

### Spelling traps (Canadian)

We follow Canadian English. The Globe style guide is the tiebreaker
when StatCan and BoC usage diverge.

- labour, neighbour, behaviour, vapour, harbour
- centre, theatre, fibre, metre (the unit); meter (the device)
- programme (when referring to a scheme or initiative); program
  (computing). The Globe is shifting toward `program` for both;
  we use `programme` for policy initiatives and `program` for
  software, with `programme` as the default tiebreaker.
- defence, offence, licence (noun) / license (verb), practice (noun)
  / practise (verb)
- -ize endings for most cases per BoC and StatCan: organize,
  recognize, normalize, harmonize, criticize. (-yse vs -yze: analyze.)
- modelled, modelling, travelled, traveller, fuelled (double-l in
  Canadian)
- cheque (the bank instrument), not check
- enrol, enrolled, enrolment
- judgement (general usage) / judgment (legal contexts)
- aluminium is British; aluminum is Canadian-and-American. Use
  aluminum.

When in doubt, the Globe and Mail style guide is the working
tiebreaker; the Canadian Press Stylebook is the backstop.

---

## 7. The two voice modes

The dashboard ships two distinct prose registers. Both are Canadian.
Both are numerate. Both follow Sections 1-6 above. They differ in
who is talking and what they are allowed to do.

### Mode A: Automated event-blurb voice

**Where it lives.** The basics-layer print blurbs that fire on
release: CPI, LFS, monthly GDP, quarterly GDP, BoC rate decisions,
trade balance, fiscal monitor. Two to four sentences. Generated
automatically against a template; tuned by writer; polished by
style-editor; reviewed by the editorial-director.

**What it sounds like.** A wire-service lede written by someone who
respects the reader. Primary source, primary number, primary
comparator, plus the one observation that a chart cannot make.

**Rules of the road.**

- Lead with the print: variable, value, period.
- Second sentence: comparator -- prior print, consensus, or BoC
  projection. Surprise framing per Section 8.
- Third sentence (optional): the one structural observation -- the
  breadth, the composition, the divergence -- that the chart does
  not show on its own.
- Fourth sentence (optional, rare): the next data point that
  matters and why.
- No editorial. No "we think." No "watch for." No "this suggests
  the BoC will." That is deep-dive territory.
- No clichés (Section 6). No hedging tics. No jargon-as-armor.
- Pure declarative. Past tense for the print, present tense for the
  state, future only when the calendar is the subject (`The next
  print lands June 18`).

**Example -- good.**

> Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from
> March and 0.1pp above the Bloomberg consensus of 2.2%. Core-trim
> held at 2.7% and core-median ticked down to 2.8%. Shelter
> contributed 1.1pp to the headline, with mortgage-interest cost
> continuing its mechanical fade. The next print is June 24.

**Example -- bad (do not ship).**

> April's CPI report was a bit of a mixed bag, coming in slightly
> hotter than some had expected, though core measures suggested the
> underlying picture remains broadly consistent with the Bank's
> path. Goldilocks may yet hold. Watch shelter.

The second version commits four sins in four sentences: a cliché
("mixed bag"), a hedge ("a bit of," "slightly," "some had
expected," "broadly consistent"), a cliché ("Goldilocks"), and a
piece of editorializing ("Watch shelter") that the blurb voice is
not allowed.

### Mode B: Deep-dive voice

**Where it lives.** The eight pillars (Section 5 of
`dashboard_purpose.md`) and any future deep dives. Typical length is
**1,000 to 1,750 words** (a 4-7 minute read). Reasoning: the
publication's primary distribution is LinkedIn to a credentialed-
but-skim-first audience; longer than ~1,750 words bleeds attention
without proportional argument-gain. A piece that needs to run longer
should be split into a sequence rather than scoped wider — one piece,
one argument, one sit.

If a piece is running past 1,750 words, the right cut is structural:
delete a supporting sub-thesis, do not line-edit. Length without
weight is verbosity.

**What it sounds like.** A senior Canadian economist writing for a
peer at CPP Investments. Argument-bearing. Willing to take a side.
Willing to say "we do not yet know" and name what would resolve it.
Willing to disagree with the Bay-Street consensus, name the
disagreement, and name the falsification trigger.

**Rules of the road.**

- The opening paragraph states the question and the answer. Not
  the question and three other questions. The answer can be "we do
  not yet know -- here is the cheapest test that would resolve it,"
  and that is a finished opening.
- One argument per piece. Sub-arguments support; they do not
  compete.
- Cite primary sources in running prose. The Big-Six are not
  sources (see Section 8). The MPR, StatCan tables, OSFI bulletins,
  CMHC reports, IMF Article IV, OECD Economic Survey, C.D. Howe BCC
  communiques, BIS quarterly review -- these are.
- Name what would change our mind. Every central call has a
  falsification trigger.
- Sentence length varies. Paragraph length stays short (Section 2).
- Numerate. Every number that carries the argument has a citation one
  click away. Constructed series have a methodology note.
- The closing paragraph is the call and the watchpoint. Not a
  summary of the piece. Not "in conclusion." The call and the
  watchpoint.

**Example opening -- good.**

> The mortgage-renewal wall has peaked. Of the roughly $1.1 trillion
> in residential mortgage debt outstanding at the end of 2023, the
> peak of the renewal-payment-shock distribution passed in late
> 2025; the residual through 2027 is meaningful but mechanical.
> This piece argues two things: first, that the median 2026
> renewer faces a 14 to 22 percent payment increase rather than the
> 30 to 40 percent figure that dominated 2024 commentary; second,
> that the channel through which the residual matters for the BoC
> is no longer aggregate consumption but the regional dispersion of
> distress.

**Example opening -- bad.**

> The mortgage renewal wall has been a major topic of discussion
> for some time now, and there are many different views on where
> we go from here. Some commentators have argued that the worst is
> behind us, while others remain concerned. This piece will explore
> some of the key issues.

Bad version: no claim, no number, no Canadian specificity, no
direction. A reader has nothing to disagree with, which means they
have nothing to read.

### Headlines and chart titles

Headlines: deep-dive voice. Active, declarative, specific. Sentence
case. No clickbait constructions ("You will not believe").

- Good: `The renewal wall has peaked; the residual is regional`
- Good: `Per-capita GDP is rising for the wrong reason`
- Good: `Canadian goods exports to the US: still 73%, still falling`
- Bad: `Mortgage renewals: what you need to know`
- Bad: `A deep dive into Canadian housing`

Chart titles: blurb voice. Descriptive, not editorial. The chart
shows what it shows; the annotation says what it means.

- Good (title): `MLS HPI benchmark, six CMAs, Y/Y`
- Good (annotation in callout): `Toronto and Vancouver leading the
  national turn`
- Bad (title): `Toronto and Vancouver are leading the housing turn`

---

## 8. Consensus and surprise prose

Per the editorial decision recorded in the 2026-05-10 changelog of
`dashboard_purpose.md`: market consensus (Bloomberg / Reuters
median, or aggregated forecaster median where the paid feed is
unavailable) is a **derived numerical input** to our surprise
framing, not a **cited authority**. The voice principle that we do
not cite Big-Six economics in running prose applies to citation, not
to forecast aggregation.

This section is how to phrase the distinction.

### How to say "consensus expected X"

Good -- consensus as derived numerical comparator:

- `0.1pp above consensus.`
- `In line with the Bloomberg median of 2.2%.`
- `The print came 5 bps tighter than the forecaster median.`
- `2.3% Y/Y, against a consensus 2.2% and a BoC April MPR
  projection of 2.4%.`
- `The aggregated forecaster median sat at 2.2% going into the
  print.`

The convention: name "consensus" or "the forecaster median" or "the
Bloomberg median" as a number, attached to a comparison. Do not
attribute it as a view.

### How not to say it

Bad -- consensus as cited authority:

- `RBC expected 2.2%.` (Big-Six citation; banned)
- `TD's call of a 25bp cut was vindicated.` (Big-Six citation;
  banned)
- `The Street was looking for 2.2%.` (`The Street` is a US
  construction and a vague-source dodge; banned)
- `Most economists thought the BoC would cut.` (Vague-source dodge;
  banned)
- `Scotia and BMO had flagged the upside risk.` (Big-Six citation;
  banned)

The pattern to break: any sentence that treats a Big-Six desk as a
named view to be agreed or disagreed with. The aggregated median
enters as a number; the individual desks do not enter as voices.

### When the consensus is the story

Sometimes the dispersion of forecasts is itself informative -- a
particularly wide range, a strong skew, a known outlier desk. The
dispersion can be reported as a number without crossing into bank
citation:

- `Forecaster range was 1.9 to 2.5%, the widest in nine months.`
- `Six of the seven Canadian forecasters in the Bloomberg survey
  had the cut; one held.`
- `The forecaster median has shifted from 2.7% in February to 2.2%
  by April, tracking the soft shelter prints.`

These are descriptions of the distribution of inputs, not citations
of opinions.

### When the BoC's MPR is the comparator

If market consensus is genuinely unavailable for a series, the BoC
MPR central projection is the fallback anchor. Phrase it with the
vintage:

- `Against the BoC's April MPR projection of 2.4%.`
- `0.2pp below the BoC's January MPR path.`

The MPR is a citation, not just an input -- so it is named directly
and dated.

### The BoC's own surprises

When we discuss the BoC's reaction function, we can describe what
the BoC has signalled, what it has done, and the gap. We do not
need a Big-Six intermediary to describe a BoC surprise:

- `The BoC cut 25 bps, against a Summary of Deliberations two
  weeks prior that had flagged "more patience" as the dominant
  view -- a notable shift.`
- `Market pricing implied a 38% probability of a cut going in; the
  cut landed.` (Market pricing is data, not opinion.)

---

## 8b. Splash hero abstract — the take, written last

### What the hero abstract is

**A take on the Canadian macro picture as a whole — not a status
report.** Two to three declarative sentences (hard cap five) that state
the editorial argument about where the cycle is and what's driving it.
**Length budget matches the topic-page section abstract** — the hero
answers a question with a take at the whole-economy scope, same shape
as a section answers at section scope. A heavier hero pushes the splash
tile lines below it down and unbalances the page. Numbers earn their
place ONLY when they ARE the take (a level crossing, a regime
shift, a structural fact that anchors the argument). Most data belongs
in the section tiles below where readers can scan it directly.

**The live reference for voice and structure** (current as of
2026-05-11):

> Cyclically, Canada is slowing down. Disinflation is in the final
> mile and slack is building in the labour market. Structurally, the
> economy is readjusting to halted population growth and tariffs.
> Per-capita output is virtually flat since 2019; the US export share
> has fallen from three quarters to two thirds over the last year.

**Shape that lands a take:**

- Sentence 1: the thesis in one declarative line (the cyclical or
  cycle-level read).
- Sentence 2: one supporting beat — what cyclical evidence backs the
  thesis.
- Sentence 3: the pivot — what the structural / second-order story is.
- Sentence 4 (and optionally 5): one or two concrete structural facts
  that ground the pivot.

**What to cut from a draft hero abstract:**

- Status-report openings ("Headline CPI firmed back to 2.3%...").
- One sentence per section (a four-fact recitation across four sections
  with no editorial thread).
- Microscale numbers that belong on section pages (specific
  percentiles, basis-point spreads, deltas-vs-prior).
- Any sentence that could appear unchanged on a section tile below.
- Hedge clauses ("though"... "but"... "with the caveat that...").

**The test:** read the hero by itself, without the section tiles below.
Does the reader walk away with a VIEW, or with a list of recent prints?
If the latter, rewrite from the thesis down.

### Ordering rule: hero is last

When a blurb pass writes the splash page (the hero abstract paragraph
plus the seven section blurbs), **the hero abstract is the LAST piece
written, not the first.** The seven section blurbs are authored first;
the hero abstract is then synthesized from them.

**Why.** The hero abstract is a publication-frontmatter paragraph that
names the state of the Canadian cycle. The cycle reads as the
aggregate of what each section is saying that day. Writing the hero
first means guessing at the cycle-level read before the section reads
are pinned. Writing it last means the hero can pull the central fact
from each section blurb and stitch a single coherent cycle paragraph
from real, vetted section-level reads.

**Practical sequence for a writer / pipeline dispatch:**

1. Author all seven section blurbs against pipeline data. Vet each.
2. Once the seven are stable, read them as a set and identify the
   anchoring cycle theme (loosening? tightening? mixed? where is the
   headline tension?).
3. Author the hero abstract drawing from the section blurbs' actual
   facts. Do not introduce a new claim in the hero that isn't
   surfaced or implied by at least one section blurb beneath it.

A hero abstract that contradicts the section blurbs below is a bug;
the ordering rule prevents it. If a writer finds themselves unable to
write the hero because the sections "don't agree," that's diagnostic
information — write what's true about the disagreement.

This rule applies to both Mode 2 automated and human-led blurb passes.
The auto-blurb pipeline (when it runs autonomously on release days)
must order its dispatches accordingly: section-level blurb generation
fires per-section on each release, but the hero-abstract regeneration
is gated on having ALL seven current-cycle section blurbs in hand.

## 8c. Citing third-party research providers

**Three modes for how a third-party source can appear in our prose.**
The mode determines the bar.

### Mode 1 — Fact citation

A claim that *X is the case*, sourced from a primary document or
triangulated across credible secondaries. The standard process: card
in `editorial/source_cards/registry.yaml`, `verification_tier` of A
(primary verified) or B/C (secondary triangulated, user-approved).
See `editorial/review_protocol.md` for the full tier mechanics.

Bank economics desks do not appear in Mode 1. They are not
fact-reproducers; they are competitors. See
`editorial/credible_secondaries.md` for the explicit exclusion.

### Mode 2 — Consensus framing

When the editorial point is what the private sector collectively
expects, an aggregated range or median across forecasters is the
citation, with no single forecaster named as authority.

GOOD: *"Private-sector forecasters see growth between 1.0% and 1.8%
next year."*

GOOD: *"Consensus expects 25 basis points of further easing through
year-end."*

BAD: *"TD Economics sees growth at 1.4% next year."* (Single desk
named as authority — wrong mode. Either aggregate it into a consensus
range, or treat as Mode 3 with the appropriate framing.)

Always say "consensus" or "private-sector forecasters" — never
"Big-Six median" or any phrasing that names which desks were
captured. The aggregation is the citation; which banks happened to
contribute it on a given cycle is implementation detail. See
memory note `feedback_consensus_labelling.md`.

### Mode 3 — Analysis citation

When a single third-party — typically a bank economics desk, a peer
research provider, or a named analyst — has published something
genuinely unique that becomes the subject of editorial discussion.
The claim is what they argued, not what is true.

**The frame test.** Read the sentence aloud. Replace "X argues Y"
with "Y is true." Does it still work? If yes, the framing is honest
analysis citation. If you'd lose the editorial punch by adding "X
argues" to it, the claim is being smuggled in as fact when it isn't.
Either reframe or cut.

GOOD: *"CIBC has argued that StatCan may be undercounting the
population by as much as a million; the agency rejects the
estimate, but the question is alive in the debate over the
population denominator."*

GOOD: *"BMO Capital Markets argued in March that the BoC would
hold through Q2, against a consensus that had been pricing
further cuts; the call has so far proved correct."*

BAD: *"Canadian housing is undervalued, according to CIBC
Capital Markets."* (Reframable: either cut, or rewrite as
*"CIBC Capital Markets has argued Canadian housing is
undervalued, citing X. Whether the methodology travels is
unsettled."* — but at that point, ask whether the claim is worth
elevating at all.)

**Rules for Mode 3.**

1. **Frame as claim, not fact.** Use "argues," "has argued,"
   "argued in [date]," "estimates," "projects." Never "X says Y
   is true" or "Y, per X."
2. **Name the analyst, the institution, and the date.**
   Institution-only is too cheap; "CIBC says" reads as fact.
   "Avery Shenfeld at CIBC, August 2023" reads as a specific
   claim from a specific person at a specific moment.
3. **Make it editorial discretion.** Mode 3 is reserved for cases
   where the third-party's claim is genuinely unique, materially
   relevant to the macro picture, and worth the reader's
   attention. Not every interesting bank-desk forecast qualifies;
   most don't. The bar is "is this analysis the news?"
4. **User approval before shipping.** Mode 3 citations cannot ship
   without the user (Jay Zhao-Murray) explicitly approving the
   specific use. The candidate card lands in
   `editorial/source_cards/_pending/<surface>/<id>.yaml` with
   `mode: 3` and an empty `user_approved_at` field; the writer's
   draft holds the placeholder in `editorial/drafts/_holding/`.
   The build-time gate refuses Mode 3 cards without
   `user_approved_at` and `user_approved_by`.
5. **When in doubt, cut.** Mode 3 is a narrow exception. The
   publication's positioning is independent research, not a digest
   of what competitors are saying. Default: don't cite. Citing
   them routinely makes us a news site about them, which is not
   what we are.

### Where third-party citations fail

Some claims will be genuinely interesting and materially relevant
but the third-party's analysis cannot be triangulated to a primary
chain — the analyst published something, no one else has reproduced
it, and the claim is paywalled or otherwise inaccessible. Under our
rules, that claim does not ship. The discipline isn't about
softening the language to a defensible hedge ("CIBC may have
argued..."); the discipline is to cut the claim entirely. Sibley
Creek's positioning is built on every claim being verifiable. A
claim we cannot verify is one we don't make.

## 9. Working notes for style-editor

**Concision is the core discipline.** Every word, every sentence,
every paragraph must earn its place. The style-editor's
default move when uncertain is to cut. Length without weight is
flab; flab dilutes voice; voice is the publication's edge. If a
sentence can be removed without changing the editorial claim, remove
it. If a paragraph can be reduced to one sentence, reduce it. If a
word can be cut without loss, cut it.

A short list of edits I make most often, recorded here so the
writer can pre-empt them.

1. Cut "going forward."
2. Cut "interestingly."
3. Replace "There are X factors that..." with "X factors..." and
   start the sentence with the noun.
4. Replace nominalizations with verbs.
5. Split paragraphs at the "but" or "however."
6. Hyphenate compound modifiers before nouns; do not hyphenate
   after.
7. Push the clause that carries the claim to the front of the sentence.
8. Replace "Bay Street consensus" used as a citation with the
   aggregated forecaster median used as a number.
9. Replace `BOC` with `BoC` and `Stats Can` with `StatCan` on
   sight.
10. Reject "soft landing" unless the writer has defined the
    landing.

When my edits change emphasis or structure (not just mechanics), I
mark them and route back to writer. When prose conflicts with a
fact, I escalate to writer / researcher -- I do not rewrite the
fact.

---

End of style guide.

This file is owned by style-editor. Revisions are noted in the
changelog below; substantive voice changes route through
editorial-director.

## Changelog

- 2026-05-10: Initial version. style-editor.
