---
name: demote-chart
description: Demote a live chart out of production — to alternatives (kept under comparison) or archive (parked indefinitely). Removes the SectionLayout registry entry + moves the file + transfers metadata.
version: 1
---

# /demote-chart

Triggers when the user runs `/demote-chart <chart-name>` or `/demote-chart <chart-name> <to-zone>`.

## Behavior

1. **Resolve the live chart.** The arg can be an exact filename, a component name, a natural-language fragment, or absent. Resolution:
   - **Exact** — glob `src/components/charts/<section>/` for the file.
   - **Fragment** — read `SectionLayout.astro`'s `chartRegistry` and `src/pages/<section>.astro` plate entries; fuzzy-match the fragment against plate `title` and `indicator` fields; confirm via `AskUserQuestion`.
   - **No arg** — picker: section, then chart in that section (showing plate titles, not filenames).

   If ambiguous, ask one question via `AskUserQuestion` to disambiguate.

2. **Resolve the target zone** if not provided:
   - alternatives — under comparison to a replacement
   - archive — parked, possibly pinned

3. **Find the chartKey for this chart.** Read `SectionLayout.astro` `chartRegistry` and find the entry mapping to this component.

4. **Ask about the plate slot it leaves behind.** Via `AskUserQuestion`:
   - Replace immediately with a different chart from alternatives (then promote that one — you'd typically use `/promote-chart` for that flow; offer it as a redirect)
   - Leave empty for now (plate will show DATA NOT YET WIRED placeholder)
   - Delete the plate entry from the section page entirely

5. **Ask for manifest metadata** for the destination zone. The user provides:
   - `whatDifferent` (1-2 sentences) — how it differs from what's now live
   - `whyBetter` (1-2 sentences) — why this view is worth keeping
   - `pinned` (only if zone is archive) — boolean; if pinned, ask for an optional `pinnedReason` badge text

6. **Execute:**
   a. `node scripts/move_chart.mjs <live-path> <to-zone-path>` — moves the file, rewrites imports, inserts in destination manifest. The script will need to be told the metadata via a flag or by writing the new manifest entry after the move; coordinate.
   b. Remove the registry entry + import from `SectionLayout.astro`.
   c. Handle the section-page plate per step 4.

7. **Verify**: `npm run build` clean. Report what moved.

## Concurrency safety

Same rules as /promote-chart — don't race `SectionLayout.astro` / `<section>.astro` / `panel_data.py` edits.

## Voice constraints
- Tight status output, ≤150 tokens.
