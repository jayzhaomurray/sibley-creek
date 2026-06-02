/*
 * fiscal/index.ts — plate registry for the /fiscal/ section chartbook.
 *
 * Original five plates (existing panels) + five new plates (Plate1–5 as specified in
 * claude-ref/proposals/fiscal_redo_chart_spec.md). New plates read from panel-6 through
 * panel-10 of fiscal.json.
 *
 * SectionLayout.astro chartKey additions required (frontend-designer):
 *   Existing: "fiscal-panel-1" through "fiscal-panel-5" (original panels)
 *   New plates:
 *   "fiscal-plate-1-alt" -> Plate1BalanceTwoPanel       (panel-6, two-panel: full history + forecast zoom) [WINNER, the canonical Plate 1]
 *   "fiscal-plate-2"     -> Plate2RevenuesPctGDP        (panel-7+8, merged two-series rev vs exp) [WINNER]
 *   "fiscal-plate-4"     -> Plate4FederalDebtPctGDP     (panel-9, debt % GDP)
 *   "fiscal-plate-5"     -> Plate5IssuanceByInstrument  (panel-10, gross issuance flow stacked bars)
 *
 *   CUT 2026-06-02: "fiscal-plate-3" -> Plate3ProgramExpPctGDP (panel-8) — redundant with the
 *     merged Plate 2 (which carries the expense line). Component file retained per "tag and
 *     leave"; unwired from fiscal.astro + the SectionLayout registry.
 *
 *   PRUNED 2026-06-02 (Jay picked the winners; losing alternates unwired, files kept):
 *     "fiscal-plate-1"     -> Plate1BalanceComposition (original single-panel balance)
 *     "fiscal-plate-2-alt" -> Plate2RevExpTwoPanel     (two-panel rev/exp ALT)
 *
 * Panel data file: data/site/panel_data/fiscal.json
 * Section accent token: var(--section-accent-fiscal); fallback: var(--accent)
 */

export interface FiscalPlateEntry {
  /** Plate number, 1-indexed. */
  num: number;
  /** Zero-padded plate number string for display. */
  number: string;
  /** ChartKey for SectionLayout dispatch. */
  chartKey: string;
  /** Component file path (documentation only; not imported here). */
  componentPath: string;
  /** Indicator label — appears in plate-index nav chips. */
  indicator: string;
  /** Short label for the plate-index nav. */
  plateIndexLabel: string;
  /** Title placeholder — writer refines before ship. */
  titlePlaceholder: string;
  /** Data key(s) expected in fiscal.json for this plate. */
  dataKeys: string[];
  /** Pipeline wiring status. */
  status: "WIRED" | "NEAR" | "MISSING" | "PLACEHOLDER";
  /** Source card reference. */
  sourceCard: string;
}

export const fiscalPlates: FiscalPlateEntry[] = [
  {
    num: 1,
    number: "01",
    chartKey: "fiscal-panel-1",
    componentPath: "src/components/charts/fiscal/Panel1FederalTrajectory.astro",
    indicator: "Federal monthly + YTD balance",
    plateIndexLabel: "Federal trajectory",
    titlePlaceholder:
      "Fiscal is tracking the same cadence as recent years, not leaning against the cycle.",
    dataKeys: ["dof_fiscal_monthly_balance", "dof_fiscal_ytd_balance"],
    status: "WIRED",
    sourceCard: "pipeline:dof:dof_fiscal_ytd_balance + pipeline:dof:dof_fiscal_monthly_balance",
  },
  {
    num: 2,
    number: "02",
    chartKey: "fiscal-panel-2",
    componentPath: "src/components/charts/fiscal/Panel2DebtServiceRatio.astro",
    indicator: "Public debt charges / revenues, monthly ratio with 5-year band",
    plateIndexLabel: "Debt service",
    titlePlaceholder:
      "Debt service is now consuming [X]c of every dollar of federal revenue.",
    dataKeys: ["debt_service_ratio", "debt_service_ratio_band_lo", "debt_service_ratio_band_hi"],
    status: "NEAR",
    sourceCard: "editorial/source_cards/_pending/fiscal/plate-2.yaml (Tier A)",
  },
  {
    num: 3,
    number: "03",
    chartKey: "fiscal-panel-3",
    componentPath: "src/components/charts/fiscal/Panel3PBOvsDoF.astro",
    indicator: "PBO EFO Sept 2025 vs DoF SEU April 2026 deficit projection tracks",
    plateIndexLabel: "PBO vs DoF",
    titlePlaceholder:
      "PBO sees [X]bn more deficit by FY[YY] than DoF.",
    dataKeys: ["dof_seu_deficit_projection", "pbo_efo_deficit_projection"],
    status: "MISSING",
    sourceCard: "editorial/source_cards/_pending/fiscal/plate-3.yaml (Tier B, pending_user)",
  },
  {
    num: 4,
    number: "04",
    chartKey: "fiscal-panel-4",
    componentPath: "src/components/charts/fiscal/Panel4ProvincialDebt.astro",
    indicator: "Net debt-to-GDP: ON / QC / AB / BC most-recent budgets",
    plateIndexLabel: "Provincial debt",
    titlePlaceholder:
      "Net debt-to-GDP: provinces span [X] to [Y]%.",
    dataKeys: ["provincial_net_debt_to_gdp"],
    status: "MISSING",
    sourceCard: "editorial/source_cards/_pending/fiscal/plate-4.yaml (Tier B, pending_user)",
  },
  {
    num: 5,
    number: "05",
    chartKey: "fiscal-panel-5",
    componentPath: "src/components/charts/fiscal/Panel5OperatingCapital.astro",
    indicator: "Operating vs capital balance: DoF SEU Apr 2026 vs PBO Nov 2025 reclassification",
    plateIndexLabel: "Operating/capital",
    titlePlaceholder:
      "PBO reclassifies $[X]bn of DoF's 'capital' as operating.",
    dataKeys: ["dof_operating_balance", "pbo_operating_balance"],
    // PLACEHOLDER: real data requires researcher extraction from DoF SEU Apr 2026
    // fiscal tables and PBO Nov 17 2025 analysis (~$94B reclassification).
    // Component renders PanelEmpty until pipeline emits operating/capital split.
    status: "PLACEHOLDER",
    sourceCard:
      "Pending researcher extraction. See: " +
      "https://thehub.ca/2025/11/17/carneys-budget-has-a-94-billion-gap-in-investment-spending-and-a-shortfall-in-government-operating-balance-pbo/ " +
      "and DoF SEU April 2026 Annex 1.",
  },
  // ---- NEW PLATES (fiscal_redo_chart_spec.md) --------------------------------
  // These five plates implement the A.8 forecast convention canon:
  // history = solid ink, forecast = dotted ink (lines) or hatched+outlined (bars),
  // vertical break rule + FORECAST stamp at handoff, MTA red dot at junction.
  // ---- fiscal-plate-1 (Plate1BalanceComposition) UNWIRED 2026-06-02 ----------
  // The original single-panel signed-bar balance chart. Jay picked the two-panel
  // Plate1BalanceTwoPanel (now the canonical Plate 1, chartKey fiscal-plate-1-alt).
  // Component file retained per "tag and leave"; unwired from fiscal.astro + the
  // SectionLayout registry.
  {
    num: 7,
    number: "07",
    chartKey: "fiscal-plate-2",
    componentPath: "src/components/charts/fiscal/Plate2RevenuesPctGDP.astro",
    // R2.5: MERGED two-line chart: revenues vs expenses on one honest axis.
    // fiscal.astro wires: data.primary = frt_revenues_pct_gdp, data.secondary = frt_program_exp_pct_gdp.
    indicator: "Federal revenues vs program expenses, % of GDP (merged two-line, FY1983-84 + SEU 2026)",
    plateIndexLabel: "Revenue vs Expense",
    titlePlaceholder: "[TITLE TK]",
    dataKeys: ["frt_revenues_pct_gdp", "frt_program_exp_pct_gdp"],
    status: "WIRED",
    sourceCard: "fiscal.json panel-7 (revenues) + panel-8 (expenses); combined by fiscal.astro",
  },
  // ---- fiscal-plate-3 CUT 2026-06-02 ----------------------------------------
  // Plate3ProgramExpPctGDP (panel-8 standalone expenses) was redundant with the
  // merged Plate 2, which already carries the expense line. Unwired from
  // fiscal.astro + the SectionLayout registry. The component file is retained
  // per the "tag and leave" convention and may be re-promoted if needed.
  //
  // ---- ALTERNATE PLATES (comparison set; "alternate lives alongside") -------
  {
    num: 7.5,
    number: "07a",
    chartKey: "fiscal-plate-1-alt",
    componentPath: "src/components/charts/fiscal/Plate1BalanceTwoPanel.astro",
    // ALT to Plate 1: two-panel small-multiples (Mode B, per-panel y-axes).
    // Panel A = full FY1983-84 history total bars; Panel B = forecast-window zoom
    // (FY2024-25 -> FY2030-31) with operating (solid) / capital (cross-hatch) split.
    indicator: "Budget balance — full history + forecast operating/capital zoom (ALT, two-panel)",
    plateIndexLabel: "Balance (alt)",
    titlePlaceholder: "[TITLE TK]",
    dataKeys: ["frt_federal_balance_total", "frt_federal_balance_opex", "frt_federal_balance_capex"],
    status: "WIRED",
    sourceCard: "fiscal.json panel-6 (pipeline:dof:frt_federal_balance_total + frt_federal_balance_opex + frt_federal_balance_capex)",
  },
  // ---- fiscal-plate-2-alt (Plate2RevExpTwoPanel) UNWIRED 2026-06-02 ----------
  // The two-panel small-multiples rev/exp ALT. Jay picked the merged two-series
  // overlay (Plate2RevenuesPctGDP, chartKey fiscal-plate-2). Component file
  // retained per "tag and leave"; unwired from fiscal.astro + the registry.
  {
    num: 9,
    number: "09",
    chartKey: "fiscal-plate-4",
    componentPath: "src/components/charts/fiscal/Plate4FederalDebtPctGDP.astro",
    indicator: "Federal debt, % of GDP (FY2006-07 history + SEU 2026 forecast)",
    plateIndexLabel: "Debt/GDP",
    titlePlaceholder: "[TITLE TK]",
    dataKeys: ["frt_federal_debt_pct_gdp"],
    // Overlap note: Panel6DebtToGDP covers similar territory from 1980.
    // This plate covers FY2006-07 onward and is A.8-conformant.
    // Editorial-director to resolve whether this supersedes Panel6DebtToGDP.
    status: "WIRED",
    sourceCard: "fiscal.json panel-9 (pipeline:dof:frt_federal_debt_pct_gdp)",
  },
  {
    num: 10,
    number: "10",
    chartKey: "fiscal-plate-5",
    componentPath: "src/components/charts/fiscal/Plate5IssuanceByInstrument.astro",
    indicator: "Gross issuance flow by maturity bucket: bills + notes + bonds ($B, stacked)",
    plateIndexLabel: "Issuance mix",
    titlePlaceholder: "[TITLE TK]",
    dataKeys: ["frt_issuance_flow_bills", "frt_issuance_flow_notes", "frt_issuance_flow_bonds"],
    // FY2025-26 and FY2026-27 are forecast (is_forecast: 1); FY2019-20 to FY2024-25 are history.
    // All three buckets carry forecast points, so the full stacked total projects honestly.
    status: "WIRED",
    sourceCard: "fiscal.json panel-10 (pipeline:dof:frt_issuance_flow_bills + frt_issuance_flow_notes + frt_issuance_flow_bonds)",
  },
];
