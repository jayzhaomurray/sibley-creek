---
name: move-chart
description: Move a chart between holding zones (alternatives ↔ archive) or to/from live. Wraps scripts/move_chart.mjs and handles the index.ts entry transfer + SectionLayout registry update + page wiring as needed.
version: 1
---

# /move-chart

Triggers when the user runs `/move-chart <chart-name> <to-zone>` or `/move-chart <chart-name>` (skill asks which zone).

## Zones

- **`alternatives`** — `src/components/charts/_alternatives/<section>/` — under active comparison to a live chart
- **`archive`** — `src/components/charts/_archive/<section>/` — parked indefinitely
- **`live`** — `src/components/charts/<section>/` — wired into the section page

## Behavior

1. **Resolve the chart.** The arg can be:
   - **Exact identifier** — a component name (`Panel2URDrivers`), an alt filename (`Alt_Panel2LabourSharesOfPop`), or a relative path. Glob `_alternatives/*/`, `_archive/*/`, and `<section>/` to find it.
   - **Natural-language fragment** — a phrase the user remembers (e.g. `"Y/Y growth"`, `"the wedge chart"`, `"hours vs headcount"`). Read every `index.ts` manifest in `_alternatives/` and `_archive/`; fuzzy-match the fragment against `title` and `whatDifferent` fields. Confirm via `AskUserQuestion`: "Did you mean: <title> (`<filename>`)?"
   - **No arg at all** — multi-step picker. Ask via `AskUserQuestion`: (a) which section, (b) which chart in that section. Show entries by their `title` field, not the technical filename. Filenames appear only in the final status line.

   If the arg matches >1 chart in any path, show the candidates by title via `AskUserQuestion` and let the user pick.

2. **Resolve the target zone.** If the user gave a zone, use it. Otherwise ask via `AskUserQuestion`:
   - alternatives / archive / live

3. **Run the path-aware mover** to do the file move + import rewrite + manifest transfer:
   ```
   node scripts/move_chart.mjs <from-path> <to-path>
   ```
   The script handles: `git mv`, depth-delta import rewriting, source-manifest entry removal, destination-manifest entry insertion (for alts/archive only).

4. **If destination is `live`**: ALSO update the SectionLayout registry. Read `src/layouts/SectionLayout.astro`, find the `chartRegistry` object, add one line: `"<chartKey>": <ComponentName>`. Ask the user for the `chartKey` if it can't be inferred from the alt's `file` field (which usually carries the slot it was built to fill).

5. **If source is `live`**: ALSO remove the SectionLayout registry entry for that chartKey. The plate on the section page will show "DATA NOT YET WIRED" until something else gets registered or the plate is removed from `<section>.astro`.

6. **Verify**: `npm run build` clean. Report what moved and which files changed.

## Concurrency safety

If another agent is in flight on `SectionLayout.astro` or the destination `<section>.astro`, queue this move instead of dispatching. Don't race shared files.

## Voice constraints
- Cap response at ~150 tokens for status-only output.
- Format: `moved: <name> → <zone>. registry: <updated|skipped>. build: <clean|N errors>.`
