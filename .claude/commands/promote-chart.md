---
name: promote-chart
description: Promote a chart from alternatives → live. Handles the file move + import rewrite + SectionLayout registry update + section-page plate entry + auto-demote of the displaced live chart, in one command.
version: 1
---

# /promote-chart

Triggers when the user runs `/promote-chart <chart-name>` or `/promote-chart <chart-name> <plate-id>`.

## Behavior

1. **Resolve the alt.** The arg can be an exact filename, an alt component name, a natural-language title fragment, or absent. Resolution:
   - **Exact** — glob `_alternatives/<section>/` for the file.
   - **Fragment** — read all `_alternatives/<section>/index.ts` manifests; fuzzy-match against `title` and `whatDifferent` fields; confirm via `AskUserQuestion` ("Did you mean: <title>?").
   - **No arg** — multi-step picker: section first, then chart by title within that section.

   If ambiguous, show candidates by title via `AskUserQuestion` and let the user pick.

2. **Identify the destination plate slot.** Either from the arg, or read the alt's `index.ts` entry — the `whatDifferent` / `whyBetter` text usually names the plate. If unclear, ask the user (e.g. "Which plate slot? labour-panel-2 / labour-panel-3 / labour-panel-4 / other").

3. **Identify what's currently live in that slot.** Read `SectionLayout.astro`'s `chartRegistry` for the chartKey. The current component is the one being displaced.

4. **Ask about the displaced chart.** One question via `AskUserQuestion`:
   - Move to alternatives (kept under comparison)
   - Move to archive (parked indefinitely; offer the pinned-yes/no toggle)
   - Just unwire (leave the file in `<section>/` but remove from registry — rare)

5. **Execute the moves in this order:**
   a. Move displaced chart out: `node scripts/move_chart.mjs <live-path> <new-zone-path>` (uses the user's choice from step 4). This also updates the destination manifest.
   b. Move the alt in: `node scripts/move_chart.mjs <alt-path> <live-path>`. This removes from the alternatives manifest. No destination manifest insertion (the live folder doesn't have one).
   c. Update `SectionLayout.astro` `chartRegistry`: replace the old component import + the registry entry with the new component. Read the file, make the two edits surgically.

6. **Seed the section-page plate entry** in `src/pages/<section>.astro`. The promoted chart's alt-manifest entry has `title` and `whatDifferent` — use those to draft the new `indicator` and a working `title`. The `interpretationHtml` becomes a placeholder for the writer.

7. **If the alt's `index.ts` entry signalled `<dispatch writer immediately to draft from chart data>` for the title or blurb** (from the chart-spec form's default), dispatch the `writer` agent in parallel to draft those — pass the chart's data + the editorial frame from the alt's `whatDifferent` / `whyBetter` fields.

8. **Verify**: `npm run build` clean. Run the overlap detector. Report what moved + what's wired.

## Concurrency safety

- If another agent is in flight on `SectionLayout.astro` or `<section>.astro` or `panel_data.py`, **queue this promotion** — don't race. Tell the user it's queued and will fire when the in-flight agent lands.

## Voice constraints
- Tight status output. Format example:
  - `promoted: Alt_Panel2LabourSharesOfPop → labour-panel-2.`
  - `displaced: Panel2LabourStocks → archive (pinned: yes).`
  - `writer: dispatched for title + blurb.`
  - `build: clean.`
