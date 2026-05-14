"""IMF DataMapper series catalog.

These series enter as Canadian-macro context for the Policy section ALT
fiscal-stance chart (panel-7-alt). They are NOT wired to a live plate yet;
the panel uses expected_status="WIRED" so the data layer is ready when
editorial decides to promote.

Scope caveat (applies to all entries below):
    All IMF WEO fiscal indicators for Canada are GENERAL GOVERNMENT
    (consolidated federal + provincial + local + social-security funds),
    not federal-only. The Department of Finance Canada's Fiscal Reference
    Tables (PDF, annual) are the authoritative federal-only source but
    require PDF extraction. Use the IMF series for:
        - Long-history charts (1980+) where the general-govt scope is
          acceptable and editorially noted.
        - Comparisons against other countries (IMF uses consistent
          general-govt consolidation across all WEO members).
    Do NOT use IMF series in contexts that assert federal-only framing
    (e.g. comparing to the Fiscal Monitor which IS federal-only).

Series included:
    - GGXCNL_NGDP: General government net lending/borrowing, % of GDP.
      Negative = deficit (net borrowing). 1980-present; includes forward
      projections.
    - GGXWDG_NGDP: General government gross debt, % of GDP. 1980-present.
      NOTE: This is GROSS debt (financial liabilities), not NET debt
      (liabilities minus financial assets). The IMF does not publish
      Canada's general-government NET debt. For a "net debt" framing,
      this series overstates the headline metric; document clearly.

Re-verify cadence:
    IMF WEO is published in April and October each year. Pipeline build
    will pull the current-vintage values on each run; no manual re-verify
    needed unless the indicator ID or API base URL changes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImfSpec:
    name: str            # CSV filename slug
    indicator_id: str    # IMF DataMapper indicator ID
    country: str         # ISO3 country code
    units: str
    frequency: str       # always "annual" for WEO indicators
    section: str
    notes: str = ""


IMF_SERIES: dict[str, ImfSpec] = {

    # General government net lending/borrowing, % of GDP.
    # Negative values = deficit (net borrowing). Positive = surplus.
    # WEO historical series 1980-present + IMF forward projections.
    # Used for: Policy panel-7-alt fiscal-stance chart (primary slot).
    #
    # Scope caveat: GENERAL GOVERNMENT, not federal-only. IMF WEO April 2024
    # vintage covers actuals through 2023; 2024 and beyond are projections.
    # The pipeline cannot programmatically distinguish actuals from projections;
    # as a convention, treat the last two years as projections unless
    # DoF Public Accounts has been released for those years.
    "imf_can_gg_balance_pct_gdp": ImfSpec(
        name="imf_can_gg_balance_pct_gdp",
        indicator_id="GGXCNL_NGDP",
        country="CAN",
        units="% of GDP (general government net lending/borrowing)",
        frequency="annual",
        section="policy",
        notes=(
            "IMF WEO -- Canada general government net lending/borrowing as % of nominal "
            "GDP. SCOPE: general government (federal + provincial + local + social "
            "security), NOT federal-only. Negative = deficit. Source: IMF DataMapper "
            "API, indicator GGXCNL_NGDP, country CAN. "
            "WEO published April and October; current-vintage fetched at each pipeline "
            "run. Includes IMF forward projections beyond the last Statistics Canada "
            "public-accounts actuals; treat data from current calendar year onward as "
            "projections. For federal-only framing, DoF Fiscal Reference Tables (PDF) "
            "are the authoritative source."
        ),
    ),

    # General government gross debt, % of GDP.
    # NOTE: This is GROSS financial liabilities, not net debt (assets subtracted).
    # The IMF does not publish Canada's general-government net debt in the
    # DataMapper API (GGXWNG_NGDP returns null for CAN as of May 2026 probe).
    # Used for: Policy panel-7-alt fiscal-stance chart (secondary slot).
    #
    # At ~80-110% of GDP, this series is materially higher than the federal-only
    # net debt (typically ~30-40% of GDP). The difference reflects:
    #   1. Province + municipality + social-security fund debt included
    #   2. Gross vs net distinction (financial assets not netted out)
    # Document both gaps in any chart caption.
    "imf_can_gg_gross_debt_pct_gdp": ImfSpec(
        name="imf_can_gg_gross_debt_pct_gdp",
        indicator_id="GGXWDG_NGDP",
        country="CAN",
        units="% of GDP (general government gross debt)",
        frequency="annual",
        section="policy",
        notes=(
            "IMF WEO -- Canada general government gross debt as % of nominal GDP. "
            "SCOPE: general government (all levels), GROSS (not net). IMF GGXWNG_NGDP "
            "(net debt) returns null for Canada; gross is the only available WEO "
            "debt-level series for CAN. Range: ~45% (1980) to ~118% (2020 COVID peak) "
            "to ~110% (2024). These levels are not comparable to federal-only "
            "net debt metrics (DoF FRT ~30-40% of GDP). Source: IMF DataMapper API, "
            "indicator GGXWDG_NGDP, country CAN. WEO published April/October; "
            "includes forward projections from current year onward."
        ),
    ),
}
