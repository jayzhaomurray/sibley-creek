# Debt/GDP plate — what does the reader actually want? (internal memo, 2026-06-04)

Scope: plate-4 of `src/pages/fiscal.astro` (federal accumulated deficit % GDP, 40yr
history + forecast, flat near 41%). Question from Jay: what's the takeaway someone
wants from a debt/GDP chart, and does this one need a comparator?

## 1. The reader questions a federal-debt/GDP chart can answer, ranked for OUR reader

Our reader is P1 (Bay Street allocator, CPP/OTPP gravitational centre) and P2
(PBO/DoF/BoC analyst). They are policy-literate and think in liability streams and
fiscal capacity for the next shock. Ranked by what they actually bring to THIS chart:

1. **Sustainability / trajectory** — is the ratio stabilizing or compounding? This
   is the whole game for a liability-stream reader. A flat ratio means the debt
   dynamic is contained; a rising one means r-minus-g is working against you. THIS
   is the question the chart is built to answer.
2. **Capacity for the next shock** — how much fiscal room before the next downturn?
   Answered *by the same line*: distance below the 1990s peak IS the headroom read.
   Not a separate question for this reader; it's the trajectory question's "so what."
3. **Historical context (vs mid-1990s peak)** — already in-frame via the 40yr
   history. This is context, not a standalone reader question. It's the denominator
   on questions 1-2.
4. **Burden (interest cost as share of revenue)** — a genuinely distinct question,
   but it is **already a separate plate in canon** (Section 4.6 unit 2,
   debt-service/revenues with the PBO 13.2%-by-2030-31 anchor). It does not belong
   ON the debt/GDP chart; it belongs on its own.
5. **Comparison (G7, provinces-combined, gross vs net)** — the LEAST of what this
   reader brings to a *federal* debt/GDP chart. P1/P2 already know the G7-net framing
   cold. It is the most likely thing to *decorate* rather than *inform*.

The top question is sustainability, and capacity is its corollary. The history is
the comparator that answers both. Burden and peer-comparison are separate questions
that either live elsewhere or risk being decoration.

## 2. Does the current chart answer the top question on its own?

**Yes.** A 40-year line with the 66.6% mid-1990s peak, the 28% pre-crisis low, the
47% pandemic spike, and a flat ~41% forecast track answers "is it stabilizing?"
(flat) and "how much room?" (24+ points below peak) without any second series. The
self-comparison through time IS the comparator. The takeaway sentence already lands
it: "The level is elevated; the trajectory is flat." That is the correct, defensible
read and it needs no help to be true.

## 3. Comparator options, assessed honestly

- **(a) G7 / IMF general-government net debt.** Tempting because Canada looks
  best-in-G7 on net. But: (i) it answers a question the reader didn't ask at a
  *federal* chart, (ii) it's a known framing fight (best on net, mid-pack on gross)
  — surfacing it half-told is worse than not surfacing it, (iii) it swaps the
  *federal accumulated deficit* basis for *general-government net* — a different
  aggregate, so it can't share the y-axis honestly without a methodology fight on
  the canvas. Changes the takeaway from "contained trajectory" to "Canada looks
  good vs peers" — a DIFFERENT, more complacent story. Decoration-to-distortion risk.
- **(b) Total government incl. provinces.** This is the real analytical objection to
  federal-only (BoC/IMF view: federal understates the consolidated burden). It
  genuinely changes the level (~federal 41% vs total-government ~90%+ of GDP). But
  consolidated government debt is **already the subject of canon unit 4** (provincial
  net debt/GDP, ON/QC/AB/BC). The federal/provincial split is a deliberate two-plate
  editorial structure, not something to collapse onto one chart. Folding provinces
  in here would pre-empt plate 4 and bury the federal trajectory signal.
- **(c) Public debt charges as % of revenue.** The strongest *question*, but it is
  **canon unit 2** with its own PBO anchor. Putting it on the debt/GDP chart double-
  books it and muddies two distinct y-axes (% of GDP vs % of revenue).
- **(d) As-is, history as the only comparator.** History is doing the comparator
  job and doing it for the exact question the reader brings.

## 4. Recommendation

**Leave it as-is. No second series.** History is the comparator, and it answers the
top-ranked question (sustainability) and its corollary (capacity) on its own. Every
proposed comparator either (i) answers a question that already has its own plate in
canon (burden -> unit 2; provinces -> unit 4), or (ii) imports a different aggregate
on a shared axis and shifts the takeaway from "contained trajectory" to a more
complacent "Canada looks good vs peers" story we don't want to lead with on a
*federal* chart. This is the Vignelli restraint call: the chart already earns its
place; a comparator would decorate, not inform.

One framing note (not a comparator): the takeaway is stronger if it states the
*mechanism* explicitly — the ratio is flat because dollar debt grows no faster than
nominal GDP, not because borrowing stopped. The current interpretation already does
this ("dollar debt keeps climbing past $1.6 trillion, but growing no faster than the
economy keeps the ratio flat"). Keep that; it's the take-mechanism-land structure
working correctly.

**Takeaway sentence under this recommendation (unchanged in substance):**
*Federal debt has stabilized near 41% of GDP — elevated against its pre-2008 low,
but far below the mid-1990s peak, and flat across the forecast because dollar debt
is growing no faster than the economy.*

## Flag for Jay (separate from the question asked)

The live `fiscal.astro` is FOUR plates (balance two-panel, rev-vs-exp, debt/GDP,
issuance-by-instrument). Canon Section 4.6 specifies a different FIVE-plate slate:
federal trajectory, **debt-service/revenues (the burden cut)**, **PBO-vs-DoF delta**,
**provincial net debt/GDP**, operating-vs-capital. The debt-service/revenues "burden"
plate and the provincial plate — the two comparators I just argued AGAINST putting
on the debt/GDP chart — are supposed to exist as their OWN plates and currently don't
on this branch. The right home for the burden and comparison questions isn't a second
series on plate-4; it's the missing canon plates. Worth reconciling the branch against
canon as a separate decision.
