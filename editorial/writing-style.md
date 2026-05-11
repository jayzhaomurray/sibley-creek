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
setup," "the tape" do not. If a term is load-bearing and not in the
reader's working vocabulary, define it once on first use; do not
patronize.

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
  two only when the second decimal is load-bearing.
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

### Headlines and chart titles

- Headlines and chart titles are sentence case, not title case:
  `Core-trim ticks down, but services ex-shelter holds`.
- No terminal period in headlines or chart titles.
- A chart title states what the chart shows, not what the reader
  should conclude: `Vacancy-to-unemployment ratio, 2015-2026` is a
  title; `Labour market is loosening fastest in Ontario` is an
  editorial annotation or a callout, not a chart title. Editorial
  director scopes which is which.
- Chart subtitles carry the unit and the date: `Per cent, monthly,
  to March 2026`.
- Sources line, every chart: `Source: Statistics Canada Table
  14-10-0287-01. Author calculations.` Primary source first; "Author
  calculations" appended when the series is constructed.

### Paragraph length and rhythm

- Short paragraphs. Two to five sentences is the target. A paragraph
  that runs eight sentences should split.
- Lead with the load-bearing sentence. Subordinate clauses last, not
  first.
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
`dashboard_purpose.md`) and any future deep dives. 1,200 to 2,500
words typically; longer when the question demands.

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
- Name what would change our mind. Every load-bearing call has a
  falsification trigger.
- Sentence length varies. Paragraph length stays short (Section 2).
- Numerate. Every load-bearing number has a citation one click
  away. Constructed series have a methodology note.
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

## 8b. Ordering rule for splash-page blurb passes

When a blurb pass writes the splash page (the hero abstract paragraph
plus the seven section blurbs), **the hero abstract is the LAST piece
written, not the first.** The seven section blurbs are authored first;
the hero abstract is then synthesized from them.

**Why.** The hero abstract is a publication-frontmatter paragraph that
names the state of the Canadian cycle. The cycle reads as the
aggregate of what each section is saying that day. Writing the hero
first means guessing at the cycle-level read before the section reads
are pinned. Writing it last means the hero can pull the most
load-bearing fact from each section blurb and stitch a single coherent
cycle paragraph from real, vetted section-level reads.

**Practical sequence for a writer / pipeline dispatch:**

1. Author all seven section blurbs against pipeline data. Vet each.
2. Once the seven are stable, read them as a set and identify the
   load-bearing cycle theme (loosening? tightening? mixed? where is
   the headline tension?).
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

## 9. Working notes for style-editor

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
7. Push the load-bearing clause to the front of the sentence.
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
