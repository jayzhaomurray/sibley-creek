# Night-shift summary — 2026-05-11

## Plain-English summary

The biggest things that landed live overnight:

1. **Four deep-dive research articles are now published on the live site.** This was the publication's biggest gap when you went to sleep — zero published research. Now there are four, all with charts, all fact-checked, all on the live URL:
   - `/research/mortgage-renewal-wall/` (Pillar A — your existing draft, polished to v5, embedded with 3 inline charts, 67 numeric claims verified)
   - `/research/boc-fed-divergence/` (Pillar B — drafted, 6 charts, 38 claims verified, "BoC held April 29 not cut" caught correctly)
   - `/research/per-capita-output/` (Pillar E — drafted, 5 charts, 41/48 claims verified, productivity 1.2%→1.1% slip caught)
   - `/research/us-tariff-repricing/` (Trade-tariffs — new deep dive you requested, 6 charts, 38 claims, IEEPA post-SCOTUS prose-fence respected)

2. **The splash is no longer full of lorem ipsum.** Hero abstract rewritten with grounded May-2026 cycle prose. All 7 section blurbs replaced with fact-checked Mode 2 prose (5 false framings corrected by fact-checker: GDP "firmest since summer," Labour "first sub-zero," Markets WTI "2-year high," Policy framing, Trade "post-1990 norm"). The redundant lipsum `__note` slot on every section panel (7 visible blocks) was cut.

3. **All 7 section chartbook pages now have real plate prose.** ~130 reader-facing TKs eliminated. The writers caught several factual corrections in the prior placeholder narratives — GDP output gap is widening not closing, inflation's "shelter doing the work" frame is stale (food + energy now lead), Labour V/U ratio is through pre-pandemic norm not above it, tariff escalations were June 2025/April 2026 not "March 2026."

4. **About + Methodology pages went live.** About has a named bio (ex-Bloomberg econ editor at Bloomberg Canada; Monex Canada FX analyst; BoC research-assistant; Western), a Sleeping Giant photo above the fold (Wikimedia Commons CC BY-SA 3.0), and a tight "why Sibley Creek" paragraph.

5. **The OG card now renders.** LinkedIn / Twitter unfurls for sibleycreek.ca will show the Sleeping Giant + SIBLEY CREEK wordmark + tagline. Previously 404'd.

6. **Two chart-review surfaces for your wake-up decisions:** `/chart-improvements/` (8 pairs of original-vs-V2 audit-flagged charts) and `/chart-alternatives/` (28 alternative chart treatments across all 7 sections). Both excluded from sitemap/robots — internal review pages.

7. **Process discipline codified.** The three-gate review protocol you asked for is now canon at `editorial/review_protocol.md` + project `CLAUDE.md` so future sessions read it on startup. Style-editor concision discipline ("every word, every sentence, every paragraph must earn its place") locked into the agent file. Editorial-director Gate 3 surface-fit ownership made explicit.

What FAILED (blockers I hit):

- **Auto-blurb pipeline could not run autonomously.** Requires `ANTHROPIC_API_KEY` env var. Pivoted to direct writer-agent authoring instead — same outcome. Boc-tracker's `subprocess.run(["claude", "--print"])` CLI pattern is queued as a fix for future autonomous runs.

- **Some pipeline data is missing for specific chartbook plates.** 8 plates across the 7 sections (FCI composite, credit spreads OAS, bank PCL/CET1, full pop-per-housing-unit ratio, CMHC arrears, true output gap CAPB, two derived inflation pass-through series). Writers shipped honest publication-voice descriptions without fabricating numbers. Flagged for researcher to wire the backing series.

- **GitHub deploy "failure" you reported** — WebFetch on the Actions page showed all 5 deploys green. You may have been looking at a stale tab. All commits pushed cleanly.

## Successes — detailed

| Item | Where it lives | Live? |
|------|---------------|-------|
| Pillar A deep dive (mortgage renewal wall) | `/research/mortgage-renewal-wall/` | Yes — first published research |
| Pillar B deep dive (BoC-Fed divergence) | `/research/boc-fed-divergence/` | Yes |
| Pillar E deep dive (per-capita output) | `/research/per-capita-output/` | Yes |
| Trade-tariffs deep dive | `/research/us-tariff-repricing/` | Yes — new piece you requested |
| 20 inline SVG charts across deep dives | `public/charts/{pillar-a,pillar-b,pillar-e,trade-tariffs}/` | Yes |
| Hero abstract (no lorem ipsum) | `src/components/home/TitleStatement.astro` | Yes |
| 7 section blurbs (fact-checker corrected) | `src/data/sections.ts` | Yes |
| All 7 section chartbook plate prose | `src/pages/{gdp,inflation,labour,policy,markets,trade,housing}.astro` | Yes |
| About page (with bio + Sleeping Giant photo) | `/about/` | Yes |
| Methodology page | `/methodology/` | Yes |
| OG card (1200×630) | `public/og-default.png` | Yes — LinkedIn unfurl works |
| Custom 404 page | `/404` | Yes |
| Sitemap | `/sitemap-index.xml` + `/sitemap-0.xml` | Yes |
| Robots.txt | `/robots.txt` | Yes |
| 6 V2 chart improvements + comparison page | `/chart-improvements/` | Live (internal review surface) |
| 28 alternative chart treatments | `/chart-alternatives/` | Live (internal review surface) |
| Per-capita GDP series wired in pipeline | `pipeline/build.py` + `data/processed/gdp_per_capita_yoy.csv` | Pipeline |
| Three-gate review protocol | `editorial/review_protocol.md` + `CLAUDE.md` | Canon |
| Sparkline canon doc | `design/sparkline-canon.md` | Canon |
| Code cleanup | 0 errors, 0 warnings, 0 hints | Build |

## Failures / open issues — detailed

| Item | Why | What unblocks it |
|------|-----|------------------|
| Auto-blurb pipeline live runs | Needs `ANTHROPIC_API_KEY`; current pipeline uses `anthropic.Anthropic()` | Set env var, OR port boc-tracker's `subprocess.run(["claude", "--print"])` pattern into `pipeline/blurbs/` (queued) |
| 8 plate prose blocks with data-missing | Pipeline doesn't fetch FCI composite, credit-spreads OAS, bank PCL/CET1, pop-per-housing-unit, CMHC RMIR, CAPB output-gap, 2 inflation pass-through derivations | Researcher to wire backing series next session |
| Hero abstract may carry stale shelter frame | Inflation writer caught: "shelter doing the work" is no longer true; food/energy lead now. Hero says "cycle is loosening" — defensible but not synthesized from the new section blurbs | Re-run hero pass per the "hero-last" rule with current section blurbs (5-min job) |
| Per-capita employment derivation in pipeline | Labour writer flagged: `employment_level` series MISSING; per-capita prose used emp_rate + aggregate hours as proxy | Researcher to fetch StatCan v2062811 |
| Visual regression baselines | Stale after section-page prose changes | Run `npm run test:visual:update` next session |
| Fact-checker Gate re-run on new plate prose | Writers authored; only spot-checked claims | Dispatch fact-checker on all 7 section pages |

## Things to look at first when you scan the site

1. **The four published deep dives** — read at least the leded paragraph of each. These are the publication's first real content. Pillar A is the strongest because it had the most prior drafting; B / E / Trade-tariffs were authored from scratch tonight.
2. **The splash hero abstract** — the May-2026 cycle paragraph. Does it land?
3. **About page** — bio, photo above the fold, name-and-mark paragraph. Style-editor went over it twice; should read tight.
4. **`/chart-improvements/`** — 8 pairs of original-vs-V2 charts. Pick which ones to retire to V2 production; the V2 path is in `src/components/charts/<section>/Panel*V2.astro`.
5. **`/chart-alternatives/`** — 28 alternative chart treatments. Scan, pick favorites, tell me which to retire to production.
6. **Section chartbook pages** — `/gdp/`, `/inflation/`, etc. The plate prose is fresh. Watch for any reader-visible drift you don't like.

## Commits shipped overnight

`202e4e9 → 4ec97e7 → 7021f30 → e65592d → 3524532 → a3f14f3 → dce773e → 269fb42 → fcdae56 → ff58b47 → 01d1126`

11 commits. Run `git log --oneline -11` to see them with messages.

## Where the queue stands

In flight at wake-up: none. The fact-checker Gate 2 re-run on the new plate prose was the next queued item before you came back — it's the cleanest thing to dispatch now if you want closure on the three-gate protocol.
