# Chart No-Drift Workflow

**Status:** Process guardrail, 2026-06-02. Internal working memory. This does
not replace `design/design-system.md` or `design/canon_reference_panel.md`; it
turns them into a workflow future agents can follow.

## Vocabulary

Use surface names, not tier numbers.

- **Overview charts:** dashboard/splash/overview mini charts and sparklines.
- **Chartbook charts:** full topic-page charts inside `ChartbookUnit`.
- **Feature charts:** bespoke research/deep-dive charts.

## Hard Boundary

Chartbook prose lives outside the SVG.

- Plate title: page file / `ChartbookUnit` title slot.
- Interpretation blurb: page file / `ChartbookUnit` interpretation slot.
- Source line: page file / `ChartbookUnit` source slot.
- SVG: axes, ticks, direct labels, compact subpanel labels, numeric callouts,
  short data annotations, forecast/recession/reference labels.

If a text string is a sentence, it probably does not belong inside a chart SVG.

## Template-First Rule

Every new chart starts by choosing a chart family:

1. line time series
2. two-panel composite
3. small multiples
4. signed bars
5. stacked bars / contribution bars
6. special shell: scatter, slopegraph, dumbbell, other exceptional forms

Bespoke SVG is allowed only after naming why the chart cannot use an existing
family.

## Agent Workflow

Before writing a chart:

1. Identify the surface: overview, chartbook, or feature.
2. Pick the chart family above.
3. Reuse the closest live chart/template and preserve its chrome.
4. Put prose only in the page/`ChartbookUnit` slots.
5. Keep SVG labels short.
6. Run the contract check:

```bash
node scripts/check_chartbook_contract.mjs
```

Before a copy-placement pass:

1. Edit page files or citation sidecars.
2. Do not edit `src/components/charts/**` unless replacing compact chart labels
   or annotation words.
3. If a chart needs geometry changes, split that into a separate chart-builder
   pass.

Before a chart-geometry pass:

1. Do not change plate titles, blurbs, source text, or section abstracts.
2. Only edit chart components and data-transform code needed for the chart.
3. Run visual QA after source checks.

## Current Enforcement

`scripts/check_chartbook_contract.mjs` catches the most common drift class:

- long visible SVG `<text>` strings
- section-accent token use in chart component `fill`/`stroke`
- warning for bespoke SVGs that do not obviously use `0 0 720 405`

It is intentionally not wired into `npm run build` while active fiscal work is
in flight. Wire it after current chart cleanup if the working tree is stable.

## Rule Of Thumb

Allowed inside SVG:

- `FORECAST`
- `Revenues`
- `Program spending`
- `Operating`
- `Capital`
- `1996 peak`
- `66.6%`

Not allowed inside SVG:

- `The operating balance crosses into surplus by 2028-29--capital spending holds the total down.`
- `The deficit has been the rule, not the exception, since the financial crisis.`

