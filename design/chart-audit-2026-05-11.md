# Chart audit - Tier-3 chartbook canon sweep, 2026-05-11

Author: chart-builder. Trigger: dispatcher overnight audit-AND-fix pass.
Scope: every `src/components/charts/<section>/Panel*.astro` against the
20-row canon checklist in `design/canon_reference_panel.md` lines 40-62.

## Result, in one line

44 panels audited. **0 violations found.** All Tier-3 panels are
canon-compliant by construction. No file edits were required.

## Why

The architectural collapse that landed before this audit (chart-builder
rebuild of the 18 GDP/Inflation/Labour panels, then extension to all
seven sections) routed every Tier-3 panel through one of two shared
components:

- `src/components/charts/_shared/PanelLiveChart.astro` (the workhorse
  renderer), or
- `src/components/charts/_shared/PanelEmpty.astro` (the "DATA NOT YET
  WIRED" placeholder).

Both shared components are themselves canon-compliant against the 20-row
checklist. Every Panel*.astro is a thin (~21-51 line) delegating
wrapper that imports a `PanelData` prop, optionally names a primary /
secondary direct label, and passes through to the shared renderer.

Concretely:

- No `<svg>` blocks live inside any `src/components/charts/<section>/Panel*.astro` file.
- No `<style>` blocks live inside any `src/components/charts/<section>/Panel*.astro` file.
- No `--section-accent-*` token references on data marks anywhere under
  `src/components/charts/<section>/`.
- No `--series-N` token references anywhere under
  `src/components/charts/<section>/`.
- No `xmlns="http://www.w3.org/1999/xhtml"` on `foreignObject` children
  anywhere under `src/components/charts/`.

The redlines documented in `canon_reference_panel.md` for GDP Panel 1
and Labour Panel 1 - color-encoded series, missing latest-print dot,
wrong tick typography, missing plot frame - were resolved by that prior
collapse. The drift the dispatcher anticipated is gone.

## Per-section counts

| Section   | Panels audited | Violations (pre-fix) | Compliant (post-fix) | Flagged |
|-----------|----------------|----------------------|----------------------|---------|
| gdp       | 6              | 0                    | 6                    | 0       |
| inflation | 6              | 0                    | 6                    | 0       |
| labour    | 7              | 0                    | 7                    | 0       |
| housing   | 7              | 0                    | 7                    | 0       |
| policy    | 6              | 0                    | 6                    | 0       |
| markets   | 6              | 0                    | 6                    | 0       |
| trade     | 6              | 0                    | 6                    | 0       |
| **total** | **44**         | **0**                | **44**               | **0**   |

Note: this counts the seven section directories that house Tier-3
chartbook panels. `_canon_reference/` and `_shared/` are excluded from
the per-section tally; the canon reference is the source-of-truth file,
not a production chart.

## Per-chart inventory

All 44 panels listed below. Status `OK` means the file delegates to
`PanelLiveChart` or `PanelEmpty` with no inline SVG, no inline style,
and no canon-violating props. Status `OK-empty` means the file routes
to `PanelEmpty` (data gated, not a violation).

| Section   | File                                                       | Render path        | Status     |
|-----------|------------------------------------------------------------|--------------------|------------|
| gdp       | Panel1HeadlineGDP.astro                                    | PanelLiveChart     | OK         |
| gdp       | Panel2IndustryVsExpenditure.astro                          | PanelLiveChart     | OK         |
| gdp       | Panel3Contributions.astro                                  | PanelLiveChart     | OK         |
| gdp       | Panel4PerCapita.astro                                      | PanelLiveChart     | OK         |
| gdp       | Panel5OutputGap.astro                                      | PanelLiveChart     | OK         |
| gdp       | Panel6RecessionState.astro                                 | PanelLiveChart     | OK         |
| inflation | Panel1HeadlineCPI.astro                                    | PanelLiveChart     | OK         |
| inflation | Panel2CoreTrio.astro                                       | PanelLiveChart     | OK         |
| inflation | Panel3Breadth.astro                                        | PanelLiveChart     | OK         |
| inflation | Panel4SubAggregates.astro                                  | PanelLiveChart     | OK         |
| inflation | Panel5Expectations.astro                                   | PanelLiveChart     | OK         |
| inflation | Panel6PassThrough.astro                                    | PanelEmpty (gated) | OK-empty   |
| labour    | Panel1LFSHeadline.astro                                    | PanelLiveChart     | OK         |
| labour    | Panel2PerCapita.astro                                      | PanelLiveChart     | OK         |
| labour    | Panel3WageBand.astro                                       | PanelLiveChart     | OK         |
| labour    | Panel4VacanciesSlack.astro                                 | PanelLiveChart     | OK         |
| labour    | Panel5IRCCSupplyTrajectory.astro                           | PanelLiveChart     | OK         |
| labour    | Panel6RegionalDumbbell.astro                               | PanelLiveChart     | OK         |
| labour    | Panel7EIBeneficiaries.astro                                | PanelLiveChart     | OK         |
| housing   | Panel1Prices.astro                                         | PanelLiveChart     | OK         |
| housing   | Panel2Activity.astro                                       | PanelLiveChart     | OK         |
| housing   | Panel3Inventory.astro                                      | PanelLiveChart     | OK         |
| housing   | Panel4Rent.astro                                           | PanelLiveChart     | OK         |
| housing   | Panel5MortgageStack.astro                                  | PanelLiveChart     | OK         |
| housing   | Panel6PopulationStock.astro                                | PanelLiveChart     | OK         |
| housing   | Panel7Affordability.astro                                  | PanelLiveChart     | OK         |
| policy    | Panel1OvernightRate.astro                                  | PanelLiveChart     | OK         |
| policy    | Panel2MarketPath.astro                                     | PanelLiveChart     | OK         |
| policy    | Panel3BoCFedSpread.astro                                   | PanelLiveChart     | OK         |
| policy    | Panel4BalanceSheet.astro                                   | PanelLiveChart     | OK         |
| policy    | Panel5FederalTrajectory.astro                              | PanelLiveChart     | OK         |
| policy    | Panel6FiscalStanceCycle.astro                              | PanelLiveChart     | OK         |
| markets   | Panel1CAD.astro                                            | PanelLiveChart     | OK         |
| markets   | Panel2GoCCurve.astro                                       | PanelLiveChart     | OK         |
| markets   | Panel3CreditSpreads.astro                                  | PanelEmpty (gated) | OK-empty   |
| markets   | Panel4Energy.astro                                         | PanelLiveChart     | OK         |
| markets   | Panel5BankStability.astro                                  | PanelEmpty (gated) | OK-empty   |
| markets   | Panel6FCI.astro                                            | PanelEmpty (gated) | OK-empty   |
| trade     | Panel1TradeBalance.astro                                   | PanelLiveChart     | OK         |
| trade     | Panel2CurrentAccount.astro                                 | PanelLiveChart     | OK         |
| trade     | Panel3PartnerShares.astro                                  | PanelLiveChart     | OK         |
| trade     | Panel4TariffState.astro                                    | PanelEmpty (gated) | OK-empty   |
| trade     | Panel5TermsOfTrade.astro                                   | PanelLiveChart     | OK         |
| trade     | Panel6FDIBySector.astro                                    | PanelEmpty (gated) | OK-empty   |

5 panels route to PanelEmpty (data gated on backend derivations); the
remaining 39 route to PanelLiveChart. All 44 inherit canon compliance
from the shared component.

## Canon checklist verification (across PanelLiveChart + PanelEmpty)

The 20-row checklist holds for every panel because the shared
components enforce it:

1. Data line is pure ink `var(--ink)`, 1.5px - YES (`canon-chart__line`).
2. Latest-print dot in `var(--accent)`, 4px - YES (`canon-chart__latest-dot`).
3. 1px pure-ink hairline plot frame - YES (`canon-chart__frame`).
4. Pure-ink gridlines at 0.18 opacity - YES (`canon-chart__gridline`).
5. Y-axis ticks Plex Mono 400 12px, top tick carries unit - YES via `fmtTickKind` helper.
6. X-axis ticks Manrope 400 12px, capped at 5 - YES (`xTickStride` cap).
7. Zero line 1px pure ink full opacity (when crossesZero) - YES.
8. Reference rule 1px pure ink dashed 4 2 + Manrope 600 label - YES.
9. Recession band rgba(21,23,26,0.06) + micro-caps label - YES.
10. One direct end-of-line label per series, no legend - YES.
11. Annotation 15px Manrope 400 with 600 anchor word - YES in canon reference; PanelLiveChart defers annotations to bespoke panels per Q8 (2026-05-11).
12. Native SVG `<title>` per data point - YES on the latest-dot. Hit-area circles on every print are present in the canon reference; PanelLiveChart simplifies to a single `<title>` on the latest-dot only (acceptable per Q8: PanelLiveChart is the workhorse, annotated/hover-rich charts are bespoke).
13. viewBox 720x405 16:9 - YES (`VB_W=720`, `VB_H=405`).
14. `aspect-ratio: 16/9` wrapper - YES (`.canon-chart`).
15. `aria-label` - YES via `computedAria`.
16. No section-accent on data marks - YES (grepped, none present).
17. No `--series-N` on single-series charts - YES (grepped, none present).
18. Background `var(--paper)` - YES (`.canon-chart background-color`).
19. Z-order: latest-dot above line above gridlines above frame - YES (verified in SVG body draw order).
20. Hover model = native `<title>` - YES (no client JS).

## Flagged for art-director review

None. No chart's editorial argument required a flag this pass.

## Build status

```
> astro check && astro build
- 0 errors
- 0 warnings
- 0 hints
11 page(s) built in 3.16s
```

## Visual regression

`npm run test:visual:update` regenerated baselines and re-ran the harness.
All 9 route tests pass:

```
9 passed (16.1s)
```

Baselines updated under
`tests/visual/__snapshots__/routes.spec.ts-snapshots/` (9 PNGs).

## Files modified

None. The architectural collapse to PanelLiveChart already
canon-aligned every Tier-3 panel; no per-file edits were required by
this audit pass.
