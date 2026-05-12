# GDP — chart diagnosis

Page: https://sibleycreek.ca/gdp
Last updated: 2026-05-12

How to use: open /gdp in another tab. For each plate, check what
resonates as wrong, write in your own read where the boxes miss, and
give a priority. The free-text is where the real diagnosis lives —
the checkboxes are starter hypotheses I can be wrong about.

Priority key:
- KILL — chart should be replaced entirely with a different visual
- FIX — chart concept is right, needs surgical changes
- FINE — leave it, it's already doing its job

---

## P1 — Headline GDP, m/m

Title: "Monthly GDP rose 0.2% in February, a second consecutive gain."

Current geometry (my guess): single line of monthly m/m % change,
recent ~year of data, no reference line, no Y/Y context.

What might be wrong:
- [ ] Title invokes "below trend" / "1.0% Y/Y" but the chart shows neither — no reference line at potential growth, no Y/Y series
- [ ] m/m series is inherently noisy; "two consecutive gains" is two data points, hard to read as a story
- [ ] No marker on the latest value
- [ ] Y-axis bounds wrong (too tight, too loose)
- [ ] Time window wrong (too short, too long)
- [ X] Something else: title talks about monthly gdp rising 0.2%, a second consecutive gain. you'd expect a m/m chart to fit that. we have level. the chart is also quite boring. it's just a mostly diagonal line. visually it tells us not much aside from the economy is still growing but the pace has slowed down these last few years. the y/y% and trend stuff would have to fit a different chart potentially? or maybe we can discuss as if we have multiple charts? do we need to show literally every claim? idk. but we are not showing what we're talking about. we are mostly showing line go up.

Your read:

Priority (KILL / FIX / FINE): probably needs switching.

---

## P2 — Total vs per-capita real GDP, indexed to 2019Q4

Title: "Aggregate growth has run well ahead of per-capita output since 2019."

Current geometry (my guess): two lines indexed to 2019Q4 = 100, total
real GDP and per-capita real GDP, six years of quarterly data. The
widening gap between the lines is the population contribution.

You've already flagged this as the one chart on the page you like.
This section is to capture what specifically works (so we can codify
it) and whether anything could still be sharpened.

What works (check all that apply):
- [X ] The comparison is in the geometry — gap = the thesis
- [ ] Indexed view eliminates unit confusion
- [X] Two lines is the right number of lines
- [X] Time window (2019Q4 onward) is right
- [ ] Something else: visually the chart tells a story. growth, then recession (covid) then growth again. but per capita has the same bounce back and hardly a recovery. the story is well known. but it is a good looking chart. I said two lines is the right number but sometimes more is right. i like the small multiples here. i like small multiples in general.

What could still be sharper:
- [ ] Endpoint labels at right edge ("Total", "Per-capita") to kill the legend
- [ ] Latest-value marker (red dot) on each series
- [ ] Light annotation labelling the gap as "population contribution"
- [X] Already perfect, don't touch
- [ ] Something else:

Your read:

---

## P3 — Growth-rate cross-check (m/m and Q/Q SAAR)

Title: "Monthly industry growth firmed in early 2026 even as the Q4
annualized read turned slightly negative."

Current geometry (my guess): m/m monthly line (or bars) + Q/Q SAAR
line on the same panel. Two cadences, two magnitudes, one y-axis.

What might be wrong:
- [X] Two cadences on one panel don't visually compare — different units, different magnitudes
- [X] The paradox in the title (monthly up, quarterly down) doesn't read from the geometry
- [X] Would work better as two small charts side by side
- [ ] Or: m/m as primary, with quarterly SAAR overlaid as step risers at quarter boundaries
- [X] The "cross-check" concept itself is the problem — pick one cadence and own it
- [ ] Title is the right takeaway but the chart can't support it
- [X] Something else: it is the type of chart that is common, but i feel like is mostly noise. month is up. quarter is down. okay so what. what do i do with this. and they just look like random wiggly lines. the whole chart to me is noise, not insight, and it's the type of thing that is typical analysis because most analysis of economic data is done in about a half-hour to an hour after the data comes out. people are rushing. they don't know. the release is noise. i feel almost obligated to have these growth rates because everyone watches them. i don't retain anything. 

Your read:

Priority (KILL / FIX / FINE):

---

## P4 — Contributions to quarterly growth

Title: "An inventory drawdown swamped a positive domestic profile in Q4."

Current geometry (my guess): stacked bars by component (consumption,
exports, government, investment, inventories), recent quarters on x.

What might be wrong:
- [ ] Inventory (the story) not visually emphasized — all five components weighted equally
- [ ] Accent color should be on the inventory bar, rest in restrained ink
- [ ] Horizontal bars might read better than vertical for a single-quarter focus
- [ ] Hard to tell which color is which component without hunting
- [ ] No annotation labelling "inventories -4.2pp" on the plot
- [ ] Time window wrong — too many quarters dilutes the Q4 focus
- [X] Something else: first of all, we don't even show what we're talking about. this chart talks as if it has contributions; it only has quarterly growth. and frankly, quarterly growth works better as a bar chart usually anyway, not a line chart. but we don't even have the contributions we're talkinga bout. and then again, so what. it's inventory driven? what do we do with this information. does that mean growth is secretly good, and we should ignore all inventory swings? or is the inventory drag saying something?

Your read:

Priority (KILL / FIX / FINE):

---

## P5 — BoC MPR output gap

Title: "Output gap widened to -1.0% in Q4 2025, doubling the Q3 shortfall."

Current geometry (my guess): single line of % of potential, plotted
against a zero baseline, multi-year history.

What might be wrong:
- [ ] Lonely line — needs the gap (between line and zero) shaded, not just drawn as a wiggle
- [ ] Zero baseline not bold enough; it should be the visual reference
- [ ] No recession bands or historical context — "deepest since early 2021" isn't legible without them
- [ ] Latest value not labelled on the plot
- [ ] No marker on the current point
- [ ] Y-axis range may compress the recent movement
- [X] Time window wrong
- [X] Something else: this one is very much okay... it is functional. i can't tell if it would be better as a bar chart. but anyway, the output gap is slightly negative. fine. we are below potential, there's slack, that shouldn't be inflationary, that's a sign the bank shouldn't hike. there's insight there, so it is functional. but maybe we could use a comparison. or some other takeaway. what can we infer from the size of the output gap? how much, really, is a 1% gap? and then this is pure boc data. should we try to extend on this with our own estimates? project forward potential, use the latest gdp data, see where the output gap is tracking? how it's moved from where it was the last time the bank released this? now that's starting to get more interesting. 

Your read:

Priority (KILL / FIX / FINE):

---

## P6 — Labour productivity, business sector

Title: "Productivity growth decelerated sharply into year-end."

Current geometry (my guess): single line of Y/Y % change, business-sector
labour productivity per hour, multi-year.

What might be wrong:
- [ ] Title invokes the Canada-US gap as structural context, US isn't on the chart
- [X] Lonely line — no comparison series, no reference level
- [ ] Y/Y alone doesn't show the level story (the actual productivity gap)
- [ ] No marker on the latest value
- [X] The "decelerated sharply" claim needs an annotation or visual emphasis on the rolloff
- [ ] Time window wrong
- [X] Something else: it is fine, whatever. productivity growth is trash. but canada's productivity being weak is a known structural story. the interesting thing is why? many people will say it's the lack of investment after the oil price collapse in 2014. others will say it has to do with taxes or regulation or something. but i guess, i don't know what i really get out of tracking productivity quarter to quarter. big gaps, trends, sure. productivity to me is a long-run structural story. tracking it short term, who gives a fuck.

Your read:

Priority (KILL / FIX / FINE):

---

## Page-level notes

Things that apply across all GDP charts (e.g. tick-font size, chart
height consistency, color usage, axis label conventions):

---

## Plan (decided 2026-05-12)

After diagnosis, the disposition for each plate:

- **P1 Headline GDP — REWORK.** Small multiples: left panel m/m % bars (last ~24 months); right panel Y/Y % line on full history with a horizontal reference line at potential growth (~1.7%). Two panels, two cadences. "Second consecutive gain" reads on the left, "below trend" reads on the right.

- **P2 Total vs Per-capita — KEEP AS IS.** Reference exemplar for the chart canon.

- **P3 Cross-check — CUT.** Quarterly SAAR is redundant once P1 carries the headline reads with proper geometry. Page drops to five plates.

- **P4 Contributions — REWORK.** First verify the data wiring (the current chart appears to show quarterly growth, not the decomposition the title claims). Then: stacked bars by component (actually wired), with a "final domestic demand + trade" line overlaid so the ex-inventories signal reads cleanly. Inventory bars in the accent color. New title direction: "Strip the inventory swing and Q4 was an expansion." Chart carries an argument, not a decomposition.

- **P5 Output gap — METHODOLOGY DISCUSSION PENDING.** Direction agreed: BoC published gap (solid line) + Sibley nowcast extension (dashed line) + optional revision band showing how the gap has moved since the last MPR. Build deferred until methodology is hashed out (potential growth assumption, GDP vintage used, revision band construction).

- **P6 Productivity — DELETE FROM PAGE.** Productivity is a structural story (long-run Canada vs US, post-2014 widening). Doesn't belong on the cyclical GDP page. Idea parked in `editorial/chart-diagnosis/ideas.md` for future placement (likely a Research deep dive).

**Resulting page:** 4 plates immediately (P1 reworked, P2 kept, P4 reworked, P6 deleted). 5 plates once the P5 output-gap nowcast lands.

**Build status as of 2026-05-12:**
- P1 small-multiples rework: TODO
- P3 cut from page: TODO
- P4 data wiring verification + rework: TODO
- P6 deletion from page: TODO
- P5 methodology + build: deferred for joint discussion

