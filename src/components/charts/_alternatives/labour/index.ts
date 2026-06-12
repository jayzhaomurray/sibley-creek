/*
 * _alternatives/labour/index.ts — chart-alternatives manifest for the
 * Labour section.
 *
 * Two flavours of entry live here:
 *
 *   1) Placeholder Alt*.astro components that pull from data/raw/ CSVs
 *      directly via _shared/altUtils.ts. They draw with no `data` prop.
 *
 *   2) Production components (under src/components/charts/labour/) kept
 *      on the alt page for review against their live counterpart. These
 *      take pipeline panel_data from data/site/panel_data/labour.json
 *      via the `data` field on the entry; the alt page passes that
 *      through as the `data` prop on render.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";
import labourPanelData from "../../../../../data/site/panel_data/labour.json";
import { pickPanel } from "../../_shared/panelData";

import Alt2_YouthVsPrime from "./Alt2_YouthVsPrime.astro";
import Alt3_WageGrowthYoY from "./Alt3_WageGrowthYoY.astro";
import Alt4_VacanciesVsEI from "./Alt4_VacanciesVsEI.astro";
import Alt5_URDecompIdentity from "./Alt5_URDecompIdentity.astro";
import Alt6_ShimerDecomp from "./Alt6_ShimerDecomp.astro";
import Alt7_PopulationDecomposition from "./Alt7_PopulationDecomposition.astro";
import Alt8_PopulationDemand from "./Alt8_PopulationDemand.astro";
import Alt_Panel2LabourSharesOfPop from "./Alt_Panel2LabourSharesOfPop.astro";
import Alt_Panel2LabourStocksYoY from "./Alt_Panel2LabourStocksYoY.astro";

import Panel1LFSHeadlineIndexed from "../../labour/Panel1LFSHeadlineIndexed.astro";

const labourPanel1Data = pickPanel(labourPanelData, 1);
const labourPanel2Data = pickPanel(labourPanelData, 2);

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt2_YouthVsPrime,
    file: "labour/Alt2_YouthVsPrime.astro",
    title: "Youth vs prime-age unemployment",
    whatDifferent:
      "Youth (15-24) primary line over prime-age (25-54) secondary dashed line. Gap is the cyclical-vs-structural decomposition.",
    whyBetter:
      "Youth unemployment leads cycle deterioration; the pair makes turning points legible six months earlier than the headline.",
    dataFields:
      "youth_unemployment_rate.csv + prime_age_unemployment_rate.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_WageGrowthYoY,
    file: "labour/Alt3_WageGrowthYoY.astro",
    title: "LFS vs SEPH wage growth Y/Y",
    whatDifferent:
      "Both series in Y/Y growth (not levels), with 3% trend reference. LFS leads, SEPH is the payroll truth.",
    whyBetter:
      "Wage Y/Y is what the BoC watches; production Panel 3 shows levels, which obscure the cycle.",
    dataFields: "lfs_wages_all.csv (Y/Y) + seph_earnings.csv (Y/Y)",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_VacanciesVsEI,
    file: "labour/Alt4_VacanciesVsEI.astro",
    title: "Vacancies vs EI claims, both indexed",
    whatDifferent:
      "Both indexed to Jan 2019 = 100 to share a unitless axis. Vacancies up + EI up = mismatch; vacancies down + EI up = recession.",
    whyBetter:
      "The two-sided cycle read (demand and dislocation) is invisible from either chart alone.",
    dataFields:
      "job_vacancy_rate.csv + ei_regular_beneficiaries.csv, both indexed",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt5_URDecompIdentity,
    file: "labour/Alt5_URDecompIdentity.astro",
    title:
      "ΔUR identity decomposition: numerator vs denominator",
    whatDifferent:
      "Stacked signed bars per month — ΔU contribution (heavier ink, numerator) plus ΔE contribution (lighter ink, denominator) — sum exactly to ΔUR. The actual ΔUR series overlays as a thin dashed line; latest month in MTA red.",
    whyBetter:
      "ΔUR = (ΔU·E − U·ΔE)/(LF·LF). The decomposition disciplines hot takes that confuse a denominator shift (population grew faster than jobs) with labour-market deterioration (jobs were lost). Most months one bar dominates — the chart names which.",
    dataFields:
      "unemployment_rate.csv + unemployment_level.csv (E and LF derived from LFS identity LF = U/(UR/100), E = LF − U)",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt6_ShimerDecomp,
    file: "labour/Alt6_ShimerDecomp.astro",
    title:
      "Cyclical UR moves: separation-driven or finding-rate-driven?",
    whatDifferent:
      "Two-panel Shimer-style decomposition: monthly separation rate (left, ~2% normal, spikes in 2020) and job-finding rate (right, ~30% normal, collapses in recessions). Both derived from stocks plus short-duration unemployment via Elsby-Michaels-Solon.",
    whyBetter:
      "The same UR move can come from rising separations (people losing jobs, leads recessions) or falling finding rates (matching market frozen, persists into early recoveries). Naming which channel is doing the work disciplines cycle-stage takes that the level chart can't support.",
    dataFields:
      "unemployment_level.csv + unemployment_rate.csv + unemployment_1_to_4_weeks.csv (E derived from LFS identity)",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt8_PopulationDemand,
    file: "labour/Alt8_PopulationDemand.astro",
    title: "Population level and Y/Y growth, two-panel composite",
    whatDifferent:
      "Two-panel chart: left = total Canadian population level (quarterly, since 2010); right = Y/Y growth rate computed in-component from the same level series. Built for the housing section's demand-fundamentals slot but moved to labour alts — population is a people story, not a housing story.",
    whyBetter:
      "Cleaner than the full decomposition: just shows the shape (surge to ~3% Y/Y in 2023-24, collapse to -0.25% Y/Y in 2026 Q1 — first negative print in over a decade) without the noise of stacked components. Editorial focus on direction rather than composition.",
    dataFields: "pop_total.csv (StatCan 17-10-0009-01, quarterly).",
    addedAt: "2026-05-13",
  },
  {
    Component: Alt7_PopulationDecomposition,
    file: "labour/Alt7_PopulationDecomposition.astro",
    title:
      "Quarterly population change decomposed: candidate replacement for the IRCC supply plate",
    whatDifferent:
      "Stacked composition of quarterly population change — natural increase, net PR, net NPR (in MTA red, the swing factor), and a residual that closes the identity to ΔPOP — with total population overlaid as a thin dashed line on a right-side axis. 60 quarters / 15 years.",
    whyBetter:
      "Production Panel 4 plots PR landings and net NPR vs plan; this names the entire denominator dynamic at once. The 2024–25 NPR pivot reads as the bucket that flipped sharply negative, and the dashed level line shows how the cumulative composition has rolled the pop_total over. User asked for it as a candidate replacement for the IRCC supply-trajectory plate.",
    dataFields:
      "pop_births + pop_deaths + pop_immigrants + pop_emigrants + pop_net_npr + pop_total (all quarterly, data/raw/).",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt_Panel2LabourSharesOfPop,
    file: "labour/Alt_Panel2LabourSharesOfPop.astro",
    title: "Stocks as shares of population 15+ (Alt A)",
    whatDifferent:
      "Three-panel composite. Each stock divided by population 15+ and expressed as a share. Three shares sum to 100% by construction. 120-month window. Employed share ≈ published employment rate (identity); unemployed share is share-of-population NOT the headline UR; NLF share is the inactivity rate.",
    whyBetter:
      "Strips out population growth so the compositional shift is legible. Live Plate 2 plots levels in millions, which slope up together with population — the editorial signal (which bucket is gaining faster) gets buried. Shares isolate it.",
    dataFields:
      "employment_level.csv + unemployment_level.csv + employment_rate.csv (pop_15+ derived chart-side via employment / employment_rate).",
    data: labourPanel2Data,
    addedAt: "2026-05-12",
  },
  {
    Component: Alt_Panel2LabourStocksYoY,
    file: "labour/Alt_Panel2LabourStocksYoY.astro",
    title: "Stocks as Y/Y growth rates (Alt B)",
    whatDifferent:
      "Three-panel composite. Each stock as Y/Y % change. 36-month window. Zero line drawn on each panel.",
    whyBetter:
      "Y/Y strips the level-trend; what remains is cyclical signal. NLF Y/Y consistently above employment Y/Y is the visible 'where movement is concentrated' story. Removes the population-growth dominator without forcing the reader to think in shares.",
    dataFields:
      "employment_level.csv + unemployment_level.csv + employment_rate.csv (pop_15+ + NLF derived chart-side; Y/Y via same-month-prior-year lookup).",
    data: labourPanel2Data,
    addedAt: "2026-05-12",
  },
  {
    Component: Panel1LFSHeadlineIndexed,
    file: "labour/Panel1LFSHeadlineIndexed.astro",
    title: "LFS headline indexed to pre-pandemic baseline",
    whatDifferent:
      "Forces all three rates (unemployment, employment, participation) onto a shared scale (Feb 2020 = 100) so the divergence between them is the geometry.",
    whyBetter:
      "User preference was per-panel y-axis tuning instead; this is the alternative kept for reference.",
    dataFields:
      "lfs_unemployment_rate.csv + lfs_employment_rate.csv + lfs_participation_rate.csv, all rebased to Feb 2020.",
    data: labourPanel1Data,
    addedAt: "2026-05-12",
  },
];
