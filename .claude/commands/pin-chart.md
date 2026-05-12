---
name: pin-chart
description: Toggle the pinned flag on an archived chart. Pinned charts render at the top of /chart-archive in a ★ Pinned zone. Use /pin-chart <name> to pin, /pin-chart <name> off to unpin.
version: 1
---

# /pin-chart

Triggers when the user runs `/pin-chart <chart-name>` (pin) or `/pin-chart <chart-name> off` (unpin).

## Behavior

1. **Resolve the chart.** The arg can be an exact name, a natural-language title fragment, or absent. Resolution:
   - **Exact** — glob `src/components/charts/_archive/<section>/` for the file.
   - **Fragment** — read every `_archive/<section>/index.ts`; fuzzy-match the fragment against `title` / `whatDifferent`; confirm.
   - **No arg** — picker: section, then chart by title.

   The chart must be in archive. If you find it in `_alternatives/` or live, tell the user to `/move-chart` it to archive first.

2. **Determine action.** If the second arg is `off` or `unpin`, this is an unpin. Otherwise it's a pin.

3. **For pin:** Optionally ask for `pinnedReason` — a short badge text (one phrase, e.g. "good geometry idea", "saved methodology", "future deep-dive material"). User can skip.

4. **Edit the archive section's `index.ts`.** Find the entry for this chart by component name or file. Set `pinned: true` (or remove it, on unpin). If pinning, also set `pinnedReason` if the user gave one.

5. **Verify**: `npm run build` clean. The chart now appears in the ★ Pinned zone at the top of `/chart-archive` (or moves back to the archive list if unpinned).

## Voice constraints
- One-line status output. Format examples:
  - `pinned: Alt_Panel2LabourStocksYoY (reason: "good geometry idea").`
  - `unpinned: Panel2URDriversIndexedWedge.`
