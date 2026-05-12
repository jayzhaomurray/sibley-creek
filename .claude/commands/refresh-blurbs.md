---
name: refresh-blurbs
description: Audit existing blurbs on a section page against the voice canon and current data, flag the stale or off-voice ones, and dispatch writer to regenerate just those surfaces. Doesn't touch good blurbs.
version: 1
---

# /refresh-blurbs

Triggers when the user runs `/refresh-blurbs <section>` (e.g. `/refresh-blurbs labour`). Without an arg, asks which section.

## Phase 1 — audit

For the named section, gather everything that has reader-facing prose:

1. **Section abstract** — the top-of-page editorial blurb in `src/pages/<section>.astro` (look for the `sectionAbstract` or similar field on the page).
2. **Plate titles** — the `title:` field of each plate entry.
3. **Plate interpretation blurbs** — the `interpretationHtml:` field of each plate entry.
4. **Sparkline blurb** — the section's splash blurb in `data/site/sections.json` (`spark_blurb` or similar field).

For each piece of prose, run two checks **in parallel**:

A. **Style audit** (dispatch `style-editor` agent in audit mode). Brief: "Read this prose. Score against `editorial/writing-style.md` voice canon. Flag if any of: load-bearing language, math symbols in prose, sentence-form on the canvas, Big-Six citation, voice-doctrine leakage, banned vocabulary, awkward register. Return PASS or FAIL + 1-line reason."

B. **Fact-check audit** (dispatch `fact-checker` agent in audit mode). Brief: "Read this prose. Cross-reference every number, date, and citation against the latest data in `data/site/panel_data/<section>.json` and `data/site/sections.json`. Flag if any of: stale numbers (>1 vintage old), numbers that don't match current data, citation drift (e.g. wrong StatCan table number). Return PASS or FAIL + 1-line reason."

Surfaces that pass both audits are LEFT ALONE. Surfaces that fail either audit go on the regen list.

## Phase 2 — surface review

Print the regen list to the user:

```
Audit complete for <section>. <N> surfaces flagged:

- plate-2 title: "Labour force is growing..." — FAIL (style): vintage-locked editorial copy; doesn't generalize
- plate-3 blurb: "...running at 3.1% in March..." — FAIL (fact): March is two vintages old; current is May 2026
- sparkline blurb — PASS
- section abstract — PASS

Regenerate the 2 flagged surfaces? (y/n)
```

If the user says no or rejects specific items, stop. If yes, proceed to phase 3.

## Phase 3 — regenerate

For each approved-flagged surface:

1. Identify the surface_id by looking it up in `pipeline/blurbs/section_context.py` for that section. The surface_id format is e.g. `labour_panel_2_blurb` or `labour_section_abstract`.

2. Run the auto-blurb pipeline for just that surface:
   ```
   python -m pipeline.blurbs.run --release-id <section>_<release-type>_<vintage> --section <section> --surface <surface_id>
   ```
   The `<release-type>` and `<vintage>` come from the section's current data vintage (read `data/site/panel_data/<section>.json` `generatedAt` and the section's `release_key` from `section_context.py`).

3. After the cycle completes, the writer's draft sits in `editorial/blurbs/_cycles/<release-id>.json`. Open it, extract the drafted surface text, and apply it to the section page:
   - Plate titles → update the `title:` field in `src/pages/<section>.astro`
   - Plate blurbs → update the `interpretationHtml:` field
   - Section abstract / sparkline blurb → wherever they live

4. After all regens land, run `npm run build` and report.

## Phase 4 — report

Tight status output:

```
refreshed: <section>. <N> surfaces regenerated, <M> left unchanged. build: clean.
- plate-2 title: updated
- plate-3 blurb: updated
```

## Constraints

- **Three-gate review still applies before any prose ships live.** Even after refresh-blurbs lands a draft, the user reviews it. The skill writes drafts; the user accepts or rejects. Per CLAUDE.md: every reader-facing prose passes fact-check + style polish + surface fit before promotion to published.
- **Don't touch passing surfaces.** The whole point is to leave good work alone.
- **Don't run the full cycle if only one surface failed.** Use `--surface <id>` to scope.

## Concurrency safety

- The auto-blurb pipeline writes to `editorial/blurbs/_cycles/`. If another agent is running an auto-blurb cycle, queue this one.
- Don't dispatch this skill while a section page is being edited by another agent.

## Voice constraints
- Cap status output at ~150 tokens.
