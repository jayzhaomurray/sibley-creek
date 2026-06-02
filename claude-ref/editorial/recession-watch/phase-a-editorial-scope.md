# Recession Watch — Phase A editorial scope + writer brief

Owner: editorial-director. Status: scope locked, awaiting data + chart land.
Surface: new live-tracker page. Home section: GDP (`/gdp/recession-watch/` or
`/recession-watch/` — frontend decides routing; editorially it lives under GDP).
Pays off the published commentary at
`work/published/commentaries/testing-2qtr-recession-rule.pdf`.

This doc is the editorial truth for the page. The writer drafts from it; it then
runs the three review gates (fact-check, style, surface-fit) before promote.

---

## 0. The editorial spine (read before anything else)

The commentary made one argument: the two-quarter rule captured only ONE of
Shiskin's three dimensions (duration), and that is why it over-fires — eight
triggers since 1961, five official recessions. The CD Howe Business Cycle
Council judges all three together: duration, depth, breadth (the commentary
uses Shiskin's "duration, depth, diffusion"; we render "diffusion" as
**breadth** in reader copy because it's the plainer word and matches Jay's
clarity bar).

**Recession Watch is the live, multi-dimensional monitor the commentary
promised.** Where the commentary said "the rule is one-dimensional; the real
thing is multi-dimensional," this page shows the multi-dimensional thing,
updating. It does not re-litigate the rule (that's the commentary's job and
the page links back to it). It shows where the current economy sits on each
dimension against the only honest benchmark: the four past recessions, traced
from their own cycle peaks.

The page must read as a MONITOR, not a forecast and not an alarm. The usual
state is "not in recession territory," and the copy is designed for that being
the resting state, with the drama held in reserve for when a series actually
enters the envelope. A monitor that cries wolf is the two-quarter rule's
failure mode; we do not repeat it.

---

## 1. What the page communicates

### 1.1 Headline question (the page-header question)

**"Is Canada in a recession — and how would we know before the committee
calls it?"**

That second clause is the page's whole reason to exist. CD Howe dates
recessions in arrears (the commentary's example: Covid trough April 2020,
announced August 2021). This page is the read in the meantime — not a verdict,
a vantage point. The header question answers itself through the four charts:
by watching depth, breadth, and duration jointly against past recessions.

### 1.2 The current verdict line (template the writer fills from data)

A single synthesis sentence directly under the header, regenerated each
refresh from the live data. It is a Mode 2 (terse, observation-first) line,
NOT a take with a thesis. Structure:

> "[Output] is down [X]% over [N] months with [Y]% of industries shrinking
> since the peak — [below / inside / past] every past recession at this stage."

Rules for the writer:
- The bracketed verdict word is a three-state classifier driven by the
  trigger logic (§1.4): **below** (clear of the envelope on at least one of
  depth/breadth), **inside** (within the past-recession range on depth AND
  breadth AND duration jointly), **past** (deeper/broader/longer than the
  median past recession at this stage). In the resting state it is "below."
- When the economy is at or near its peak (the current live state), the line
  must read calmly and truthfully — e.g. output essentially flat, breadth low,
  duration zero or near-zero. Do NOT manufacture drama from a 0.1% wobble.
  If output is at a fresh peak, the honest verdict is that no downturn clock
  is running; the writer phrases that plainly rather than forcing the template.
- Numbers come from the pipeline slots; cite via slot binding, not hardcoded
  phrases (writing-style §4.1e). No source name in the line (§4.1).
- One sentence. Hard cap two. This is the most-read surface on the page; it
  earns brevity.

### 1.3 What each of the four charts is FOR (one phrase each)

The four are a 2x2: {GDP, employment} x {depth, breadth}. Each overlays the
current downturn (measured from its own cycle peak, t=0) on the four past
recessions (1981, 1990, 2008, 2020).

1. **GDP depth** — how far output has fallen from its peak, vs how far it fell
   in past recessions by the same month. *("Is the fall deep enough?")*
2. **GDP breadth** — what share of industries are below their own output peak,
   vs past recessions. *("Is the fall broad enough?")*
3. **Employment depth** — how far employment has fallen from its peak, vs past
   recessions. *("Is the job loss deep enough?")*
4. **Employment breadth** — what share of industries are shedding jobs since
   the peak, vs past recessions. *("Is the job loss broad enough?")*

The 2x2 is the editorial argument made visible: a real recession shows up on
BOTH output and employment, on BOTH the size of the fall and its spread. The
two-quarter rule sees only the top-left cell (output, depth, and only via the
sign of a quarterly change). The page shows all four.

### 1.4 The trigger logic (the editorial claim the page makes)

A downturn reaches recession territory when it enters the past-recession
envelope **jointly on depth + breadth + duration** — not on any single
dimension. This is the entire point versus the two-quarter rule. The copy must
never let a single chart's reading stand in for the verdict; the verdict (§1.2)
is the joint read. The methodology note (§2) states this plainly so a reader
can restate it in one sentence.

---

## 2. Methodology note — what to explain, plainly

Surface: a methodology note one click away (writing-style §3, §7 "show your
work"). Read once, not read deeply — so it is complete but not long. Plain
language; a reporter must be able to restate each metric in one sentence. NO
"diffusion index," NO "amplitude/scope" jargon dressed up. Cover, in order:

1. **The four metrics, in plain words.**
   - GDP depth: "How far real GDP has fallen below its most recent peak,
     in per cent."
   - GDP breadth: "The share of industries whose output is below its own
     peak" — explicitly NOT "diffusion index." Name the industry basis
     (StatCan monthly GDP by industry, ~20 industries / NAICS sectors —
     writer confirms the exact count and level from the pipeline).
   - Employment depth: "How far employment has fallen below its peak."
   - Employment breadth: "The share of industries shedding jobs since the
     employment peak."
   Each one sentence. A reporter restates it verbatim.

2. **The cycle-peak clock (t=0).** Each line is measured forward from its own
   cycle peak — the month output (or employment) was highest before the
   decline. The x-axis is months since that peak, so 1981, 1990, 2008, 2020,
   and today all start at the same origin and can be compared at "the same
   stage." Explain why peak-relative, not calendar: it puts every downturn on
   the same clock.

3. **The four-recession comparator basis.** The comparators are the four CD
   Howe-dated recessions since 1981: 1981-82, 1990-92, 2008-09, 2020.
   - State plainly that **1974-75 is excluded** and why: the monthly
     industry data needed for the breadth metrics begins later, and the
     pre-1981 vintage is not NAICS-native. (Writer confirms exact start month
     from the pipeline; the commentary's GDP series starts Q2 1961 but the
     *monthly by-industry* breadth basis is the binding constraint.)
   - Note the **1997 data seam**: StatCan's monthly GDP by industry switched
     to a NAICS basis around 1997; series before the seam are bridged/spliced.
     One sentence, flagged honestly, so a reader knows the 1981 and 1990
     breadth lines rest on a splice. Writer confirms the exact seam handling
     from backend.

4. **Monitor, not forecast.** State explicitly: this page reports where the
   economy sits today relative to past recessions at the same stage. It does
   not forecast whether a recession will occur, and it does not date
   recessions — only the CD Howe Business Cycle Council does that, in arrears.
   A series entering the envelope is a signal to watch, not a call.

5. **Revision policy.** Monthly GDP by industry and LFS employment are revised.
   The current downturn's lines move as data is revised; past recessions are
   shown on final, revised vintages. One sentence stating that the live line
   is provisional and will shift with StatCan revisions.

Keep the whole note tight — methodology pages get read once. No internal
canon, no "chartbook unit," no process narration.

---

## 3. Surface-fit guardrails — what does NOT belong on this page

Cut on sight (gate 3). Hold to Jay's clarity bar: legibility is the product.

- **No "diffusion index."** The breadth metric is "share of industries
  shrinking since the peak." A method a reporter can restate in one sentence.
  This is the single most important guardrail — it is the page's reason to
  exist over the textbook version.
- **No dropped-feature ghosts.** A Sahm-rule / unemployment-gap gauge was
  considered and dropped. It does not appear anywhere — not in the charts, not
  in the methodology, not as "we also looked at." Dropped means gone.
- **No re-litigating the two-quarter rule.** The commentary did that. This page
  links back (§5) and assumes the reader can get the argument there. One
  sentence of framing max; do not re-run the eight-triggers-five-recessions
  table here.
- **No forecast language.** No "we expect," "likely," "heading toward,"
  "warning sign," "flashing red." The page reports position, not trajectory.
- **No over-claiming the verdict.** "Below every past recession at this stage"
  is a statement about position on the charts, not a guarantee no recession is
  coming. The verdict line and methodology must not let a reader walk away
  thinking the page rules a recession out.
- **No internal canon / process narration.** No "tri-modal," "live tracker,"
  "chartbook unit," "Mode 1/2," "we cite primary sources," "primary-source
  discipline." Show the discipline; never write about it. (memory:
  voice-doctrine-stays-internal.)
- **No Big-Six framing, no committee name-checking as authority.** CD Howe is
  cited as the body that dates recessions (a fact); not as a voice we lean on.
- **No source names in chart blurbs or the verdict line** (writing-style §4.1).
  Citations live in the chart source line and methodology note.
- **No alarm chrome.** No countdown, no "recession probability %", no traffic-
  light that turns red. The 2x2 of charts plus one calm verdict line IS the
  product. Do not let a template add a gauge slot that auto-fills.
- **Does this surface need MORE than the four charts + verdict + methodology
  link?** Default no. If the build offers an "explainer paragraph" slot or a
  "key takeaways" box, cut it unless the editorial argument requires it. The
  charts are the evidence; the verdict line is the read; the commentary carries
  the why.

---

## 4. Writer brief (dispatch when data + charts land)

**Specialist:** writer. **Then:** fact-checker -> style-editor ->
editorial-director (three gates) before promote.

**Surface + register, per prose unit (name these in the dispatch):**

| Prose unit | Surface | Register |
|---|---|---|
| Page intro / abstract (1-2 sentences) | page header, under the question | section-abstract synthesis (writing-style §4.1b/§4.1i) — answers the header question with a take, but a calm one; this is a monitor's framing, not a deep-dive thesis |
| Verdict line | directly under abstract, live | Mode 2 terse, observation-first (§1.2 template); regenerates each refresh |
| Four chart titles | one per chart | chart-plate title canon (§4.2 / Sec 4.2): sentence case, terminal period, names the finding not the level. In the resting state the finding is often "the current downturn is shallower/narrower than any past recession at this stage" — phrase the title to that, not to a number |
| Four chart blurbs (2-4 sentences each, IF the surface carries blurbs) | under each chart | plate-blurb (§4.1f-2, §4.2): name what the comparison shows; do NOT describe how to read the overlay; do NOT recite the y-axis. The blurb selects the signal (is the current line inside or outside the past-recession spread, and by how much) |
| Methodology note | one click away | read-once register (§2 above): plain, complete, tight |

**Inputs the writer must use:**
- This scope doc (the editorial truth).
- The published commentary PDF (the thesis the page pays off) — for framing
  consistency only; do NOT copy its prose.
- The live pipeline data (depth %, breadth %, months-since-peak, per-recession
  comparator series) once landed — cite via slot binding (§4.1e).
- The chart spec once landed — to confirm what each chart actually shows
  before titling it.

**Hard constraints for the writer:**
- The verdict line and abstract must read calmly in the resting (at-peak)
  state. Do not force the drama template onto flat data.
- Plain words for breadth ("share of industries shrinking since the peak").
  Never "diffusion."
- No forecast, no alarm, no source names in blurbs/verdict (§3).
- Chart titles carry the finding, not the level (§4.2). In the resting state,
  the finding is the reassuring-but-true one: the current track is clear of the
  past-recession envelope.
- Countable / superlative claims ("shallower than any past recession at this
  stage") anchor to a compute slot or enumeration, not the author's eyeball
  (§4.1f, §4.1h — true superlatives, no "second-X").

**Deliverables (writer returns):**
1. Page abstract (1-2 sentences).
2. Verdict-line template, written to fill from the live slots, with the
   three-state classifier wired and a worked example for the current
   (at-peak) state.
3. Four chart titles.
4. Four chart blurbs (confirm with me whether this surface carries per-chart
   blurbs before drafting — the page may stand on titles alone in the
   restraint register; see §3 last bullet).
5. Methodology note (§2 contents).

---

## 5. Links to / from the commentary

- **Page -> commentary.** One link, at the foot of the page or in the
  methodology note: a single line pointing the reader to the commentary for
  the argument behind the monitor (why the two-quarter rule over-fires; why
  duration/depth/breadth jointly). Phrasing names the finding, not the format
  ("Why two negative quarters isn't a recession" rather than "read our PDF
  commentary"). NOT threaded into a chart blurb (§4.1f-3 bans deep-dive/cross
  links inside blurbs; this is a published-commentary link at page level, which
  is permitted, but keep it to the page chrome, not the blurb prose).
- **Commentary -> page.** The commentary is already published as a PDF; a
  future re-issue or its web version should point forward to Recession Watch as
  "the live monitor." Flag to Jay: if the commentary gets a web landing page,
  add a forward link. Not a Phase A blocker.

---

## 6. Open decisions to surface to Jay before/with dispatch

1. **Per-chart blurbs: yes or no?** Restraint register (§3) argues the page can
   stand on four titles + one verdict line + methodology, with NO per-chart
   blurbs — the overlay charts are self-evident and blurbs risk reciting them.
   Recommendation: ship without per-chart blurbs in Phase A; titles + verdict
   carry it. Confirm.
2. **Route:** `/recession-watch/` (top-level, matches its standalone-monitor
   identity and the commentary's prominence) vs `/gdp/recession-watch/`
   (editorially homed under GDP). Recommendation: top-level route, GDP-homed in
   nav. Frontend call; flag editorial preference.
3. **Verdict classifier wording:** "below / inside / past" the envelope — or
   softer ("clear of / within / beyond"). Recommendation: "clear of / within /
   beyond every past recession at this stage" reads less binary than
   below/inside/past. Confirm with style-editor at gate 2.
