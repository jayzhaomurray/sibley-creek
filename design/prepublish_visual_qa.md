# Pre-publish visual QA - macro-research-department

Status: blessed. Author: art-director. Date: 2026-05-11.
Audit target: dist/ as of 2026-05-11 build. Vignelli canon (design/design-system.md v1.0).

This is the pre-publish sweep. It excludes work already in flight in the two
parallel dispatches (backend numeric formatter; chart-builder frontend formatter +
PanelLiveChart label-overflow). It covers everything else.

---

## 1. Executive summary

Verdict: **DO NOT ship as-is.** Fix the 4 CRITICAL issues plus 6 HIGH issues
before the site goes public. Total: **10 issues** to clear pre-publish; the
remaining 12 MEDIUM/LOW items are post-publish cleanup.

Severity counts:

| Severity   | Count | Disposition           |
|------------|-------|-----------------------|
| CRITICAL   | 4     | Block publish.        |
| HIGH       | 6     | Block publish.        |
| MEDIUM     | 8     | Post-publish sweep.   |
| LOW        | 4     | Defer to v1.1.        |

**Top 3 CRITICAL issues** (the ones a Bay Street reader will pattern-match on
in the first 10 seconds):

1. **Literal "TK" strings rendered in pure ink across every section page.**
   Section-page plate `asOf`, `title`, `interpretation` prose, and `callout`
   value/unit/delta fields contain the journalism convention "TK" hand-typed
   into the .astro files (e.g. `asOf: "TK"`, `value: "TK"`, `unit: "TK"`).
   The publication has a global "Series are placeholder values" footer
   disclosure, but the cell-level TKs render in the same Plex Mono pure-ink
   weight as a real `2.3%`. A Bay Street reader scanning a CPI plate reads
   "Headline CPI printed TK y/y" as a typo or a broken substitution. This is
   the largest single trust-leak surface in v1. Files: every `src/pages/*.astro`
   plate body. Fix brief in Section 4.
2. **Homepage date "May 11, 2026" rendered in MTA red.** The
   `vig-title__h-date` span pulls `color: var(--accent)` in TitleStatement.astro
   line 144. The canon's Section 3 lists the eight permitted MTA red moments
   (figure number, plate number, section number, latest dot, focus ring, link
   hover, selection, brand kicker tokens). A date on the homepage hero is none
   of these. The red drains the rationing budget on the page's most-visible
   surface. Fix: drop to pure ink, OR re-cast as a permitted brand kicker
   token (the canon already covers `INDEPENDENT` and `PROUDLY CANADIAN` -
   the date is not a kicker, so the cleaner fix is pure ink).
3. **Homepage panel data leaks: indicators with `value: "TK"` in
   `data/site/sections.json` render the literal string "TK" in real-data
   Plex Mono ink in the indicators table.** The pipeline emits 6+ such rows
   (e.g. GDP "Per-capita GDP, y/y", inflation "CPI breadth >3%", labour
   "Per-capita employment, y/y", housing "CMHC arrears rate", housing "Months
   of inventory"). The enrichment in `src/data/site_data_loader.ts` checks
   `value.length > 0` and passes "TK" through as a real value rather than
   coercing to null, so the placeholder gray styling never engages. The
   `available: false` flag the pipeline already emits is the right signal to
   coerce these rows. Fix brief in Section 4.
4. **Homepage `DeepDivePanel` "Coming soon" stamp renders in pure ink, not
   placeholder gray.** The unpublished-piece stamp uses class
   `.vig-dd__stamp-body--tk` but no matching CSS rule exists in
   DeepDivePanel.astro (the rule was added to research/index.astro but not
   here). Result: "Coming soon" reads at the same weight/color as a real
   "Published May 14, 2026" date, leaking the placeholder status. Fix in
   Section 4. The research index page has the same `--tk` class with the
   correct gray rule - copy that.

---

## 2. Per-route findings

### 2.1 / (homepage) - dist/index.html

- **CRITICAL.** Date in `--accent` red. See Section 1 issue 2.
  File: `C:\Users\jayzh\projects\macro-research-department\src\components\home\TitleStatement.astro:144`.
- **CRITICAL.** "Coming soon" stamp in DeepDivePanel renders in pure ink.
  See Section 1 issue 4. File:
  `C:\Users\jayzh\projects\macro-research-department\src\components\home\DeepDivePanel.astro:104`,
  CSS rule missing in same file's `<style>` block.
- **CRITICAL.** Sections.json TK leaks: GDP "Per-capita GDP, y/y", inflation
  "CPI breadth >3%", labour "Per-capita employment, y/y" all render the
  literal "TK" in the panel indicators table in real-data Plex Mono ink.
  File: `src/data/site_data_loader.ts:188-205` (enrichPrint).
- **HIGH.** The `vig-title__abs` lorem ipsum on the homepage abstract is a
  prominent paragraph (15px Manrope 200, 64ch). It renders correctly in
  placeholder gray, but its sheer length next to a "Canadian Macro Overview"
  hero headline is visually load-bearing. A Bay Street reader reads ~3 lines
  of "Lorem ipsum dolor sit amet" right under the hero - the placeholder is
  correctly marked, but the editorial vacuum is the first thing the reader
  sees after the hero. Decision needed: writer dispatch for a 2-3 sentence
  hero abstract before publish, OR replace with a Vignelli-disciplined short
  manifesto (~12 words; "Canadian macroeconomics, set in print discipline.
  Charts before columns. Sources at point of use."). Flagged for
  editorial-director; not strictly an art-director fix but flagged here
  because the visual cost is high. File:
  `src/components/home/TitleStatement.astro:67-69`.
- **MEDIUM.** The 3-cell `vig-title__stamp` shows "Headline CPI, y/y" /
  "BoC overnight rate" / "Unemployment rate" with real values; this works.
  But the `--ink-faint` opacity-composition pattern is not used on the
  vertical hairlines between cells - they are pure black at 100%, which
  reads slightly heavier than the spec's intent. Defer.
- **MEDIUM.** Homepage panel mini-charts use 320x180 viewBox and 30px right
  gutter behavior, while canon design-system.md Section 5.1 specs Tier-2
  MiniChart at 248x72 with 32px right gutter. The production panel is
  closer to a Tier-3 inline chart squeezed to tile scale. This is acceptable
  v1 drift (the tile chart is editorially larger than a sparkline; it
  carries 24-month history) but the canon should be updated to bless the
  homepage-panel-chart tier explicitly, or the homepage panel chart should
  be tightened to 248x72. Recommend documenting as Tier 2.5 in the canon
  (post-publish). File: `src/components/home/SectionPanel.astro:114-119`.
- **LOW.** The 4-panel-wide indicator table cap on the homepage panel
  (4 rows max) is hard-coded by sections.json having 4-6 prints per section.
  Some sections render 4 rows, some render 5-6. This means panel heights
  drift slightly across the 2x4 grid. Acceptable v1 register; the panel
  bottoms are not aligned but the panel grid still reads. Defer.

### 2.2 /inflation/ - dist/inflation/index.html

- **CRITICAL.** Hand-typed TK in every plate's interpretation/title/asOf/
  callout. Six plates affected. Example: plate 1 `asOf: "TK"`, title
  "Headline CPI printed TK in the latest month, TK relative to consensus.",
  interpretationHtml "Headline CPI printed `<strong>TK y/y</strong>`, TK
  relative to consensus...", callout `value: "TK", unit: "year-over-year,
  TK", delta: "TK vs prior"`. Renders in pure ink. File:
  `C:\Users\jayzh\projects\macro-research-department\src\pages\inflation.astro:39-143`.
- **HIGH.** The chartbook-unit eyebrow `As of TK` renders the literal "TK"
  in Plex Mono 12px pure ink right where a reader expects "Mar 2026; released
  Apr 16, 2026". This is the second worst trust-leak on a section page after
  the in-body TKs. File: `src/components/section/ChartbookUnit.astro:127-130`
  - the component receives `asOf` as a string and renders it verbatim; the
  fix is at the call site (the plate definitions) plus a defensive coercion
  in the component (if `asOf === "TK"` render in the placeholder gray class).
- **HIGH.** The `latestReleaseLabel` prop on `SectionLayout` is hand-typed
  `"Headline CPI, TK"` - the SectionPageHeader renders this in Plex Mono
  12px pure ink in the right rail of the headline band, immediately under
  "LATEST RELEASE" micro-caps. The "TK" sits next to a 44px headline
  question ("Is Canadian inflation returning to target?") so the eye lands
  on it. File: `src/pages/inflation.astro:161`.
- **MEDIUM.** Plate 2 interpretation contains "Three-month annualized
  momentum sits a notch above the year-over-year, consistent with a flat
  near-term path." This is hand-authored prose but is also asserting a
  forecast in the absence of real data. Style-editor concern, not
  art-director, but flagged because the visual weight of the prose makes
  the assertion feel authoritative when it shouldn't be in v1. Defer.

### 2.3 /gdp/ - dist/gdp/index.html

- **CRITICAL.** Same TK leak pattern as inflation. Six plates, each with
  TK in asOf, title, interpretation, callout. File:
  `C:\Users\jayzh\projects\macro-research-department\src\pages\gdp.astro`.
- **HIGH.** Same `latestReleaseLabel: "GDP m/m, TK"` leak in the section
  header.

### 2.4 /labour/ - dist/labour/index.html

- **CRITICAL.** Same TK leak pattern. Plus seven plates (one more than the
  other sections), so seven TK surfaces.
- **HIGH.** Same `latestReleaseLabel: "LFS, TK"` leak.

### 2.5 /policy/ - dist/policy/index.html

- **CRITICAL.** Same TK leak pattern across six plates.
- **HIGH.** Same `latestReleaseLabel` leak.

### 2.6 /markets/ - dist/markets/index.html

- **CRITICAL.** Same TK leak pattern across six plates. Markets has the
  highest TK density (every plate's `asOf`, every plate's `value`, every
  plate's `delta`, every plate's `unit` are "TK") because most markets data
  is pipeline-dependent and writers haven't backstopped a single number.
- **HIGH.** Same `latestReleaseLabel` leak.

### 2.7 /trade/ - dist/trade/index.html

- **CRITICAL.** Same TK leak pattern across six plates.

### 2.8 /housing/ - dist/housing/index.html

- **CRITICAL.** Same TK leak pattern across SEVEN plates (Housing has a
  7th plate, Affordability, added in Wave 5).

### 2.9 /research/ - dist/research/index.html

- **MEDIUM.** "Coming soon" stamps render correctly in `--tk` gray (Section
  1 issue 4 was specifically the homepage `DeepDivePanel`; the research
  index has its own correct CSS rule). No critical issues here.
- **LOW.** The research index hero `<h1>Research</h1>` clamps from 40px to
  56px (`clamp(40px, 6vw, 56px)`). At 1200px viewport this renders ~52px,
  larger than the section-page headline question at `clamp(28px, 4vw, 44px)`.
  The visual hierarchy reads `/research/` as a heavier page than `/inflation/`,
  which inverts the editorial weight (research is one of eight cells on the
  homepage; inflation is one of seven core sections). Recommend dropping
  the research h1 to `clamp(36px, 5vw, 48px)` to match the chartbook
  headline rhythm. Defer.

---

## 3. Cross-cutting findings

### 3.1 The TK rendering pattern (CRITICAL, applies to all 7 section pages + homepage panels)

The publication has adopted "TK" as the journalism convention for "to come,"
but the design system never canonized a typographic treatment for it. Result:
TK strings render in whatever class their host element provides, which means
real-data Plex Mono pure ink for table cells, Manrope 800 for plate titles,
Manrope 400 for interpretation prose. The global footer disclosure ("Series
are placeholder values for the v1 release") is correct but insufficient -
disclosure at the foot of the page does not redeem a "Headline CPI printed
TK y/y" in the chart's interpretation paragraph 800px above.

**Two issues nest here:**

1. **The data layer:** `data/site/sections.json` ships rows where the
   pipeline produces `"value": "TK"` instead of `null`. The
   site_data_loader.ts treats a non-empty string as a real value. Fix:
   coerce `value === "TK"` (and `asOf === "TK"`) to `null` at the enrichment
   layer, so the existing `--placeholder` mid-gray styling fires. This is a
   2-line fix in `enrichPrint`.

2. **The component layer:** section-page plates and the SectionLayout's
   `latestReleaseLabel` prop take strings verbatim. The ChartbookUnit and
   SectionPageHeader components don't inspect the string for a TK pattern.
   Fix: at the component, if asOf/value/etc === "TK", wrap in a `__tk`
   placeholder class with `color: #8A8A8A` and `font-family: var(--font-mono)`
   (the same treatment research/index.astro already uses).

The canon needs a new section to formalize this: **"Section 3.5 - Placeholder
ink treatment."** I will draft this in a follow-on canon update (flagged
below). Until then the implementation rule is: any string equal to "TK"
renders in `#8A8A8A` Plex Mono with `0.14em` tracking and `text-transform:
uppercase`. See research/index.astro's `--row-stamp-body--tk` rule for the
canonical implementation.

### 3.2 Lorem ipsum density (HIGH on homepage, MEDIUM on section pages)

The homepage abstract is visible lorem ipsum (Section 2.1 above). Every
section page's plate interpretations have either real prose with embedded
TKs (the dominant pattern) or pure placeholder lorem ipsum. The placeholder
ink is correctly mid-gray in most cases, but the editorial vacuum is a
visible feature of the v1 build. Defer to editorial-director / writer for
a triage on minimum publish-ready prose. From a visual standpoint, the
placeholder rendering is correct.

### 3.3 Asymmetry between homepage and section pages on the figure/plate eyebrow weight

The homepage panel's `FIGURE 1.` eyebrow uses the Manrope 600 "Figure" word
plus Manrope 800 `--accent` numeral. The section page's `PLATE 01` eyebrow
uses the SAME treatment (Manrope 600 "Plate" word plus Plex Mono 800
`--accent` numeral). Note the family difference: homepage figure-numeral is
Manrope, plate-numeral is Plex Mono. This is intentional per canon Section
6.2: the plate number is a Knoll-catalogue mono stamp, the figure number is
a panel eyebrow. The asymmetry is canonical and reads correctly. No action.

### 3.4 Section header headline questions are appropriately weighted

The seven section pages' headlines render `clamp(28px, 4vw, 44px)` Manrope
800 with `-0.018em` tracking and a 22ch max-width that forces editorial
linebreaks. At 1240px viewport all seven headlines fit the rhythm. No action.

### 3.5 The `latestReleaseLabel` prop is consistently leaky across all six
section pages

Every section's `latestReleaseLabel` is a hand-typed string like
`"Headline CPI, TK"` or `"LFS, TK"`. Renders in Plex Mono 12px pure ink in
the SectionPageHeader's right rail under "LATEST RELEASE" eyebrow. Pattern
fix: make `latestReleaseLabel` accept `null` and render the
`PLACEHOLDER.notWired` micro-caps gray treatment, then in each page set the
prop to `null` when the data isn't yet wired. See fix brief F2.

### 3.6 Alignment + hairlines

Hairlines are pixel-aligned. The home grid uses a `border-top + border-left`
on the parent + `border-right + border-bottom` on each cell, which produces
exactly one 1px ink rule at every shared edge - no doubling, no gap. The
section page's `2px` closing rule after the plate index is the only thicker
rule on the page and is canonical (chartbook-template Section 2). The
chartbook unit's plot-frame border + table-row borders all share the same
1px pure ink. **No alignment issues found.**

### 3.7 MTA red rationing audit (one issue, see Section 1 issue 2)

Permitted MTA red moments per design-system.md Section 3:

- Latest-print dot on a chart: USED, correct.
- Figure-number numeral: USED, correct.
- Plate-number numeral: USED, correct.
- Section-number kicker: USED, correct.
- Focus rings: USED, correct.
- Link hover (research index titles): USED, correct.
- Selection: not visible in static dist.
- Brand kicker tokens (`INDEPENDENT` etc.): USED, correct.

**Violations:**
- Homepage hero date `May 11, 2026` in `--accent` (Section 1 issue 2).
- Footer 2px red rule (`.vig-col__rule--signal`). Borderline. The canon
  doesn't list a "footer signal rule" as a permitted moment. But the rule is
  a single 2px line directly above the publication mark, functioning as a
  brand-signal kicker for the colophon. I assess this as a defensible
  brand-signal moment IF the canon is updated to include "section-close /
  publication-mark rule" in Section 3's permitted list. Flagging for canon
  amendment rather than removal. See canon amendment note below.
- Research index `.row-title:hover` transitions to `--accent` color AND
  underline. The canon Section 3 permits link hover (color + underline);
  this is correct. No violation.

### 3.8 Typography micro-details

- Eyebrow letter-spacing at `0.18em-0.22em`: COMPLIANT across all eyebrow
  classes in production components.
- Plex Mono used for data only: COMPLIANT. The one debatable use is in the
  plate-number numeral (which is mono caps for the Knoll-catalogue plate
  feel); this is canonical per chartbook-template Section 3.
- No italic in production: COMPLIANT.
- Tabular nums on numeric columns: COMPLIANT. The `--ink` token resolves to
  pure black and `font-variant-numeric: tabular-nums` is set globally on
  `.vig-panel__td--val`, `.vig-title__stamp-num`, etc.

### 3.9 Hard-coded color audit

Production component hex literals (outside the token system):

| File | Hex | Disposition |
|------|-----|-------------|
| SectionPanel.astro SVG | `#FFFFFF`, `#000000`, `#E63946` | OK - direct SVG primitives. The canon allows these because SVG `fill`/`stroke` don't accept CSS vars in all rendering paths. Mirrors of token values. |
| SectionPanel.astro placeholder | `#8A8A8A`, `#9A9A9A`, `#6B6B6B` | OK per canon Section 3 "Decisions flagged" - placeholder mid-gray is a hard-coded escape hatch. |
| TitleStatement.astro | `#8A8A8A` | Same. OK. |
| DeepDivePanel.astro | `#8A8A8A` | Same. OK, BUT note the `.vig-dd__stamp-body--tk` class is referenced without its CSS rule - the leak in Section 1 issue 4. |
| VignelliColophon.astro | `#8A8A8A` | Same. OK. |
| PanelEmpty.astro | `#9A9A9A`, `#6B6B6B` | Same. OK. |

**No production hard-coded hex outside the placeholder discipline.** Token
system is respected.

### 3.10 `--ink-faint` opacity composition

The canon Section 3 prescribes opacity-composing `--ink-faint` (which
resolves to pure black) to get visible-restraint chrome. Implementation
audit:

- VignelliMasthead pipe separators: `color: var(--ink-faint); opacity: 0.32;`
  COMPLIANT.
- SectionPageHeader kicker separators: `color: var(--ink); opacity: 0.32;`
  COMPLIANT (uses `--ink` directly rather than `--ink-faint`; functionally
  identical since they resolve to the same value).
- ChartbookUnit eyebrow separator: `color: var(--ink); opacity: 0.32;`
  COMPLIANT.
- TitleStatement eyebrow dot: pure ink `4px x 4px` square. COMPLIANT.

No issues.

### 3.11 Edge-of-frame clipping

I spot-checked the chartbook unit at 1240px viewport. Long indicator names
in the eyebrow (`Sub-aggregates: shelter, services ex-shelter, goods, food,
energy` at 11px Manrope 600) sit on one line up to ~1000px viewport; at
narrower widths the eyebrow wraps. No clipping.

`latestReleaseLabel` strings up to ~32ch fit the right-rail max-width
(`max-width: 32ch` on `.section-header__stamp-body`). The longest in
production today is `"BoC decision, April 16, 2026"` (~28ch). No overflow.

**One issue not addressed by the formatter dispatches:** the homepage panel
indicator-name cell in the 4-row table can be very long (e.g. "EI regular
beneficiaries, y/y" at ~31 characters), and the table column for the
indicator name uses `padding-right: 8px; padding-left: 0;` with no
`max-width`. Long names overflow the cell visually into the value column
when the parent panel is at its narrow breakpoint (~600px). The
backend-formatter dispatch will not address this because it's a string
LABEL not a numeric value. **Flagged separately as MEDIUM, fix brief F8.**

---

## 4. Fix briefs

These are paste-ready briefs for chart-builder / frontend-designer dispatches.
Each is one paragraph plus file paths.

### F1 (CRITICAL) - Drain TK rendering across data layer + section pages

The `data/site/sections.json` enrichment in
`C:\Users\jayzh\projects\macro-research-department\src\data\site_data_loader.ts`
function `enrichPrint` (lines 188-206) currently passes through any non-empty
string as a real value, including the literal "TK" the pipeline emits for
not-yet-wired rows. The fix is two-fold: (1) in `enrichPrint`, treat
`raw.value === "TK"` (and `raw.asOf === "TK"`, `raw.delta === "TK"`) as
equivalent to null, so the existing `value === null -> render in
placeholder gray` path engages automatically; (2) at the section-page level
(`src/pages/{gdp,inflation,labour,housing,policy,markets,trade}.astro`),
every plate currently has hand-typed `asOf: "TK"`, `title: "...TK..."`,
`interpretation: "...TK..."`, `callout: { value: "TK", unit: "...TK...",
delta: "TK vs prior" }`. The clean fix is to change these to `asOf: null,
interpretation: null, callout: null` and update `ChartbookUnit.astro` to
render placeholder-styled `[ NOT WIRED ]` micro-caps gray markers when
those props are null (mirroring the homepage SectionPanel pattern). The
in-body TK strings inside interpretation prose ("Headline CPI printed TK
y/y") are harder - they require a writer pass to replace with placeholder
prose or with `<span class="tk-inline">TK</span>` micro-caps gray spans;
recommend writer dispatch for the in-body TK replacements specifically.
Implementation owner: frontend-designer for the loader + component coercion;
writer for the in-prose TK substitution.

### F2 (CRITICAL) - Remove `--accent` from the homepage date

In `C:\Users\jayzh\projects\macro-research-department\src\components\home\TitleStatement.astro`
line 144, the `.vig-title__h-date` selector sets `color: var(--accent)`.
The canon Section 3 does not include "date in hero headline" in the
permitted MTA red set. Change to `color: var(--ink)`. The visual hierarchy
(headline line + date on the next visual row) still reads via weight
contrast (both at 800) and line break alone. If editorial wants the date
to be a brand-signal element, the canonical path is to recast it as a
brand kicker token in the eyebrow row above the headline (e.g. "INDEPENDENT
| PROUDLY CANADIAN | MAY 11, 2026") rather than as a sub-headline.
Implementation owner: frontend-designer.

### F3 (CRITICAL) - Add the missing `.vig-dd__stamp-body--tk` CSS rule

In `C:\Users\jayzh\projects\macro-research-department\src\components\home\DeepDivePanel.astro`
the markup at line 104 uses class `.vig-dd__stamp-body--tk` but the
stylesheet has no matching rule. Result: "Coming soon" renders in pure
ink at the same weight as a real "Published May 14, 2026" stamp. Add this
rule to the component's `<style>` block (mirroring research/index.astro's
existing rule):

```
.vig-dd__stamp-body--tk {
  font-family: var(--font-mono);
  color: #8A8A8A;
}
```

Implementation owner: frontend-designer. 5-line change.

### F4 (CRITICAL) - Coerce sections.json "TK" string values to null in the loader

In `C:\Users\jayzh\projects\macro-research-department\src\data\site_data_loader.ts`
function `enrichPrint` (line 188). The current logic:

```
const hasValue = typeof raw.value === "string" && raw.value.length > 0;
```

passes the literal string "TK" through as a real value. The fix:

```
const isLiteralTk = (v: unknown): boolean => v === "TK";
const hasValue = typeof raw.value === "string"
  && raw.value.length > 0
  && !isLiteralTk(raw.value);
```

Apply the same `!isLiteralTk(...)` guard to `raw.asOf`, `raw.delta`, and
the `value: hasValue ? raw.value : null` cascade so the downstream
`value === null -> render PLACEHOLDER.value in gray` path engages on TK
rows. Implementation owner: frontend-designer or backend-engineer. ~6
lines.

### F5 (HIGH) - Drain section-header `latestReleaseLabel` TK leak

For each of the seven `src/pages/{slug}.astro` files: the
`latestReleaseLabel` prop currently passes strings like `"Headline CPI,
TK"`. Either (a) change the prop in `SectionLayout.astro` /
`SectionPageHeader.astro` to accept `null` and render a
`[ NOT WIRED ]` placeholder in micro-caps gray, then pass `null` from
section pages whose data isn't wired; or (b) wire the prop to the
pipeline's `releaseDate` field from `data/site/sections.json` (the policy
section already has `releaseDate: null` and labour has `releaseDate:
"2026-05-08"`, so a partial wire is possible). Recommend (b) as the
durable fix; (a) is the 1-day stop-gap. Implementation owner:
frontend-designer for (a); backend-engineer for (b).

### F6 (HIGH) - Drain `ChartbookUnit` `As of TK` leak

In `C:\Users\jayzh\projects\macro-research-department\src\components\section\ChartbookUnit.astro`
the `asOf` prop is a `string` and renders verbatim in lines 127-130. When
the section page passes `"TK"`, this is the most-visible TK on the page
because the `As of` stamp sits in the chartbook unit's eyebrow, right at
the reader's eye level for the plate. Fix: change the prop to `string |
null`. When `null` or `"TK"`, the component renders the asOf body in
placeholder gray micro-caps. Defensive coercion in the component lets
all existing TK strings get the right treatment without each page being
re-edited individually:

```
{asOf === "TK" || asOf === null ? (
  <span class="chartbook-unit__asof-body chartbook-unit__asof-body--tk">
    [ NOT WIRED ]
  </span>
) : (
  <span class="chartbook-unit__asof-body">{asOf}</span>
)}
```

Plus the matching CSS rule (mirror the research index `--tk` rule).
Implementation owner: frontend-designer.

### F7 (HIGH) - Audit and homogenize the placeholder-TK component pattern

The publication currently has THREE different "TK" / placeholder
typographic treatments in production:

1. Research index: `.research-index__row-stamp-body--tk { color: #8A8A8A; }`
   (Plex Mono micro-caps because inherits from parent).
2. Section panel (homepage): `.vig-panel__placeholder { color: #8A8A8A; }`
   + `.vig-panel__placeholder--mono` + `.vig-panel__placeholder--micro`.
3. Title statement: `.vig-title__placeholder { color: #8A8A8A; }` +
   `--mono` and `--micro` variants.
4. Colophon: `.vig-col__stamp-placeholder { color: #8A8A8A; ... }`.
5. DeepDive panel: `.vig-dd__placeholder { color: #8A8A8A; }`, BUT the
   `--tk` variant is missing (F3).

These are all consistent in color, but the family/weight/letter-spacing
varies across components. Recommend extracting a shared placeholder
typographic treatment to `base.css`:

```
.placeholder-tk {
  color: #8A8A8A;
  font-family: var(--font-mono);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
```

and consuming it from every component that renders a `[ NOT WIRED ]` /
"Coming soon" / "TK" marker. This makes the placeholder pattern
auditable (one class to grep for) and durable (one rule to change if the
canon adopts a different placeholder ink). Implementation owner:
frontend-designer; ~30 lines net across 5 files.

### F8 (MEDIUM) - Homepage panel indicator-name column long-string overflow

In `C:\Users\jayzh\projects\macro-research-department\src\components\home\SectionPanel.astro`
the `.vig-panel__td--ind` cell has no `max-width` and overflows when
indicator names exceed ~28 characters at panel-narrow breakpoints. The
backend formatter dispatch only addresses numeric values. Fix at the
component:

```
.vig-panel__td--ind {
  max-width: 22ch;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

Plus a `title` attribute on the cell so the full name is available on
hover. Implementation owner: frontend-designer.

### F9 (MEDIUM) - Standardize Tier 2.5 (homepage panel) chart spec in canon

The homepage panel mini-chart at 320x180 viewBox lives between the canon's
Tier 2 (MiniChart at 248x72) and Tier 3 (PanelLiveChart at 720x405). It
carries x-axis stamps, a 3-tick y-axis, a hairline plot frame, and a
latest-point dot - that's a Tier-2.5 hybrid. The canon needs a section
documenting this tier explicitly so future engineers don't drift it
arbitrarily. I will draft Section 5.1.5 in a canon update. No production
fix required.

### F10 (HIGH) - Decide on/document the footer signal rule

The `VignelliColophon.astro` `.vig-col__rule--signal` is a 2px MTA red
rule directly above the publication mark. It is functionally a section-
close brand-signal moment but is not explicitly listed in design-system.md
Section 3's permitted MTA red uses. Decision: keep the rule and update
the canon to include "publication-mark / section-close rule" as the ninth
permitted MTA red moment, OR drop the rule to 2px pure black. My
recommendation: keep, document. The single red rule in the footer
threads the brand signal across the entire scroll of the page and is
visually load-bearing for the Vignelli register's "single accent moment
on every screen" discipline. Canon amendment, not a code fix.
Implementation owner: art-director.

---

## 5. Canon updates surfaced by this audit

Two canon updates are warranted as a result of this sweep. I will draft
both as patches to `design/design-system.md` (separate dispatch). Flagging
here so the audit is the durable record of why they exist:

1. **Section 3.5 - Placeholder ink treatment.** A new sub-section formally
   describing: the `#8A8A8A` mid-gray, the Plex Mono caps treatment, the
   `0.14em` tracking, and the standardized "[ NOT WIRED ]" / "Coming soon"
   / "TK" string conventions. Names the canonical class `.placeholder-tk`
   (or similar) and points to the implementation. Closes the gap that
   made fixes F1-F6 each have to reinvent the treatment.

2. **Section 3.6 - The ninth permitted MTA red moment: section-close /
   publication-mark rule.** Adds the footer signal rule to the permitted
   list with rationale (one accent moment threaded across the scroll;
   functions as a brand-signal kicker for the colophon, mirroring the
   plate-number / figure-number kicker pattern).

These canon edits are flagged here per the brief's instruction; the
patch will follow as a separate art-director output.

---

## 6. Defer list (post-publish v1.1)

These are issues I judged below the publish bar. They should land in v1.1
or v1.2:

- **D1.** Homepage panel grid panel-bottom alignment when sections have
  different print counts (4 vs 5 vs 6 rows). Visual cost is minor; the 1px
  grid hairlines absorb the height drift.
- **D2.** Research index hero h1 size relative to section-page headlines
  (currently larger, inverts editorial hierarchy). Recommend
  `clamp(36px, 5vw, 48px)` in v1.1.
- **D3.** Tier 2.5 (homepage panel) chart spec documentation in the canon
  (F9 above).
- **D4.** The plate-2 inflation interpretation prose contains an authored
  forecast ("a notch above year-over-year, consistent with a flat near-term
  path") that should be writer + style-editor reviewed for tone alignment
  with the publication's "consensus as input, not citation" rule. Style-
  editor concern, not visual.
- **D5.** Homepage abstract lorem ipsum length. Replace with a 2-3 sentence
  publication manifesto or short hero abstract in v1.1.
- **D6.** Cross-section panel padding consistency: the 7 homepage panels
  use identical `padding: 18px 20px 16px` but read very slightly different
  on their bottoms because of variable-length indicator tables. Acceptable.
- **D7.** Plex Mono micro-caps tracking on `[ NOT WIRED ]` markers varies
  by component (`0.14em` in SectionPanel, `0.18em-0.22em` in others).
  Standardize via F7.
- **D8.** Inflation Panel 3 breadth band weighting (resolved in canon
  reference Q1; no action). Noted for the record - it was the question
  most likely to surface in a Bay Street reader's "this looks wrong"
  reaction, and the encoding decision is correct.

---

## Issue count summary

- CRITICAL: 4 (TK leaks across section pages; homepage date red; sections.json
  TK to ink; missing `--tk` CSS rule on DeepDivePanel).
- HIGH: 6 (homepage lorem density; section-header `latestReleaseLabel`
  leak; ChartbookUnit `asOf TK` leak; placeholder pattern homogenization;
  footer signal rule canon ratification; homepage indicator-name overflow).
- MEDIUM: 8 (panel-bottom drift, Tier 2.5 canon spec, several smaller
  hierarchy / spacing items, inflation Panel 2 prose audit, plate-2 prose,
  research h1 size, tracking inconsistency, panel placeholder ink usage).
- LOW: 4 (the deferrable items above).

---

End of pre-publish visual QA. Ship after CRITICAL + HIGH closure (10 fixes).
