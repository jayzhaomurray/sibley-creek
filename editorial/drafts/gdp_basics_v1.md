# GDP basics-layer prose -- v1 draft

Author: writer (macro-research-department).
Date: 2026-05-11. Revised 2026-05-11 against W3-R1.
Status: v1 draft for style-editor polish and fact-checker review. ASCII-only.

Anchors:
- Editorial canon: `editorial/dashboard_purpose.md` Section 4.1 (GDP basics
  elements 1-6; updated 2026-05-10).
- Voice: `editorial/writing-style.md` (Mode A for the homepage event blurb;
  Mode B-adjacent for the page lede and panel decks, kept short and
  declarative; Mode A only for the consensus callout verbs).
- Page template: `design/basics-layer-template.md` Section 9 (worked example).
- Verified anchors: `research/wave3_gdp_basics_insights.md` (Sections B, C, D).
  Latest monthly: Feb 2026 +0.2% M/M (released 2026-04-30). Latest quarterly:
  Q4 2025 -0.2% Q/Q (-0.6% Q/Q SAAR; released 2026-02-27). Output gap:
  Q4 2025 -1.0%. Q1 2026 quarterly releases 2026-05-29; March 2026 monthly
  releases 2026-05-30.

This draft fills the prose slots only. Chart titles, chart annotations,
visual treatment, and the headline-question wording are owned elsewhere
(art-director, chart-builder, editorial-director).

---

## 1. Section header headline question

The EDR-canonical question (Section 4.1) is:

> *Is the Canadian economy at potential, growing, or contracting -- and
> what is driving it?*

This is locked in canon and reproduced in the page template. No polish
proposed. The two-clause structure is doing real work: the first clause is
the position-relative-to-potential read (panel 5), the second clause is the
contributions read (panel 3). A polish that dropped the second clause would
make the page header read as a recession-watch question, which is not what
the page is. Keep as is.

(Note: `src/data/sections.ts` carries a shorter, tile-only variant --
"Is the Canadian economy at potential, growing, or contracting?" -- for the
homepage card where the second clause does not fit. That is a tile-display
truncation, not a canon revision; the basics page renders the full question.)

---

## 2. Page lede

Three sentences, set immediately below the page-level as-of stamp. State of
GDP today, anchored to verified release data; no editorializing on direction
beyond what the panels and the BoC's own potential estimate support.

> Real GDP by industry rose 0.2% in February, with StatCan's advance
> estimate flagging March as essentially unchanged. On the quarterly
> expenditure cut, the economy contracted 0.2% in the fourth quarter
> (-0.6% at an annualized rate) -- a soft handoff into 2026, with the
> output gap widening to -1.0%. The Q1 2026 print lands May 29, 2026.

Voice notes:
- Mode-B-adjacent register: short, declarative, no "we think." No
  "soft landing," no "Goldilocks," no "the consumer."
- The lede does the so-what once across the three numbers it carries
  (monthly turn, quarterly contraction, output-gap widening) and then
  hands off to the panels. It does not pre-empt panel 5 (output gap) or
  panel 4 (per-capita); it surfaces the headline reads.
- "Soft handoff" is the central description -- the monthly path is
  modestly positive while the quarterly aggregate posted a small
  contraction, and the BoC's central output-gap estimate widened from
  -0.5% in Q3 to -1.0% in Q4. Not a forecast.
- Per-capita is intentionally not in the lede this vintage: Q4 2025
  per-capita was unchanged Q/Q (after +0.5% in Q3), and the cleaner
  cycle-state read sits in Panel 4. See research-pack Section D.2.

---

## 3. Per-panel decks

One sentence each, italic, set in `body-sm` per the panel template
(Section 3 of `basics-layer-template.md`). Each deck answers "so what" for
the panel and does not recite the chart's own numbers.

### Panel 1 -- Headline real GDP

> *The monthly path turned modestly positive in early 2026; the quarterly
> cut contracted in the fourth quarter and sits below the Bank of Canada's
> potential estimate.*

### Panel 2 -- Industry vs expenditure cross-check

> *The two cuts agree on direction through the soft handoff into 2026; any
> level gap reflects the standard reconciliation between industry value
> added at basic prices and expenditure final demand at market prices.*

### Panel 3 -- Contributions to quarterly growth

> *Household consumption, exports, and government capital investment carried
> the fourth quarter into positive territory; an inventory drawdown was the
> single largest drag.*

### Panel 4 -- Per-capita real GDP

> *Per-capita real GDP was unchanged in the fourth quarter after rising in
> the third; the cut the headline obscures has turned mixed in 2025 as the
> immigration-policy reset slows the denominator.*

### Panel 5 -- Versus BoC potential

> *Output sits one percentage point below the Bank of Canada's central
> estimate of potential; the gap widened through the second half of 2025.*

### Panel 6 -- Recession state

> *The C.D. Howe Business Cycle Council has not declared a recession; the
> most recent communique (September 22, 2025) found the second-quarter
> contraction did not meet the criteria of amplitude, duration, and scope.*

---

## 4. Per-panel callout prose (Beat / Missed / In line)

Surprise-framing override per the 2026-05-10 EDR changelog: anchor to
market consensus first, BoC MPR central projection as fallback. Subscript
`[c]` / `[m]` is the art-director's visual indicator; the prose writes the
verb and the value. Verb rule (per template Section 4): outside +/-0.05pp
on growth rates is beat/miss; inside is in-line. The surprise sentence
follows the consensus-framing examples in `writing-style.md` Section 8.

### Panel 1 -- Headline real GDP

- Headline number: +0.2% M/M, February 2026.
- Delta vs prior: research-pack Section B does not surface the January 2026
  M/M number in Daily prose; the writer omits the M/M-vs-prior delta for
  this vintage and notes "second consecutive monthly gain" instead, per
  the StatCan Daily narrative.
- Consensus: ~+0.2% M/M, in line with the StatCan advance estimate. No
  measurable surprise (per W3-R1 Section D, point 9).
- Revision tag: removed for this vintage; the January 2026 revision
  direction is not in the Daily prose and the May 30 release will revise
  February in turn. Writer omits the tag rather than guess.

Callout copy:

> +0.2% month-over-month, February 2026.
> Second consecutive monthly gain. In line with consensus and with
> StatCan's own advance guidance[c].

### Panel 2 -- Industry vs expenditure cross-check

No numeric callout per the page template (Section 9, Panel 2). Editorial
status line in place of the standard callout block:

> Cross-check: industry and expenditure cuts agree on direction through
> the soft handoff into 2026. The industry monthly series is positive
> in early 2026 (Feb +0.2% M/M, March advance essentially unchanged) while
> the expenditure quarterly series contracted modestly in Q4 2025
> (-0.2% Q/Q). The two cuts can differ in any quarter through the
> statistical discrepancy line and the reconciliation of taxes net of
> subsidies on products; revisions narrow these gaps over time.

### Panel 3 -- Contributions to quarterly growth

- Headline number: -0.2% Q/Q (-0.6% Q/Q SAAR), Q4 2025.
- Delta vs prior: research-pack Section B confirms Q3 2025 was +0.6% Q/Q
  (+2.4% Q/Q SAAR). Q/Q SAAR delta therefore -3.0pp vs Q3.
- Drivers (Q4 2025): household consumption +0.4% Q/Q, exports +1.5% Q/Q,
  capital investment +0.8% Q/Q (positive contributions). Inventory
  drawdown was the largest single drag.
- Consensus: no published Big-Six median for the Q4 2025 print at the
  time of release; the W3-R1 panel-median (1.4% Q/Q SAAR) is for the
  Q1 2026 print scheduled for May 29 -- it does not anchor this callout.
- Surprise framing: omitted for this vintage; refreshes on the Q1 2026
  release with the verified bank-median value (1.4% Q/Q SAAR) and the
  BoC April 2026 MPR Q1 projection (1.5% Q/Q SAAR).

Callout copy:

> -0.2% quarter-over-quarter, Q4 2025.
> -0.6% at an annualized rate, down from +2.4% in Q3. Inventory
> drawdown was the largest drag; consumption, exports, and government
> capital investment carried positive contributions.

### Panel 4 -- Per-capita real GDP

No surprise field, per page template Section 4 ("When there is no
surprise to show") and EDR 4.1 element 4 (per-capita is a derived
construction, not a forecastable print).

Callout copy:

> Per-capita real GDP unchanged Q/Q, Q4 2025.
> After +0.5% in Q3 2025. The cut the headline obscures has turned
> mixed in 2025 as immigration policy resets the denominator.

### Panel 5 -- Versus BoC potential

No surprise field (no consensus on output gap; the BoC's own estimate is
the benchmark, not the forecast comparator).

Callout copy:

> -1.0% output gap, Q4 2025.
> Bank of Canada central estimate. Widened from -0.5% in Q3 2025 (a
> -0.5pp Q/Q step). The Q1 2026 reading refreshes after the May 29
> StatCan GDP release and the next MPR cycle.

### Panel 6 -- Recession state

No numeric callout. Editorial status line:

> Current state: The C.D. Howe Business Cycle Council has not declared
> a recession. The most recent communique (September 22, 2025) found
> that Q2 2025's contraction did not meet the recession criteria of
> amplitude, duration, and scope. Q4 2025's subsequent contraction
> post-dates the communique; the Council has not yet published a
> follow-up.

---

## 5. Event-blurb body (homepage tile, Mode A voice)

Replaces the current `last` blurb on the GDP tile in `src/data/sections.ts`.
The blurb fires on the April 30, 2026 monthly GDP release (Feb 2026
reference month); voice per `writing-style.md` Section 7, Mode A. Three
to four sentences. Past tense for the print; present tense for the state;
no editorializing on direction.

> Real GDP by industry rose 0.2% in February, the second consecutive
> monthly gain and in line with both consensus and StatCan's own advance
> estimate. The advance reading for March is essentially unchanged. The
> quarterly expenditure cut, last reported for the fourth quarter,
> contracted 0.2% (an annualized -0.6%). The next quarterly print is
> May 29, 2026; the March monthly print follows May 30.

Voice notes:
- Lead with the print: variable, value, period (sentence 1).
- Comparator second: consensus and StatCan's own advance (sentence 1
  carries both; no measurable surprise).
- The one observation that the chart cannot make on its own:
  the quarterly cut is still on the prior vintage and contracted
  (sentence 3) -- the soft handoff matters more than the monthly tick.
- Calendar-as-subject closer (sentence 4) -- both upcoming dates are
  verified against the W3-R1 research pack.
- No "watch for," no "we think," no "suggests the BoC will." Per Mode A
  rules, those go in deep-dive territory.

---

## 6. Methodology note stubs

Two-sentence stubs only; researcher fleshes out the full methodology
drawer content per `basics-layer-template.md` Section 7. The voice is
plain methodology, not editorial; the stubs name the construction and
the central assumption.

### Per-capita real GDP (Panel 4)

> Per-capita real GDP is computed as the level ratio of real GDP
> (StatCan Table 36-10-0104-01) to the StatCan quarterly population
> estimate (Table 17-10-0009-01), indexed to a common base period. The
> denominator is total population, not working-age population; this is
> the convention used in Bank of Canada MPR per-capita tables, and the
> denominator choice matters whenever participation is moving.

### Output gap vs BoC potential (Panel 5)

> The output gap shown is the Bank of Canada's central estimate, taken
> directly from Valet series `INDINF_OUTGAPMPR_Q` and refreshed on
> each Monetary Policy Report (April, July, October, January). The
> potential-output level used in the comparison chart is read off the
> MPR Appendix on each release, not constructed in-house; vintage stamps
> on the panel reflect the most recent MPR.

### Recession state -- C.D. Howe BCC (Panel 6)

> Recession dating follows the C.D. Howe Business Cycle Council, the
> recognized non-governmental arbiter of Canadian business-cycle
> turning points. Amplitude, duration, and scope are reported per the
> BCC's canonical wording on each dating-committee communique; the
> editorial entry refreshes on each communique release.

[FLAG for researcher: "indexed to a common base period" in the per-capita
stub is generic; the actual base period in the construction script should
be named once the script is authored (see `wave2_labour_methodology.md`
Section 1 for the parallel labour methodology, which uses subtractive
growth rates rather than indexed levels). The Valet key
`INDINF_OUTGAPMPR_Q` is probe-confirmed working per W3-R1 Section D
point 10 (Q4 2025 = -1.0%, quarter-start dating).]

---

## Source insights drawn from

- `editorial/dashboard_purpose.md` Section 4.1, elements 1-6, for the
  scope of each panel and the panel-by-panel construction discipline
  (industry-vs-expenditure cross-check is methodological-footnote-only
  in v1; six-bar GFCF contribution decomposition; per-capita as the
  "cut the headline obscures"; BoC potential as the v1 benchmark, not
  an in-house construction; BCC dating with canonical wording).
- `editorial/dashboard_purpose.md` Section 4.1, surprise-framing
  override (2026-05-10 changelog): consensus-first, BoC MPR fallback.
- `editorial/writing-style.md` Section 2 (numbers, percentages, dates),
  Section 4 (institution names: BoC, StatCan, BCC), Section 6 (banned
  hedging tics and clichés), Section 7 (Mode A blurb voice), Section 8
  (consensus-as-derived-number, not as cited authority).
- `design/basics-layer-template.md` Section 3 (panel anatomy: title,
  deck, callout structure), Section 4 (surprise visual + `[c]` / `[m]`
  subscripts), Section 5 (revision tag), Section 9 (worked example for
  each of the six GDP panels -- structural anchor only; specific
  worked-example wording on Panel 6 ("Expansion since 2020Q3") is
  superseded by the W3-R1 BCC verification).
- `research/wave3_gdp_basics_insights.md` Sections B (per-panel anchors,
  Feb 2026 +0.2% M/M, Q4 2025 -0.2% Q/Q / -0.6% Q/Q SAAR, output gap
  Q4 2025 -1.0%, BCC no-recession reading), C (consensus median 1.4%
  Q/Q SAAR for the Q1 2026 print; BoC April 2026 MPR Q1 projection
  1.5%), D (resolution of the prior ten flagged claims), and E
  (consolidated recommendations honoured in this revision).
- `research/wave2_labour_methodology.md` Section 1 for the per-capita
  methodology framing convention (subtractive form, monthly-frequency
  population interpolation -- the parallel labour methodology informs the
  GDP per-capita stub).

---

## Unsupported-claim flags routed to researcher

All ten flags from the prior v1 vintage are resolved by W3-R1
(see Section D of that pack). Residual items the writer flags for
follow-up after this revision:

1. **Feb 2026 M/M-vs-prior delta** (Panel 1). The W3-R1 pack notes
   that January 2026's revision direction is not surfaced in the Daily
   prose. The current callout omits the M/M-vs-prior number; if the
   researcher can pull January's revised M/M value directly from
   Table 36-10-0434-01, the callout gains a one-line "vs prior" stub.
   Low priority; the "second consecutive monthly gain" line carries the
   load.

2. **Q1 2026 surprise framing -- ready to fire on release** (Panel 3,
   event blurb). The May 29 release will produce a Q/Q SAAR print to
   compare against the verified W3-R1 consensus of 1.4% and the BoC
   April 2026 MPR projection of 1.5%. No flag for the researcher; this
   is a pipeline / writer refresh on the release.

3. **March 2026 monthly print follow-up** (event blurb). The May 30
   release will produce a March M/M print to compare against StatCan's
   own advance estimate ("essentially unchanged"). The W3-R1 pack notes
   that pre-print bank previews refresh roughly 2026-05-22 to 2026-05-26;
   the researcher refreshes consensus on the print week.

4. **Pillar D / Pillar E surface-vs-adjudicate discipline** (Panel 3,
   Panel 4). The decks intentionally describe inventory drag, consumption
   and exports lead, and the per-capita mixed pattern without resolving
   whether business investment is inflecting (Pillar D) or whether the
   per-capita recovery is through deceleration or aggregate weakness
   (Pillar E). No researcher action; flagged for fact-checker as the
   boundary the basics page should not cross.

End of v1 draft, revised 2026-05-11 against W3-R1.
