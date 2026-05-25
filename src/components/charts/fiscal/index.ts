/*
 * fiscal/index.ts — plate registry for the /fiscal/ section chartbook.
 *
 * Five plates in editorial order. Import this from the fiscal section page
 * (src/pages/fiscal.astro) to iterate plates. Chart component references
 * are listed here as documentation; the actual dispatch is through
 * SectionLayout.astro's chartRegistry keyed on chartKey.
 *
 * SectionLayout.astro chartKey additions required (backend-engineer):
 *   "fiscal-panel-1" -> Panel1FederalTrajectory
 *   "fiscal-panel-2" -> Panel2DebtServiceRatio
 *   "fiscal-panel-3" -> Panel3PBOvsDoF
 *   "fiscal-panel-4" -> Panel4ProvincialDebt
 *   "fiscal-panel-5" -> Panel5OperatingCapital
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
];
