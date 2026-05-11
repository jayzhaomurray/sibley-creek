# Gate 3 surface-fit sweep — 2026-05-11

Retroactive sweep of all reader-facing prose surfaces against the
three-gate protocol's Gate 3 (surface fit). Editor: editorial-director.
Total surfaces audited: 19. Total cuts: 14 across 9 surfaces.

---

## Per-surface verdicts

### Institutional

- **`src/pages/about.astro`** — CUTS MADE.
  - pageDesc: removed "sharper view of Canada than the median Big-Six
    economics note" (voice doctrine in SEO meta).
  - Body para 1: removed "want a sharper view of Canada than the
    median bank note" (mild voice doctrine).
- **`src/pages/methodology.astro`** — CUTS MADE.
  - Renamed H2 "Voice rules that shape the methodology" → "Citation
    and consensus" and cut the "Big-Six bank economics desks are read
    daily as competitors; they are not cited in running prose as
    authority" sentence (voice doctrine on the live site).
  - Cut the entire H2 "The auto-blurb pipeline" section — pure
    implementation/process talk (pipeline mechanics, Mode 2 reference,
    "human review gate stays") that belongs in editorial canon, not
    reader-facing methodology.
  - Vintage section: replaced "the top of a chartbook unit" with
    "each chart" (canon-jargon cut).
- **`src/pages/404.astro`** — CLEAN. Tight by design.

### Splash

- **`src/components/home/TitleStatement.astro`** — CUTS MADE.
  - Abstract: removed "Most Canadian macro coverage paraphrases
    Big-Six desk notes; we cite..." (voice doctrine in splash hero).
    Replaced with a neutral source-attribution sentence.
- **`src/data/sections.ts` blurbs (7)** — CLEAN. Already terse,
  primary-source-cited, no doctrine.
- **`src/components/home/VignelliColophon.astro`** — CLEAN.
- **`src/pages/og-preview/index.astro`** — CLEAN.

### Section pages

- **`src/pages/gdp.astro`** — CUTS MADE. Lede: stripped "Six plates
  trace..." cataloguing opener. pageDescription: stripped "Six plates
  of chart-with-interpretation."
- **`src/pages/inflation.astro`** — CUTS MADE. Same pattern.
- **`src/pages/labour.astro`** — CUTS MADE. Same pattern + Panel 2
  interpretation: "Pillar E resolves which side" → "The per-capita
  deep dive separates the population side from the weakness side"
  (canon code-letter cut).
- **`src/pages/policy.astro`** — CUTS MADE. Same pattern.
- **`src/pages/markets.astro`** — CUTS MADE. Same pattern.
- **`src/pages/trade.astro`** — CUTS MADE. Same pattern.
- **`src/pages/housing.astro`** — CUTS MADE. Same pattern + Panel 5
  interpretation: "Pillar A deep-dive territory" → "deep-dive
  territory" (canon code-letter cut).

### Deep dives (chrome only)

- **`mortgage-renewal-wall.md`** — CLEAN. Title, deck, date stamp
  appropriate to the deep-dive surface.
- **`boc-fed-divergence.md`** — CLEAN.
- **`per-capita-output.md`** — CLEAN.
- **`us-tariff-repricing.md`** — CLEAN.

### Chart review surfaces

- **`src/pages/chart-improvements.astro`** — CLEAN. Descriptions are
  1-2 sentences each. Page is excluded from sitemap/robots; not a
  reader route.
- **`src/pages/chart-alternatives.astro`** — CLEAN. whatDifferent /
  whyBetter pairs are crisp single-sentence each. Excluded from
  reader routing.

---

## Top 3 surfaces with the most drift

1. **`src/pages/methodology.astro`** — carried both voice doctrine
   (Big-Six-as-competitors framing) AND a full implementation-detail
   section (the auto-blurb pipeline H2). Both belong in
   `editorial/` canon, not on the live methodology page.
2. **The seven section pages** (collective) — all carried the
   "Six/Seven plates trace..." cataloguing opener, which is internal
   chartbook-unit framing leaking into reader-facing ledes. Also
   "plates of chart-with-interpretation" in the SEO descriptions.
   Pattern indicates a single template / brief drift, not seven
   independent failures.
3. **`src/components/home/TitleStatement.astro`** — splash hero
   abstract carried a sentence of explicit voice doctrine
   ("Most Canadian macro coverage paraphrases Big-Six desk notes")
   that is reader-facing positioning prose; cut.

---

## Flagged for restructure (none)

All cuts handled in-place. No surface required a full restructure
beyond the inline edits.
