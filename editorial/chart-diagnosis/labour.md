# Labour — chart diagnosis

Page: https://sibleycreek.ca/labour
Last updated: 2026-05-12

How to use: open /labour in another tab. For each plate, answer the
two questions — what should the reader retain, and why isn't the
current chart getting them there. Mark cuttable yes / no / maybe.
The starter checkboxes are optional jog-the-thinking material; skip
them if the free-text already covered it.

---

## P1 — LFS headline (unemployment, employment, participation)

Title: "The headline unemployment rate is steady; the employment rate
is doing the softening underneath."

Current geometry (my guess): three-line chart — unemployment rate
(primary, the eye lands here), employment rate (secondary), and
participation rate (tertiary). Y-axis spans roughly 55–70% so all
three rates share a single axis. Multi-year history.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**
you nailed why the chart doesn't work. it looks like two horizontal lines far apart. we're also missing participation on the chart currently. a tryptich small multiple could work. another idea i have is to decompose the unemployment rate. this would be a single panel. unemployment rate alone is the line. but then in stacked bars there are the inflows and outflows that explain it. entering/exiting the labour force. getting hired or losing job. so right now, i think we need to scrap the chart we have and replace it with three charts. the two you suggested (i'll probably just keep one but we'll see). and the decomp.

**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [X] Three lines on different absolute levels (UR ~7%, employment rate ~60%, participation ~65%) — y-axis range has to span all three, so the recent action (0.1pp moves) compresses visually
- [ ] The "steady on top, softening underneath" thesis isn't visible in the line geometry — needs annotation or split-view
- [X] Should be small multiples — one panel per rate, each with its own y-range, so the action in each reads
- [X] Or: index all three to a common base (e.g. Feb 2020 = 100) so they share a scale and the divergence is the geometry
- [ ] Participation rate may not be carrying weight — could be cut to two lines for clarity
- [ ] Time window — the disinflation cycle reads cleanest from 2022 onwards
- [ ] Something else:

---

## P2 — Wage band: LFS, payroll, BoC LFS-Micro vs services CPI

Title: "The headline wage measures overstate underlying pressure once
composition is stripped out."

Current geometry (my guess): three wage-measure lines plus a services-
CPI line as a real-wage anchor. Likely four-line spaghetti. Y-axis in
% Y/Y.

**What you want the reader to retain (so what?):**
is wage growth picking up or slowing down? do different measures agree or disagree?

**Diagnosis — why the current chart isn't getting them there:**
we only have lfs permanent and lfs all on the chart. they're in dollars it looks like. so it's just two parallel diagonal lines. what it says is that wages have gone up 8 bucks over the last few years. that's not really the question we're asking. we don't have any of the other wage indicators. we don't even have lfs micro which should be our main indicator now.

**Cuttable?** (yes / no / maybe)
entirely replaceable

_Optional starter hypotheses:_
- [ ] Four-line chart is too many for the eye to track
- [ ] The "gap between headline and composition-adjusted" is the story but lives between two specific lines — could highlight those two in accent and dim the rest
- [ ] Could be a band chart: LFS-Micro as the central line, range between LFS and payroll as a band around it
- [ ] Services CPI as the comparator is the right idea but visually loses to the wage lines — should be in different treatment (e.g. dashed)
- [ ] BoC 2% target line missing
- [ ] Time window
- [ ] Something else:

---

## P3 — Beveridge curve (vacancy rate vs unemployment rate)

Title: "Labour demand has not just normalized but is drifting through
pre-pandemic norms."

Current geometry: scatter plot, monthly points connected by a path.
Dashed segment for Apr–Sep 2020 (imputed from Indeed Hiring Lab).
Two annotated inflection markers (May 2020 hollow, Apr 2022 filled).
Feb 2026 latest in red. Heavily iterated already.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Beveridge curve is unconventional; reader may need more guidance to read it (e.g. quadrant labels — "loose / slack" "tight" "imputed-covid window")
- [ ] The "drifting through pre-pandemic norms" thesis needs the pre-pandemic point clearly anchored — the Sep 2019 marker should be obvious
- [ ] Time-path is hard to read on a scatter — could add year-month labels along the path at key inflections
- [ ] Imputed segment (dashed) reads fine but the methodology note belongs in the source line, not on the chart
- [ ] Already perfect, don't touch
- [X] Something else: Beveridge curve is fine as far as a beveridge curve goes. it's a fairly standard presentation for people who are familiar with the concept. Maybe we add an additional chart that's just vacancies and unemployment (levels) on one left panel and then a bar chart of the spread on the right panel. this does a lot of the same work as this chart but together they might read better; the new chart would be much easier for the average person to understand.

---

## P4 — Supply trajectory (PR landings + net NPR vs IRCC plan)

Title: "The population denominator is rolling over as the IRCC plan
pivot works through."

Current geometry (my guess): bar chart of PR landings + net NPR flows
by quarter, possibly with the IRCC plan as an overlay reference line
or band.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Two series on the same axis (PR landings positive, net NPR turning negative) — bars carry the sign well; line would not
- [ ] The IRCC plan reference may not be visible as a clean band
- [ ] The "five consecutive negative NPR quarters" claim is countable and should be visible
- [ ] The October 2024 plan pivot is a dated event — could be annotated with a vertical line
- [ ] Time window
- [X] Something else: fundamentally we want to know how the population is changing so this could be a stacked bar (natural growth from births/deaths bucketed together, net temporary, net permanent immigrants. so three buckets compositionally and one line for the population.) let's make this chart separately, not as a replacement just yet. and if we like it we'll swap it in.

---

## P5 — Regional (provincial unemployment rates)

Title: "The national headline hides a four-way split rather than a
coherent regional swing."

Current geometry (my guess): line chart of provincial unemployment
rates (BC, ON, QC, AB) plus Canada as a reference. Five lines on one
panel.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Five-line chart — classic spaghetti problem; eye can't track each province
- [X] Should be small multiples (one panel per province with Canada as a faint reference line in each)
- [ ] Or: a dumbbell / forest plot showing the 12-month delta per province — kills the time dimension but shows the "four-way split" clearly
- [ ] Endpoint labels at each line terminus would help reduce the legend burden
- [ ] Time window
- [X] Something else: four small multiples, one per major province. each small multiple has the canada comparator. wondering if we should potentially use colour to distinguish province from country or not; ask art director for opinions.

---

## P6 — EI beneficiaries

Title: "The leading EI signal has rolled over even as the LFS
unemployment rate climbed back up."

Current geometry (my guess): single line of regular beneficiaries
count (in thousands of persons), multi-year. Latest 542k Feb 2026
after a 568k Nov 2025 peak.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Lonely line — needs the LFS unemployment rate as a comparator (the title's whole point is the divergence)
- [ ] Levels chart in absolute persons may not be the right idiom — Y/Y % change might carry the cyclical signal better
- [ ] The "leading" relationship to LFS is the editorial point — could be visualized via a two-panel small multiple (level on top, with LFS unemployment rate overlaid; deltas / Y/Y below)
- [ ] Latest peak (Nov 2025) and current (Feb 2026) need to be clearly marked
- [ ] Time window
- [X] Something else: maybe this should be population deflated. need to see which population makes sense as comparator (has to be eligible for ei, don't know if temporary residents are eligible and they are now significant proportion). and then we should also have comparators on the chart. not necessarily another line, but perhaps thresholds that make sense "this is about normal, this is high, this is crisis" type of takeaway

---

## Page-level notes

Cross-cutting issues (tick fonts, chart-height consistency, BoC
2% target / control-band treatment, wage-vs-CPI register, legend
strategy, plate ordering):

