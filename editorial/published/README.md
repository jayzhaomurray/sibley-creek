# editorial/published/

Publication-ready deep-dive markdown bodies. This directory is the source of truth for what `/research/<slug>/` renders on the public site.

## Convention

- File naming: `<slug>.md` where `<slug>` matches the `slug` field on the corresponding entry in `src/data/sections.ts` `deepDives[]`. E.g. `mortgage-renewal-wall.md`.
- A piece is promoted here only after:
  1. Writer's draft has cleared fact-checker (no TKs, no unverified claims)
  2. Style-editor has done the voice polish pass
  3. Editorial director has approved final copy
- Once a file exists here AND the entry's `publishedPath` field in `sections.ts` points to it, `/research/<slug>/` is publicly routed.

## Safety guard

`src/pages/research/[slug].astro` `getStaticPaths()` filters to entries with `publishedPath` set. No file here -> no slug route built -> no possibility of accidentally leaking a draft. Even URL guessing fails because the route does not exist in the static build output.

## Working drafts

The writer's working copies live in `editorial/drafts/`. That directory is NOT read by any production page. It is the scratchpad: TKs, voice notes, unresolved fact-check items, scaffolding. Drafts never render publicly.
