---
name: fix-chart
description: Auto-dispatch chart-builder to look at a visually broken chart, diagnose the problem (overflow, spillover, weird scaling, clipped labels), and fix it — without the user spelling out what's wrong.
version: 1
---

# /fix-chart — diagnose-and-fix a visually broken chart

Triggers when the user runs `/fix-chart` (optionally with an argument: a plate id like `plate-2`, a chart key like `labour-panel-2`, an `.astro` file path, or no arg at all).

## 1. Identify the target

Resolve which chart, in this order:

1. **Explicit arg** — if the user passed `plate-2`, `labour-panel-2`, or a path, use that.
2. **Pasted screenshot** — if the user attached an image in the current turn, that IS the target. Find the chart that matches the screenshot from page context.
3. **Most-recently-discussed plate in this session** — scan back through the conversation for the last chart that was rebuilt, edited, or mentioned by name.
4. **If still ambiguous** — ask the user which chart, one short question.

Locate the underlying `.astro` component, the route that renders it (e.g. `src/pages/labour.astro`), and the built `dist/<route>/index.html`.

## 2. Capture current state

- If the user pasted a screenshot, that's the visual evidence. Pass its path to the agent.
- If `dist/<route>/index.html` is older than the `.astro` source, run `npm run build` first so the agent inspects current geometry.
- Note the chart's viewBox bounds (look for `viewBox="0 0 720 405"` or similar in the component header comment) and the plot-area margins (`M_L`, `M_R`, `M_T`, `M_B`, or equivalents).

## 3. Dispatch chart-builder

Background dispatch. Brief includes:

- The exact file path of the chart component
- The dist HTML path
- Screenshot path if the user pasted one
- The viewBox + plot-area bounds
- Instruction: **"Diagnose and fix the visual problem without asking what's wrong. The user has signalled the chart is visually broken; figure it out from the screenshot (if provided) and from inspecting the SVG geometry."**
- Common failure modes to scan for (give the agent a checklist, not a single suspect):
  - **Text outside the viewBox** — any `<text>` element with x/y beyond the canvas bounds
  - **Text outside the plot frame** — labels positioned in the right/left/bottom gutter that overflow into other content
  - **Labels clipped by the SVG edge** — text at `x > VB_W` or `x < 0`
  - **Y-axis tick labels colliding with the left edge or bleeding off the right edge**
  - **Direct labels at line termini overlapping each other or other axis labels**
  - **Bars or lines extending beyond the plot frame** — usually a clip-path missing or wrong
  - **Title or sub-panel title overlapping the plot area**
  - **Reference-line labels positioned at impossible coordinates**
- Constraints carry forward:
  - NO sentence annotations on canvas
  - NO duplicate direct labels
  - NO methodology micro-notes on canvas
  - Word-only direct labels
- Verify: `npm run build` clean, overlap detector clean, screenshot-vs-fix sanity check
- Report back what was wrong and what was fixed

## 4. Concurrency safety

- If another chart-builder agent is in flight on the same plate, **DO NOT** dispatch concurrently — wait for the in-flight agent to land first. The concurrent-edits-on-shared-files pattern has caused SSR breakage in past sessions.
- If the broken chart is one of Plates 1/2/3/etc. on a page where the page-reflow is in flight, queue this fix until after the reflow lands.

## 5. Report

After dispatch, output (one or two lines):

- `dispatched: fix-chart on <component>; diagnosing <category>`
- Or if blocked: `blocked: another agent is editing <file>, will queue`

Don't recap, don't summarize, don't ask follow-up.

## Voice constraints (carry forward from project canon)

- Cap response at ~300 tokens
- No math symbols in prose
- Match the standing tracker register
