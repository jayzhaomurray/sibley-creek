# CLAUDE.md — Sibley Creek (macro-research-department)

Read on session start. This file lives in the project root and is
visible to main Claude on every session.

## What this is

Sibley Creek is a Canadian macroeconomic publication, live at
https://sibleycreek.ca. Static Astro site deployed via GitHub Pages,
data pipeline in Python, content authored by Jay Zhao-Murray (ex-Bloomberg
economics editor). The project is a data-driven publication: the dashboard
is almost all data, topic pages are narrated chart packs, deep dives are
research built around a heart of data analysis.

Canonical sources of truth (read on demand):
- `editorial/dashboard_purpose.md` — what the publication exists to be
- `editorial/writing-style.md` — voice + style canon
- `editorial/review_protocol.md` — the three-gate review process (the core ship gate; see below)
- `design/design-system.md` — Vignelli visual canon
- `design/canon_reference_panel.md` — Tier-3 chart canon
- `design/sparkline-canon.md` — Tier-1 sparkline canon + splash composition restraint

## The three-gate review protocol (mandatory before ship)

**Every piece of reader-facing prose must pass three review gates before
shipping live:**

1. **Fact-check** (`fact-checker`): every number, date, citation verified
   against primary sources.
2. **Style polish** (`style-editor`): voice canon applied; concision
   enforced (every word, sentence, paragraph earns its place).
3. **Surface fit** (`editorial-director`): does this content BELONG on
   THIS surface in THIS context? Cuts internal canon-jargon, voice
   doctrine, implementation detail, and template-driven placeholder slots.

Full spec at `editorial/review_protocol.md`. The dispatcher (main Claude)
runs the gates in order before any promote-to-published.

Reader-facing surfaces include: the splash, section pages, deep-dive pages,
About, Methodology, chart titles, chart captions, inter-chart descriptive
copy, footer text. Internal documentation, code comments, verification
reports, and insight bases are NOT reader-facing — they have their own
quality bar.

## Operating discipline

- **Data-driven, by design.** A deep dive without charts is not a Sibley
  Creek deep dive. See `editorial/dashboard_purpose.md` Section 3.
- **Bad versions get tagged and left in place; improved versions live
  alongside.** This is the user's preferred pattern (e.g. chart V2s,
  Pillar A v3 → v4 → v5). User picks on review what to delete.
- **Hero blurbs are written LAST.** Section blurbs first; hero abstract
  synthesizes from them. See `editorial/writing-style.md` Section 8b.
- **No TKs in user-visible output, ever.** If something can't be
  verified or pulled, drop the claim entirely rather than leave a
  placeholder.
- **The brand mark (Sleeping Giant) and the y-axis sparkline canon are
  user-ratified. Do not re-author or re-derive without explicit ask.**

## Stack

- Astro 6.3.1 static-first, zero client JS on the splash
- Python data pipeline (`pipeline/`) → `data/site/sections.json` + per-section panel_data
- GitHub Pages deploy from master via `.github/workflows/deploy.yml`
- Custom domain via `public/CNAME`; no base path
- Visual regression via Playwright at `tests/visual/`

## What NOT to do

- Don't dispatch a writer / chart-builder without naming the surface
  and the voice register the surface demands (otherwise drift).
- Don't promote any deep dive without all three review gates passing.
- Don't add a content slot to a template and let it ship with
  placeholder fill — gate 3 (surface fit) cuts the slot.
- Don't cite Big-Six bank economists as authority (consensus aggregated
  as median is fine; named as voice is not).
- Don't run the auto-blurb pipeline without verifying `ANTHROPIC_API_KEY`
  is set — or use the boc-tracker `subprocess.run(["claude", "--print"])`
  pattern to bypass the API-key requirement (port to `pipeline/blurbs/`).
