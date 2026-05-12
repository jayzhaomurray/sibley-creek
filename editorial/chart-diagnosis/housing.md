# Housing — chart diagnosis

Page: https://sibleycreek.ca/housing
Last updated: 2026-05-12

How to use: open /housing in another tab. For each plate, answer the
two questions — what should the reader retain, and why isn't the
current chart getting them there. Mark cuttable yes / no / maybe.
The starter checkboxes are optional jog-the-thinking material; skip
them if the free-text already covered it.

---

## P1 — MLS HPI, national + six CMAs, Y/Y

Title: "The national price decline masks a widening split between
Toronto-Vancouver and Montreal."

Current geometry (my guess): seven-line chart — Canada composite +
Toronto, Vancouver, Calgary, Ottawa, Edmonton, Montreal — all Y/Y %.
Classic CMA spaghetti.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Seven lines on one panel — the protagonist split (Toronto/Vancouver vs Montreal) is buried in the spaghetti
- [ ] Should be small multiples — one panel per CMA, all sharing y-axis, with the composite as a faint reference in each
- [ ] Or: highlight the three protagonist CMAs (Toronto, Vancouver, Montreal) in accent and dim the rest
- [ ] Or: dumbbell / forest plot showing latest Y/Y per CMA — kills the time dimension but the split reads
- [ ] Zero reference line (the "negative territory" claim) should be bold
- [ ] Time window
- [ ] Something else:

---

## P2 — Activity (starts, completions, permits)

Title: "The completions pipeline, not new starts, is now carrying
supply."

Current geometry (my guess): three series on one chart — housing
starts (annualized units), units under construction (annualized
units), and residential permits ($ billions). Mixed units AND
magnitudes.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Three series with three different units — can't share an axis honestly
- [ ] Indexing all three to a common base (e.g. 2019 = 100) would let them share a scale and the divergence between "starts soft, completions still firm" would read
- [ ] Or: small multiples — one panel per metric
- [ ] Permits in $ probably doesn't belong on a chart that's otherwise in unit-count terms — could drop or split
- [ ] The "completions carrying supply" thesis needs the completions line as the protagonist
- [ ] Time window
- [ ] Something else:

---

## P3 — Sales-to-new-listings ratio

Title: "Absorption is soft but has not tipped into a buyers' market."

Current geometry (my guess): single line of S/NL ratio, with CREA's
50–70% balanced band possibly shaded. Multi-year.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Single line with CREA's 50–70 balanced band — this is the right idiom (same family as the inflation 1–3% control band)
- [ ] If the band isn't shaded, add it as a referenceBand prop
- [ ] "Below balanced band" is the current read; the band should make this read in two seconds
- [ ] Months-of-inventory could be a secondary line on the same chart, but might double-count
- [ ] Time window
- [ ] Something else:

---

## P4 — Rent (CPI rent + rented accommodation, Y/Y)

Title: "Rents are no longer rising; the level is now adjusting
downward."

Current geometry (my guess): two-line chart — CPI rent Y/Y +
rented-accommodation Y/Y. The two series diverge: CPI rent +0.9%, but
the rented-accommodation sub-series shows -2.5% (an outright price
decline).

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Two lines is the right number; the divergence between them IS the editorial story (CPI rent vs rented-accommodation)
- [ ] Zero reference line is needed (rented accommodation is negative)
- [ ] Could the BoC 2% target be relevant here? Or is that more inflation-page territory
- [ ] The 2020–2021 demand vacuum reference should be visible in the time window
- [ ] Time window
- [ ] Something else:

---

## P5 — Mortgage stack snapshot (5y conventional rate)

Title: "The renewal wall has peaked, with the residual risk rotating
to the labour channel."

Current geometry (my guess): single line of the 5y conventional
mortgage rate, weekly cadence, multi-year.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Lonely line — the "renewal wall has peaked" claim isn't visible from one rate alone
- [ ] Should overlay something cohort-relevant: e.g. the 2020-2021 rate trough at ~1.5% as a horizontal reference (that's the rate the renewing cohort is rolling FROM)
- [ ] Or: the rolling delta (current rate minus 5y-ago rate) as a derived series — that IS the renewal-payment shock
- [ ] Title invokes the deep dive at /research/mortgage-renewal-wall/ — chart should serve as an entry point
- [ ] Title talks "labour channel" but the chart is just the rate — chart can't deliver that claim
- [ ] Time window
- [ ] Something else:

---

## P6 — Supply ratio (immigrant flow + housing starts)

Title: "Supply is finally running ahead of incremental population-
driven demand."

Current geometry (my guess): two lines — quarterly immigrant arrivals
(persons) and housing starts (annualized units). Different units,
different cadences. Per the blurb: "the full population-per-housing-
unit ratio by CMA is not yet wired; the flow-vs-flow comparison here
is the v1 read."

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Plate explicitly flagged as v1 / not the right chart — the real read needs population-per-housing-unit ratio by CMA
- [ ] Flow-vs-flow is a proxy that doesn't directly answer "is supply keeping up"
- [ ] Backend lift: wire population-per-housing-unit ratio (StatCan Tables 17-10-0009 + 34-10-0156 or similar) so the chart matches the question
- [ ] Until backend lands, plate is borderline cuttable
- [ ] Time window
- [ ] Something else:

---

## P7 — Affordability (BoC qualifying payment / income)

Title: "Affordability is improving from peak but remains worse than
prior stress episodes."

Current geometry (my guess): single line of BoC's qualifying-mortgage-
payment-to-income ratio, quarterly, multi-decade. Latest 42.7% Q4
2025; Q2 2024 peak 50.4%. The 1989-1991 and 2007-2008 stress
episodes invoked by the title need to be visible.

**What you want the reader to retain (so what?):**


**Diagnosis — why the current chart isn't getting them there:**


**Cuttable?** (yes / no / maybe)


_Optional starter hypotheses:_
- [ ] Multi-decade single line — the prior stress episodes (1989-91, 2007-08) should be visible AND annotated to support the claim
- [ ] Without annotations, the reader can't anchor "improving from peak" vs "worse than prior stress" in the same view
- [ ] Time window MUST include 1989 to support the claim
- [ ] Could mark stress-episode peaks with markers + dates
- [ ] Something else:

---

## Page-level notes

Cross-cutting issues (CMA spaghetti pattern, mixed-units charts
across multiple plates, reference-band consistency with inflation,
annotation conventions for historical stress episodes, plate
ordering):

