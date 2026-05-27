# Sibley Creek — team orientation

A short version of how we work. Read this first. The full canon docs are linked at the bottom for when you need depth on a specific area.

Drafted 2026-05-20.

---

## What Sibley Creek is

Independent Canadian macroeconomic research firm. Two weeks old at the time of this writing. Two-pronged model: retainer advisory clients (the firm's main revenue), paid subscriptions (audience-scale revenue), supported by free public research that doubles as credibility and lead generation.

Founded by Jay Zhao-Murray, ex-Bloomberg economics editor. Team currently: Jay (founder + chief economist), Thompson Richards (senior analyst, leading deep dives going forward), Khoi Pham (research analyst, data muscle), Joe Grimbly (head of business development, commission-only).

The firm operates from the belief that there's a real gap in Canadian macroeconomic coverage between (a) big bank desk research that's free but generic and commercially constrained, and (b) institutional-priced research firms like BCA that are sized for huge clients. Sibley Creek is the boutique in between.

## What we produce

Three modes, all interconnected:

1. **Live data tracker** at sibleycreek.ca — a Python pipeline pulls Canadian macro data daily; the site renders it through a polished editorial layer. This is the public-facing product and the firm's credibility surface. Most readers find Sibley Creek through this.

2. **Short analysis on key prints** — when StatCan or the BoC publishes a major release (CPI, GDP, LFS, rate decision), Sibley Creek publishes a same-day commentary. Fast turnaround, sharp voice, opinionated take. Designed to be quotable by reporters and useful to clients.

3. **Deep-dive research** — longer-form, multi-week investigations into specific Canadian macro questions. Thompson will lead most of these going forward. Combines data analysis with source interviews to produce work that goes deeper than what bank research desks publish.

## The voice (writing canon, summary)

Sibley Creek writing is **take-driven**. Every piece argues a specific claim. The opening sentence IS the take, not the setup. The middle of the piece explains the mechanism — why the take is true. The close lands the argument — what it means or what to do with it.

Three diagnostic questions to ask of any piece before publishing:

- **Does the opening sentence say what we think, or just describe what happened?** If it's pure description, rewrite.
- **Do sentences 2-3 explain WHY, or do they list more WHATS?** Mechanism, not inventory.
- **Does the close land the argument, or does it trail off?** Every piece needs a punchline.

Banned vocabulary:

- "Load-bearing" — overused in finance writing, reached tic status; ban is total.
- "Corridor" — banned in trade/policy contexts (substitutes: route, channel, lane).
- "Per Statistics Canada" / "according to the BoC" — source attribution belongs in citations and source fields, not in prose. Name the finding, not the source.
- "Big-Six median" / "RBC says" / any named bank-desk citation as authority — Sibley Creek doesn't cite bank desks as authority. Aggregated consensus is fine ("consensus expected 3.1%"); naming the bank that said it is not.

**Specifics over aggregates.** When writing about housing, name the city. When writing about inflation, name the basket components. When writing about manufacturing, name the sectors. Aggregates set up the question; specifics answer it.

**Length budgets are enforced at build time.** Plate titles ~85 chars max. Plate interpretations ~3 sentences max. Splash blurbs ~3 sentences. Don't exceed.

Full canon: `editorial/writing-style.md`.

## The methodology

Three principles, all load-bearing (in the actual sense, not the banned-word sense):

**Simplicity.** Methods as simple as possible while still answering the question. The bar for adding analytical complexity is high. A simpler analysis that gets to the right answer beats a more sophisticated one that does the same.

**Specificity.** Aggregates are starting points, not endpoints. Specific products, specific markets, specific geographies, specific time periods, vivid examples the reader can imagine.

**Triangulation.** Data analysis is not sufficient on its own. The data tells part of the story; people close to the process tell the other part. The best work combines both.

The standard workflow:

1. **Data exploration first.** Summary statistics, distributions, contributions analysis, simple charts. Identify what the data is saying and what story it tells.
2. **Form tentative conclusions** from the data. Hold loosely.
3. **Source interviews to stress-test.** Talk to people close to the process — often these are NOT the conventional experts. A regional broker may know more about a market than a bank strategist. Use the second category when you can.
4. **Sharpen the answer** based on what the source work surfaced. Conclusions either harden or shift.
5. **Write the piece.** Take + mechanism + landing. Specifics over abstractions. Pleasant to read.

Acceptable analytical methods: averages, medians, ranges, percentiles, distributions, skew, contributions analysis, line/bar/scatter/histogram charts. Possibly acceptable with caution: linear regression, VAR, logit/probit — used only when genuinely needed.

Not in the house style: complicated statistics without clear necessity. Modeling for modeling's sake. Black-box approaches the analyst can't fully explain. Methodology-as-credentialing.

Full canon: `editorial/research_methodology.md`.

## The review process (publication gates)

Every reader-facing piece passes three gates before publishing:

1. **Fact-check.** Every number, date, citation verified against primary sources. Internal consistency (does the title's direction match the data's direction?). Countable claims enumerated, not trusted.
2. **Style polish.** Voice canon applied. Length budgets enforced. Banned vocabulary cut. Take-mechanism-land structure verified.
3. **Surface fit.** Does this content belong on THIS surface in THIS context? Cuts internal canon-jargon, voice doctrine, placeholder content, anything the reader doesn't need.

The dispatcher (Jay, or main Claude when working in dispatch mode) runs the gates in order. A failed gate kicks the piece back to the writer.

Full canon: `editorial/review_protocol.md`.

## Chart basics

Sibley Creek charts share a visual language. Without knowing the full design canon, hold to these basics:

- **Pure ink stroke, no decorative color.** Color is reserved for the most recent observation (MTA red dot on a line chart, accent-colored bar on a bar chart).
- **One verb per title.** Chart titles end with a period, name the finding, take a position. "Headline CPI rose to 2.8% in April on higher gasoline prices." Not "Canadian CPI Y/Y, Apr 2026."
- **Annotations are words, not sentences.** A chart annotation reads "Pandemic" or "Pre-pandemic average." Full sentence explanations belong in the blurb under the chart.
- **No decorative gridlines.** Hairlines at 18% opacity. Frame is 1px. Sharp ticks.
- **Plex Mono for y-tick labels. Manrope for x-tick labels.** The topmost y-tick carries the unit.

Full canon: `design/canon_reference_panel.md` and `design/sparkline-canon.md`.

## How we work together

**Pipeline + analysis vs. site code.** The Python pipeline (`pipeline/`) pulls data, computes derivations, emits panel data. The Astro site (`src/`) renders it. As an analyst you'll touch pipeline-side derivations (when adding new computed series), Astro plate components (when adding new charts), and editorial prose (when writing for the site).

**Where things live:**
- `data/raw/` — raw upstream pulls (StatCan, BoC, FRED, CREA, etc.)
- `data/processed/` — derived series (Y/Y, m/m, ratios, etc.)
- `data/site/` — what the website reads (sections.json, panel_data/*.json)
- `editorial/` — the voice canon, methodology canon, review protocol, source cards, blurb files
- `src/pages/` — section pages (inflation.astro, gdp.astro, etc.)
- `src/components/charts/` — chart components per section
- `work/` — strategy, discovery, retainer/subscription planning, and outreach operations (not reader-facing)

**Deliverables expectations:**
- All written work passes through the three review gates before going to the live site.
- All claims have citations (in the `citations` array on each plate, or in source cards in `editorial/source_cards/registry.yaml`).
- All custom analyses use the methodology canon — data exploration + source interviews where applicable.
- All charts use the chart canon.

**Communication:**
- Day-to-day: Slack (or whatever tooling the team adopts)
- Major analytical decisions: discuss with Jay before committing
- Style / voice questions: Jay arbitrates ties; the canon doc settles most

## What's expected of you

- **Take the work seriously.** The firm's brand depends on every piece being thoughtful and correct.
- **Be willing to be wrong.** Tentative conclusions get sharpened (or inverted) by source interviews. The work is iterative.
- **Read the canon docs in full when you have time.** This summary is enough to start; depth comes from reading the underlying documents.
- **Ask Jay when you're unsure.** Better to ask twice than to publish something that violates canon.
- **Bring questions back.** If the methodology doesn't fit a question you're working on, that's a useful signal. The canon evolves with experience.

## Where the full canon lives

When you need depth:

- `CLAUDE.md` at the project root — the highest-level project context, updated as the firm evolves
- `editorial/dashboard_purpose.md` — the publication's purpose and what each section is for
- `editorial/writing-style.md` — the full voice canon
- `editorial/research_methodology.md` — the full methodology canon
- `editorial/review_protocol.md` — the three-gate review process in detail
- `editorial/source_cards/registry.yaml` — the source-card registry (where verified citations live)
- `design/design-system.md` — the visual identity
- `design/canon_reference_panel.md` — the Tier-3 chart canon
- `design/sparkline-canon.md` — the sparkline canon and splash-composition rules
- `work/strategy/` — the firm's commercial strategy (read when relevant to your work; not required for analytical work)

Welcome to the team. Build something good.
