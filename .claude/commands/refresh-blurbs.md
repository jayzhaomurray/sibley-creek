---
name: refresh-blurbs
description: Audit existing blurbs on a section page against the voice canon and current data, flag the stale or off-voice ones, and dispatch writer to regenerate just those surfaces. Doesn't touch good blurbs.
version: 1
---

# /refresh-blurbs

Triggers when the user runs `/refresh-blurbs <section>` (e.g. `/refresh-blurbs labour`) for a whole section, or `/refresh-blurbs <section> <surface>` for a single surface (e.g. `/refresh-blurbs gdp plate-5` for just plate-5's title + interpretation, or `/refresh-blurbs policy section-abstract` for just the abstract). Without an arg, asks which section. With only a section arg, runs the full section as below. With both args, the audit + redraft + re-gate loop runs scoped to ONLY the named surface — Phase 1 still audits with both gates, but Scope-A audit is just the one surface; Phase 2 surfaces only that result for veto; Phase 3 redrafts only that surface; Phase 3.5 re-gates only that surface; Phase 4 reports on just that surface. The rest of the section is not touched.

**Valid surface tokens:**
- `section-abstract` — the section's `blurb.body` in `sections.ts`
- `tile-line` — the section's `tileLine` in `sections.ts`
- `plate-1` / `plate-2` / ... / `plate-N` — the plate's title + interpretationHtml (both treated as one surface unit since they're co-edited)
- `plate-N-title` / `plate-N-blurb` — for finer scope when only one of title or blurb needs refresh

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

3. After the cycle completes, the writer's draft sits in `editorial/blurbs/_cycles/<release-id>.json`. Open it, extract the drafted surface text — but **do NOT apply to the section page yet**. Proceed to Phase 3.5.

## Phase 3.5 — full re-gate loop (MANDATORY, no skipping)

Per `editorial/review_protocol.md` "Redraft re-gating": every redraft re-enters ALL THREE gates before the prose can be applied. Fact alone is not enough — the writer can fail to fix a style flag, reintroduce a banned phrase, paraphrase an MPR formula as our read, or drift to a surface-misfit register. The loop runs until every gate green on the SAME draft, or escalates to the user after N rounds.

For each batch of redrafted surfaces (don't re-gate one surface at a time; batch them so audits run once per round):

### Round 1 — re-gate all three in parallel

Dispatch concurrently:

1. **Fact re-gate** (`fact-checker` audit mode). Scope: every numeric / dated / countable / comparative / framing claim in the new draft, not just claims newly introduced. The writer's "preserved" claims are usually fine — but the surrounding rewrite may have changed the semantic context (e.g., qualifier scope), so verify the full surface. Apply semantic-flexibility discipline per `.claude/agents/fact-checker.md`. Return PASS / FAIL / PASS-WITH-FLAG per surface + per claim.

2. **Style re-gate** (`style-editor` audit mode). Scope: every redrafted surface. Run the explicit length count AND the full canon-coverage checklist per `.claude/agents/style-editor.md`. Return PASS / FAIL per surface + per checklist item.

3. **Surface-fit re-gate** (`editorial-director` audit mode). Scope: does this prose BELONG on THIS surface in THIS context? Cuts canon-jargon leakage, voice-doctrine leakage, template-driven placeholder slots, internal vocabulary that shouldn't be reader-facing. Return PASS / FAIL per surface.

### Compute the round verdict

- If ALL THREE gates return PASS for a surface → that surface is GREEN, queue for apply.
- If ANY gate returns FAIL for a surface → that surface is RED, queue for another redraft round.
- PASS-WITH-FLAG counts as GREEN for the loop, but the flag is surfaced to the user at the end so they can override.

### If any RED surfaces remain → Round 2

Hand the RED surfaces back to the writer with the combined fail list from all three gates. The writer redrafts ONLY the still-red surfaces. Then re-run the three gates on the new draft.

### Round cap = 3

If after 3 rounds any surface is still RED, **STOP**. Do not apply. Surface the residual fail list to the user:

```
Phase 3.5 did not converge after 3 rounds for <N> surfaces:
- plate-2 blurb: STILL FAIL (style: "load-bearing" reintroduced in round 3)
- plate-5 blurb: STILL FAIL (fact: peak figure still wrong despite correction)

Editorial decision required. Recommend manual rewrite or cut.
```

Per `feedback_audit_recommendations_need_user_veto.md`: the loop does not apply unilaterally; the user decides whether to keep working or cut the offending surface.

### Apply

For surfaces that converged to GREEN within the round cap:
- Plate titles → update the `title:` field in `src/pages/<section>.astro`
- Plate blurbs → update the `interpretationHtml:` field
- Section abstract → `src/data/sections.ts` (the section's `blurb.body`)
- Tile line → `src/data/sections.ts` (the section's `tileLine`)
- Sparkline blurb → wherever it lives in `data/site/sections.json`

Run `npm run build` after apply. If build fails, the gate caught something the re-gate missed — surface to user.

**The rule that closes the leak:** the writer's job is prose; verification is the gates' job. Every gate runs on every redraft, every round. A redraft that fails any gate cannot ship to the page — full stop. Three rounds is the cap to prevent infinite loops; beyond that, the writer / draft / data have a deeper problem the user must adjudicate.

## Phase 4 — report

Tight status output:

```
refreshed: <section>. <N> surfaces regenerated, <M> left unchanged.
Phase 3.5 re-gate loop: <R> rounds. <G> surfaces converged GREEN, <U> escalated to user (residual flags).
build: clean.
- plate-2 title: updated (round 1)
- plate-3 blurb: updated (round 2 — fixed "load-bearing" reintroduction)
- plate-5 blurb: ESCALATED — see residual flags above
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
