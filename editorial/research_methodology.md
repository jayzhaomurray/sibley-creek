# Sibley Creek research methodology

Authored by Jay Zhao-Murray, 2026-05-20. House canon for how research gets done at Sibley Creek. Lightly structured by Claude from Jay's original articulation; the underlying philosophy and principles are Jay's.

This document sits alongside `writing-style.md` (how the prose sounds) and `review_protocol.md` (how content gets gated before publication). This is the methodology layer — how the analysis itself is done.

---

## The starting posture

The business is fundamentally **client-led**. Sibley Creek does not operate on the premise that the analyst knows better than the client what the client should care about. The client (or the reporter, or the subscriber) brings the question. Sibley Creek goes and answers it.

This is not a Steve Jobs "the customer doesn't know what they want" firm. The opposite. The client knows what they want; the firm's job is to deliver a thoughtful, well-researched, fact-checked, opinionated, and pleasant-to-read answer to that specific question.

The research-piece strategy with media (reporters bring topics; Sibley Creek produces research) is the same principle applied to a different audience. The subscription-product Q&A model is the same principle applied to subscribers. The retainer is the same principle applied to clients. It is the underlying architecture of the firm.

---

## The three principles

**Simplicity.** Methods should be as simple as possible while still answering the question. The bar for adding complexity is high. A simpler analysis that gets to the right answer is better than a more sophisticated one that does the same.

**Specificity.** Aggregates are starting points, not endpoints. The best work is grounded in specific products, specific markets, specific geographies, specific time periods. Vivid examples that the reader can easily imagine beat statistical abstractions.

**Triangulation.** Data analysis is not sufficient on its own. The data tells part of the story; people close to the process tell the other part. The best work combines both.

---

## What data analysis looks like in this house style

Acceptable and frequently used:

- Averages, medians, ranges, percentiles, distributions, skew
- Contributions analysis (decomposing aggregates into drivers and sub-drivers)
- Line charts, bar charts, scatter plots, histograms
- Exploratory data analysis (EDA) — looking at the data carefully and thinking clearly about what it's saying
- Time-period comparisons, geographic comparisons, peer comparisons
- Identifying major drivers of a number, then their sub-drivers

Possibly acceptable with caution — pushing the methodological complexity ceiling:

- Linear regression
- VAR (vector autoregression)
- Logit / probit models

These are tools, used sparingly, when the question genuinely requires them and a simpler approach can't get there. The default is: don't reach for them.

Not in the house style:

- Complicated statistical methods used without a clear necessity
- Modeling for the sake of modeling
- Methodology-as-credentialing (using a technique because it sounds rigorous rather than because it produces the right answer)
- Black-box approaches where the analyst can't fully explain why the model produced what it did

---

## What "sources" means in this house style

The most important sources are often **the people closest to the process being observed**, not the people we conventionally label as experts.

A retail analyst may know less about what's happening in a sector than the store manager. A central bank watcher may know less about a specific policy mechanism than the person who actually implemented it. A real estate strategist at a bank may know less about a regional market than a broker who works the streets of that market every day.

The conventional "experts" (bank chief economists, academic specialists, government officials) have their place. They aggregate and synthesize. But they often miss what the people doing the work see directly. A Sibley Creek research piece should reach for the second category when it can.

The triangulation principle means: data analysis generates tentative conclusions, then source interviews stress-test those conclusions, then the conclusions either harden or shift in response.

---

## The standard workflow

1. **Start with the data.** Visualize it. Calculate simple summary statistics. Look at distributions, contributions, drivers, sub-drivers.
2. **Identify the story the data is telling.** What's the clearest possible way to present this? What's interesting? What's unexpected?
3. **Form tentative conclusions** based on the data work. Hold them loosely.
4. **Talk to well-informed people.** Sources who are close to the process. Stress-test the tentative conclusions against what they're seeing.
5. **Sharpen the answer.** Update or invert the conclusions based on what the source interviews surfaced.
6. **Write the piece.** Thoughtful, well-researched, fact-checked, opinionated, pleasant to read. Specifics over abstractions. A clear story.

---

## What this implies for the firm

- **Research output is mixed-method.** It's not "data analysis" or "reporting" — it's both, deliberately combined. Long-form reporting backed by data; data work informed by source interviews. Neither alone is sufficient.
- **Speed-to-publish is constrained by the source-interview leg.** Data work can be fast; source interviews take time. Publication cadence has to allow for this.
- **The team profile matches the method.** A junior analyst who can run summary statistics and make clear charts is useful. A senior analyst who can also conduct source interviews and stress-test data conclusions against ground-truth is more useful. Eventually the firm hires for both.
- **The output is differentiated from bank-desk research by the methodology itself.** Banks have analytical horsepower; they don't have the journalism layer. Sibley Creek's edge is the combination, not either piece alone.
- **Pieces favor specifics over aggregates.** A piece on Canadian housing should name specific cities, specific developments, specific buyers. A piece on inflation should name specific products and price points. Aggregates set up the question; specifics answer it.
- **The voice canon (`editorial/writing-style.md`) and the methodology canon (this doc) reinforce each other.** Voice is "readable, opinionated, take-driven." Methodology is "simple stats + specifics + triangulation." Both serve the same end: making the work clearer and more useful than the alternatives.

---

## What this rules out

- Heavy quantitative research as a Sibley Creek product
- Modeling-first research where the model is the deliverable
- Black-box analysis the analyst can't fully explain
- Pure desk research (data only, no source interviews) on questions where ground-truth would change the answer
- Pure reporting (interviews only, no data) on questions where the data would change the answer
- Aggregates as the destination of a piece (they're the starting point)
- Methodology-as-credentialing
