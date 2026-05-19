"""StatCan WDS series catalog.

Each entry maps an output `name` (filename slug under `data/raw/`) to a
StatcanSpec carrying the vector ID, the human table URL (for .meta.json),
units, frequency, section assignment, and any quirks/notes.

Sections: gdp | inflation | inflation_basket | labour | housing | financial | trade | policy
Cadence:  daily | weekly | monthly | quarterly | annual | basket_cycle
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StatcanSpec:
    name: str                     # CSV filename slug
    vector_id: int                # WDS V-prefix integer
    table_id: str                 # human-facing StatCan table ID, e.g. "18-10-0004-01"
    units: str
    frequency: str                # "monthly", "quarterly", "annual"
    section: str
    notes: str = ""
    scale: float = 1.0            # multiplicative scale factor applied at write time
    sa: Optional[bool] = None     # True = SA, False = NSA, None = N/A or per-series footnote


# Canonical StatCan table URL builder (mirror of statcan.table_url)
def _table_url(table_id: str) -> str:
    return f"https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={table_id.replace('-', '')[:10]}"


# ---------------------------------------------------------------------------
# Series registrations
# ---------------------------------------------------------------------------

STATCAN_SERIES: dict[str, StatcanSpec] = {

    # ----- GDP (Section 4.1) ----------------------------------------------
    "gdp_monthly": StatcanSpec(
        name="gdp_monthly",
        vector_id=65201210, table_id="36-10-0434-01",
        units="C$ trillions, chained 2017", frequency="monthly", section="gdp",
        scale=1e-6, sa=True,
        notes="Monthly real GDP, all industries, chained 2017$, SAAR. Source publishes in C$ millions; scaled 1e-6 to C$ trillions.",
    ),
    "gdp_quarterly": StatcanSpec(
        name="gdp_quarterly",
        vector_id=62305752, table_id="36-10-0104-01",
        units="C$ millions, chained 2017", frequency="quarterly", section="gdp",
        sa=True,
        notes="Quarterly real GDP, expenditure-based, chained 2017$, SAAR.",
    ),
    # GDP contributions to quarterly Q/Q-AR growth, 6-bar decomposition.
    "gdp_contrib_total":       StatcanSpec("gdp_contrib_total", 79448580, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True,
                                           notes="Total contribution to annualized Q/Q growth (headline AR comparator)."),
    "gdp_contrib_consumption": StatcanSpec("gdp_contrib_consumption", 79448555, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True),
    "gdp_contrib_govt":        StatcanSpec("gdp_contrib_govt", 79448562, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True),
    "gdp_contrib_investment":  StatcanSpec("gdp_contrib_investment", 79448563, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True,
                                           notes="Gross fixed capital formation. Business-vs-residential split deferred to Pillar D deep-dive."),
    "gdp_contrib_inventories": StatcanSpec("gdp_contrib_inventories", 79448572, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True),
    "gdp_contrib_exports":     StatcanSpec("gdp_contrib_exports", 79448573, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True),
    "gdp_contrib_imports":     StatcanSpec("gdp_contrib_imports", 79448576, "36-10-0104-01", "pp", "quarterly", "gdp", sa=True,
                                           scale=-1.0, notes="Stored as 'less imports' (negated) so positive contribution = imports fell."),
    # Labour productivity (Table 36-10-0206-01). Quarterly SA index. Resolved
    # 2026-05-11 via WDS getCubeMetadata + getSeriesInfoFromCubePidCoord on
    # productId=36100206, coordinate 1.1.1.0.0.0.0.0.0.0. Series title:
    # "Canada;Business sector;Labour productivity". Most-cited variant per BoC
    # commentary (e.g. Macklem Nov 2022 productivity speech) is business-sector
    # productivity (output per hour). Companion to ULC (Table 36-10-0206 has
    # both; ULC vector is 1409159 already wired in boc-tracker if needed later).
    # The Y/Y derivation lands in data/processed/productivity_business_per_hour_yoy.csv
    # via derive_productivity_views() in pipeline/build.py.
    "productivity_business_per_hour": StatcanSpec(
        name="productivity_business_per_hour",
        vector_id=1409153, table_id="36-10-0206-01",
        units="Index, 2017=100 (SA)", frequency="quarterly", section="gdp",
        sa=True,
        notes=(
            "Canada;Business sector;Labour productivity (real GDP per hour worked), "
            "quarterly SA index. Cube coord 1.1.1.0.0.0.0.0.0.0. Resolved 2026-05-11. "
            "Feeds GDP Panel 6 (productivity overlay) and the GDP topic-page panel "
            "data bundle."
        ),
    ),

    # Per-capita denominator: total population, Table 17-10-0009-01 v1.
    "pop_total": StatcanSpec(
        name="pop_total",
        vector_id=1, table_id="17-10-0009-01",
        units="Persons", frequency="quarterly", section="gdp",
        sa=False,
        notes=(
            "Canada total population, quarterly. Reconciliation target: Q1 2026 ~41.5M. "
            "Boc-tracker previously excluded this vector pending verification; verified by "
            "magnitude reconciliation against StatCan Daily 2026 release."
        ),
    ),

    # Natural-increase components: births and deaths, Canada-total quarterly.
    # Resolved 2026-05-12 via WDS getSeriesInfoFromCubePidCoord on Table
    # 17-10-0059-01 ("Estimates of the components of natural increase, quarterly").
    # IMPORTANT cube clarification: the previously-wired pop_immigrants /
    # pop_emigrants / pop_net_npr / pop_npr_inflows / pop_net_emigration set
    # comes from Table 17-10-0040-01 (Components of population GROWTH, the
    # migration-only cube), which does NOT publish births or deaths. Births
    # and deaths live in the sibling Table 17-10-0059-01 (natural-increase
    # cube). The slugs are still pop_births / pop_deaths so they sort
    # alongside the other pop_* migration components for Labour Panel 5 IRCC
    # / supply-trajectory consumption, but provenance is the separate cube.
    "pop_births": StatcanSpec(
        name="pop_births",
        vector_id=62, table_id="17-10-0059-01",
        units="Persons", frequency="quarterly", section="labour",
        sa=False,
        notes=(
            "Births, Canada total, quarterly. Cube coord 1.1.0.0.0.0.0.0.0.0; "
            "series title 'Canada;Births'. Table 17-10-0059-01 publishes natural-"
            "increase components separately from the migration components in "
            "Table 17-10-0040 (which is where pop_immigrants / pop_net_npr etc. "
            "live). Resolved 2026-05-12."
        ),
    ),
    "pop_deaths": StatcanSpec(
        name="pop_deaths",
        vector_id=77, table_id="17-10-0059-01",
        units="Persons", frequency="quarterly", section="labour",
        sa=False,
        notes=(
            "Deaths, Canada total, quarterly. Cube coord 1.2.0.0.0.0.0.0.0.0; "
            "series title 'Canada;Deaths'. Companion to pop_births in Table "
            "17-10-0059-01 (natural-increase cube). Resolved 2026-05-12."
        ),
    ),

    # ----- Inflation (Section 4.2) ----------------------------------------
    "cpi_all_items":     StatcanSpec("cpi_all_items", 41690914, "18-10-0006-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=True),
    "cpi_all_items_nsa": StatcanSpec("cpi_all_items_nsa", 41690973, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    # BoC's preferred core measures, published in StatCan Table 18-10-0256-01
    # at the 8:30 ET CPI release (same time as headline). Moved here from
    # BoC Valet 2026-05-19 because Valet refreshes these later on CPI
    # Tuesdays (often afternoon ET), which blocks the inflation page from
    # showing the day's print.
    # Vector-to-series mapping confirmed against BoC Valet's March 2026
    # values AND the user's April 2026 commentary: trim 2.0/2.2/2.3
    # (Apr/Mar/Feb), median 2.1/2.3/2.4, common 2.5/2.6/2.4.
    "cpi_trim":          StatcanSpec("cpi_trim", 108785715, "18-10-0256-01",
                                     "% Y/Y", "monthly", "inflation", sa=False),
    "cpi_median":        StatcanSpec("cpi_median", 108785714, "18-10-0256-01",
                                     "% Y/Y", "monthly", "inflation", sa=False),
    "cpi_common":        StatcanSpec("cpi_common", 108785713, "18-10-0256-01",
                                     "% Y/Y", "monthly", "inflation", sa=False),
    "cpi_food":          StatcanSpec("cpi_food", 41690974, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    "cpi_shelter":       StatcanSpec("cpi_shelter", 41691050, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    "cpi_services":      StatcanSpec("cpi_services", 41691230, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    "cpi_goods":         StatcanSpec("cpi_goods", 41691222, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    "cpi_energy":        StatcanSpec("cpi_energy", 41691239, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
    # Shelter sub-components, canon 4.2 element 4 (mortgage interest decomposed out).
    # Verified 2026-05-10 via WDS getDataFromVectorsAndLatestNPeriods on each ID; refer to Table 18-10-0004-01.
    "cpi_rented_accommodation": StatcanSpec("cpi_rented_accommodation", 41691073, "18-10-0004-01",
                                            "Index, 2002=100", "monthly", "inflation", sa=False,
                                            notes="Rented accommodation CPI; cross-references housing rent direction read."),
    "cpi_rent":                 StatcanSpec("cpi_rent", 41691074, "18-10-0004-01",
                                            "Index, 2002=100", "monthly", "inflation", sa=False,
                                            notes="Rent CPI sub-series."),
    "cpi_owned_accommodation":  StatcanSpec("cpi_owned_accommodation", 41691083, "18-10-0004-01",
                                            "Index, 2002=100", "monthly", "inflation", sa=False),
    "cpi_mortgage_interest":    StatcanSpec("cpi_mortgage_interest", 41691093, "18-10-0004-01",
                                            "Index, 2002=100", "monthly", "inflation", sa=False,
                                            notes="Mortgage interest cost component; central to shelter decomposition."),
    # ----- Phase 2: CPI all-items excluding indirect taxes ----------------
    # Wave 5 brief (Section 5 backend item 5, methodology resolution C.4):
    # Inflation Panel 1 gains a toggle for "CPI excluding indirect taxes" to
    # separate GST/HST and tariff pass-through from the underlying price-level
    # signal. Researcher to confirm canonical StatCan vector before Phase 2
    # build wires it.
    #
    # CANDIDATE: v41691000-series in Table 18-10-0004-01. The Wave 5 doc
    # (Section C.4) cites v41693242 as "the likely candidate" but that vector
    # is the BoC's CPIX series (CPI ex 8 most volatile + indirect taxes,
    # ATOM_V41693242 in boc_series.py), NOT the simpler "all-items ex indirect
    # taxes" the chart toggle calls for. The StatCan-published "CPI all-items
    # excluding the effect of indirect taxes" lives in 18-10-0004 under a
    # different vector ID; identification deferred to researcher (Wave 5
    # researcher follow-up #2).
    #
    # ENTRY IS COMMENTED OUT so the catalog runner does not attempt to fetch
    # a placeholder vector ID. When the researcher confirms the vector, swap
    # the comment for a live StatcanSpec block and remove the TODO.
    #
    # TODO(phase2): Researcher confirms canonical vector for "CPI all-items
    # excluding indirect taxes" in StatCan Table 18-10-0004. When known:
    #   "cpi_all_items_ex_indirect_taxes": StatcanSpec(
    #       "cpi_all_items_ex_indirect_taxes",
    #       vector_id=<TBD>, table_id="18-10-0004-01",
    #       units="Index, 2002=100", frequency="monthly", section="inflation",
    #       sa=False,
    #       notes=(
    #           "StatCan-published CPI excluding effect of changes in indirect "
    #           "taxes. Inflation Panel 1 toggle (Wave 5 fold). Distinct from "
    #           "BoC's CPIX (cpi_ex_indirect_taxes; ATOM_V41693242) which also "
    #           "excludes the 8 most volatile components."
    #       ),
    #   ),

    # ----- CPI basket weights (Table 18-10-0007-01, basket-cycle cadence) ----
    # Per W3-R2 (researcher GO decision, 2026-05-11): inflation pass-through panel
    # (canon 4.2 element 6) needs major-aggregate basket weights from Table
    # 18-10-0007-01. Basket cycles: 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024;
    # the 2024 weights apply through the next refresh (~2029). All weights are
    # "Weight at basket link month prices; Distribution to selected geographies"
    # for Canada (Dim4=1, the convention StatCan uses when documenting the basket
    # composition; Dim4=2 returns NULL for non-headline aggregates). UOM 239 (Rate
    # %, decimals 2). Resolved 2026-05-11 via getSeriesInfoFromCubePidCoord.
    #
    # Frequency tag = "annual" so existing build infra treats this as a slow
    # series; cadence is actually "publish on basket refresh" (~every 5 years
    # historically; StatCan moved to ~annual updates in 2022 per the 2023 basket
    # update memo). The catalog field stays "annual" until we have a strong
    # need to distinguish basket_cycle from annual elsewhere.
    "cpi_basket_weight_all_items":              StatcanSpec(
        "cpi_basket_weight_all_items", 91858736, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;All-items basket weight. Always 100.00 (denominator). Coord 1.1.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_food":                   StatcanSpec(
        "cpi_basket_weight_food", 91858740, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;Food basket weight. Coord 1.2.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_shelter":                StatcanSpec(
        "cpi_basket_weight_shelter", 91858892, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;Shelter basket weight. Coord 1.78.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_energy":                 StatcanSpec(
        "cpi_basket_weight_energy", 91859272, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;Energy basket weight. Coord 1.268.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_goods":                  StatcanSpec(
        "cpi_basket_weight_goods", 91859278, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;Goods basket weight (total goods including food-purchased-from-stores). Coord 1.271.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_services":               StatcanSpec(
        "cpi_basket_weight_services", 91873252, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;Services basket weight (total services including shelter services). Coord 1.279.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_goods_ex_food_energy":   StatcanSpec(
        "cpi_basket_weight_goods_ex_food_energy", 91859292, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes=(
            "Canada;Goods excluding food purchased from stores and energy. Coord "
            "1.278.1.1.0.0.0.0.0.0. The closest StatCan-published aggregate to the editorial "
            "'goods ex-energy' concept needed for the pass-through panel (canon 4.2 element 6). "
            "Resolved 2026-05-11."
        ),
    ),
    "cpi_basket_weight_all_items_ex_food_energy": StatcanSpec(
        "cpi_basket_weight_all_items_ex_food_energy", 91859248, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;All-items excluding food and energy (core CPI scope). Coord 1.256.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "cpi_basket_weight_all_items_ex_shelter":   StatcanSpec(
        "cpi_basket_weight_all_items_ex_shelter", 91859258, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes="Canada;All-items excluding shelter. Coord 1.261.1.1.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    # Services excluding shelter services: registered for parallelism with the
    # canon 4.2 element 6 right-hand-side (services-ex-shelter CPI Y/Y), but the
    # WDS series returns NULL values at this aggregation (StatCan does not
    # publish a basket-weight share for this slice). Chart layer should derive
    # it as cpi_basket_weight_services minus cpi_basket_weight_shelter.
    "cpi_basket_weight_services_ex_shelter":    StatcanSpec(
        "cpi_basket_weight_services_ex_shelter", 91859296, "18-10-0007-01",
        "Weight share, % (basket link month prices)", "annual", "inflation_basket", sa=False,
        notes=(
            "Canada;Services excluding shelter services. Coord 1.280.1.1.0.0.0.0.0.0. "
            "Probe 2026-05-11: WDS=SUCCESS but values are NULL (StatCan does not publish "
            "a weight share for this aggregation at the published cube slice). "
            "Charts should derive as services - shelter. Series registered for completeness "
            "and to trigger a build-time warning if StatCan starts publishing this aggregate."
        ),
    ),

    # ----- Labour (Section 4.3) -------------------------------------------
    # Population 15 years and over, seasonally adjusted (Table 14-10-0287-01).
    # Resolved 2026-05-13 via WDS getDataFromVectorsAndLatestNPeriods:
    # productId=14100287, coordinate 1.1.1.1.1.1.0.0.0.0 (Canada; Population
    # estimate; Total - Gender; 15 years and over; Estimate; Seasonally adjusted).
    # Identity check: employment_level (v2062811, April 2026: 21033.7k) /
    # pop_15plus (v2062809, April 2026: 34755.6k) * 100 = 60.5% = employment_rate
    # (v2062817, April 2026: 60.5%). scalarFactorCode=3 (thousands); scale=0.001
    # converts to millions for unit-consistency with employment_level +
    # unemployment_level. Denominator for Panel2LabourStocksPerCapita per-capita
    # deflation -- replaces the back-derived employment/employment_rate identity.
    "pop_15plus": StatcanSpec(
        name="pop_15plus",
        vector_id=2062809, table_id="14-10-0287-01",
        units="Millions", frequency="monthly", section="labour",
        scale=0.001, sa=True,
        notes=(
            "Population 15 years and over, Canada total, seasonally adjusted. "
            "Coordinate 1.1.1.1.1.1.0.0.0.0. Source publishes in thousands "
            "(scalarFactorCode=3); scaled 0.001 -> millions for unit-consistency "
            "with employment_level and unemployment_level. April 2026: 34.756M. "
            "Verified 2026-05-13 via employment identity check."
        ),
    ),
    "unemployment_rate":      StatcanSpec("unemployment_rate", 2062815, "14-10-0287-01",
                                          "%", "monthly", "labour", sa=True),
    "employment_rate":        StatcanSpec("employment_rate", 2062817, "14-10-0287-01",
                                          "%", "monthly", "labour", sa=True),
    "participation_rate":     StatcanSpec("participation_rate", 2062816, "14-10-0287-01",
                                          "%", "monthly", "labour", sa=True),
    "unemployment_level":     StatcanSpec("unemployment_level", 2062814, "14-10-0287-01",
                                          "Millions", "monthly", "labour", scale=0.001, sa=True,
                                          notes="Unemployed persons, scaled thousands -> millions."),
    "employment_level":       StatcanSpec("employment_level", 2062811, "14-10-0287-01",
                                          "Millions", "monthly", "labour", scale=0.001, sa=True,
                                          notes=(
                                              "Employed persons, Canada 15+, SA monthly. Scaled thousands -> millions. "
                                              "Numerator for per-capita employment growth (Pillar E). Also the headcount "
                                              "comparator in the hours-vs-headcount Labour plate (panel-2c): the Y/Y of "
                                              "employment_level vs Y/Y of aggregate_hours isolates the per-worker-hours "
                                              "channel -- when hours Y/Y slows below employment Y/Y, employers are cutting "
                                              "shifts before they cut bodies (leading-softening signal)."
                                          )),
    # Wages
    "lfs_wages_all":          StatcanSpec("lfs_wages_all", 105812645, "14-10-0320-02",
                                          "C$/hour", "monthly", "labour", sa=True),
    "lfs_wages_permanent":    StatcanSpec("lfs_wages_permanent", 105812715, "14-10-0320-02",
                                          "C$/hour", "monthly", "labour", sa=True),
    "seph_earnings":          StatcanSpec("seph_earnings", 79311153, "14-10-0223-01",
                                          "C$/week", "monthly", "labour", sa=True),
    # Vacancies
    "job_vacancy_rate":       StatcanSpec("job_vacancy_rate", 1212389365, "14-10-0371-01",
                                          "%", "monthly", "labour", sa=False,
                                          notes="JVWS publishes NSA only; chart-side 3mma is the editorial convention."),
    "job_vacancy_level":      StatcanSpec("job_vacancy_level", 1212389364, "14-10-0371-01",
                                          "Millions", "monthly", "labour", scale=1e-6, sa=False),
    # Aggregate hours (Table 14-10-0289). Resolved 2026-05-11 (research/wave2_vector_resolutions.md):
    # Canada; Total actual hours worked, all industries; Estimate (coord 1.1.1.0.0.0.0.0.0.0).
    "aggregate_hours":        StatcanSpec("aggregate_hours", 4391505, "14-10-0289-01",
                                          "Thousands of hours", "monthly", "labour", sa=True,
                                          notes=(
                                              "Canada; total actual hours worked, all industries; Estimate; SA monthly. "
                                              "Cube coord 1.1.1.0.0.0.0.0.0.0; UOM 152 (thousands of hours), decimals 1. "
                                              "Resolved 2026-05-11 via getCubeMetadata on 14-10-0289. "
                                              "METHODOLOGY: this is the labour-input measure proper -- counts every hour "
                                              "worked across the economy in a reference week, scaled to monthly. The SA "
                                              "'all industries' headline is published on a main-job basis (multi-job-holders' "
                                              "second-job hours are not included in the published SA aggregate); there is no "
                                              "SA all-jobs companion cube. Editorial use: Y/Y growth in hours vs Y/Y growth "
                                              "in employment_level (the headcount measure) isolates the per-worker-hours "
                                              "channel. Powers the hours-vs-headcount Labour plate (panel-2c)."
                                          )),
    # Provincial LFS unemployment rates (Table 14-10-0287). Resolved 2026-05-11 via WDS
    # getCubeMetadata + getSeriesInfoFromCubePidCoord. Coordinate template: {GEO}.7.1.1.1.1.0.0.0.0
    # = Geo; Unemployment rate; Total - Gender; 15+; Estimate; Seasonally adjusted. UOM 239 (Rate %).
    # NOTE: Canada-level unemployment_rate (v2062815) is already wired above under name
    # "unemployment_rate"; we mirror it here as "lfs_ca_unemployment_rate" so chart panels that
    # iterate {CA,QC,ON,AB,BC} get a uniform slug set.
    "lfs_ca_unemployment_rate":    StatcanSpec("lfs_ca_unemployment_rate", 2062815, "14-10-0287-01",
                                               "%", "monthly", "labour", sa=True,
                                               notes=(
                                                   "Canada; Unemployment rate; Total - Gender; 15+; Estimate; SA. "
                                                   "Cube coord 1.7.1.1.1.1.0.0.0.0. Companion slug for provincial set."
                                               )),
    "lfs_qc_unemployment_rate":    StatcanSpec("lfs_qc_unemployment_rate", 2063760, "14-10-0287-01",
                                               "%", "monthly", "labour", sa=True,
                                               notes=(
                                                   "Quebec; Unemployment rate; Total - Gender; 15+; Estimate; SA. "
                                                   "Cube coord 6.7.1.1.1.1.0.0.0.0. Resolved 2026-05-11."
                                               )),
    "lfs_on_unemployment_rate":    StatcanSpec("lfs_on_unemployment_rate", 2063949, "14-10-0287-01",
                                               "%", "monthly", "labour", sa=True,
                                               notes=(
                                                   "Ontario; Unemployment rate; Total - Gender; 15+; Estimate; SA. "
                                                   "Cube coord 7.7.1.1.1.1.0.0.0.0. Resolved 2026-05-11."
                                               )),
    "lfs_ab_unemployment_rate":    StatcanSpec("lfs_ab_unemployment_rate", 2064516, "14-10-0287-01",
                                               "%", "monthly", "labour", sa=True,
                                               notes=(
                                                   "Alberta; Unemployment rate; Total - Gender; 15+; Estimate; SA. "
                                                   "Cube coord 10.7.1.1.1.1.0.0.0.0. Resolved 2026-05-11."
                                               )),
    "lfs_bc_unemployment_rate":    StatcanSpec("lfs_bc_unemployment_rate", 2064705, "14-10-0287-01",
                                               "%", "monthly", "labour", sa=True,
                                               notes=(
                                                   "British Columbia; Unemployment rate; Total - Gender; 15+; Estimate; SA. "
                                                   "Cube coord 11.7.1.1.1.1.0.0.0.0. Resolved 2026-05-11."
                                               )),
    # Unemployment by duration of search (Table 14-10-0342-01).
    # Resolved 2026-05-12 via getCubeMetadata + getSeriesInfoFromCubePidCoord.
    # Cube title: "Duration of unemployment, monthly, seasonally adjusted".
    # The Shimer / Elsby-Michaels-Solon (EMS) decomposition of UR variance into
    # inflow (job-loss / separation) and outflow (job-finding) rates needs a
    # "short-term unemployed" stock series U_short_t -- the standard EMS proxy
    # is unemployed-less-than-one-month, which in StatCan-bucket terms is the
    # "1 to 4 weeks" series. Once U_short is on disk, the job-finding rate
    # f_t can be backed out of stock data alone as
    #   f_t = 1 - (U_{t+1} - U_short_{t+1}) / U_t
    # i.e., the share of last-month's unemployed who are no longer unemployed
    # (or are newly unemployed) this month.
    #
    # Coordinate template: Geo.Duration.Age.Gender.Statistics.DataType.0.0.0.0
    # Canada=1, all-ages=1, total-gender=1, Estimate=1, SA=1.
    # UOM 428 = persons; scalarFactorCode=3 = thousands -> scale 0.001 to millions
    # so the series is unit-compatible with unemployment_level (also millions).
    #
    # The full bucket set is registered so future cuts (long-term-unemployed
    # share, average-duration overlay) don't require a second WDS round-trip.
    "unemployment_total_duration": StatcanSpec(
        "unemployment_total_duration", 1078667526, "14-10-0342-01",
        "Millions", "monthly", "labour", scale=0.001, sa=True,
        notes=(
            "Total unemployed, all duration buckets, Canada 15+, SA. "
            "Reconciliation companion to unemployment_level (different cube; "
            "the duration table has a 'duration unknown' bucket so the sum of "
            "1-4 + 5-13 + 14-26 + 27+ falls short of this total by 50-80k). "
            "Coord 1.1.1.1.1.1.0.0.0.0. Resolved 2026-05-12."
        ),
    ),
    "unemployment_1_to_4_weeks": StatcanSpec(
        "unemployment_1_to_4_weeks", 1078667742, "14-10-0342-01",
        "Millions", "monthly", "labour", scale=0.001, sa=True,
        notes=(
            "Unemployed 1 to 4 weeks (short-term unemployed), Canada 15+, SA. "
            "Primary input to the Shimer / EMS UR decomposition: serves as "
            "U_short_t for backing out the job-finding rate from stock data. "
            "Coord 1.3.1.1.1.1.0.0.0.0. Resolved 2026-05-12."
        ),
    ),
    "unemployment_5_to_13_weeks": StatcanSpec(
        "unemployment_5_to_13_weeks", 1078667850, "14-10-0342-01",
        "Millions", "monthly", "labour", scale=0.001, sa=True,
        notes="Unemployed 5 to 13 weeks, Canada 15+, SA. Coord 1.4.1.1.1.1.0.0.0.0. Resolved 2026-05-12.",
    ),
    "unemployment_14_to_26_weeks": StatcanSpec(
        "unemployment_14_to_26_weeks", 1078667958, "14-10-0342-01",
        "Millions", "monthly", "labour", scale=0.001, sa=True,
        notes="Unemployed 14 to 26 weeks, Canada 15+, SA. Coord 1.5.1.1.1.1.0.0.0.0. Resolved 2026-05-12.",
    ),
    "unemployment_27_plus_weeks": StatcanSpec(
        "unemployment_27_plus_weeks", 1078668066, "14-10-0342-01",
        "Millions", "monthly", "labour", scale=0.001, sa=True,
        notes=(
            "Unemployed 27 weeks or more (long-term unemployed), Canada 15+, SA. "
            "Coord 1.6.1.1.1.1.0.0.0.0. Resolved 2026-05-12."
        ),
    ),

    # EI Regular Beneficiaries (Wave 5 brief, Section 5 backend item 1).
    # Source: StatCan Table 14-10-0011-01 ("Employment Insurance Beneficiaries
    # by Province/Territory; type of income benefits and sex"), Canada-total,
    # regular benefits, SA, monthly count of persons. v64549350 was lifted
    # from boc-tracker on 2026-05-11 (ei_regular_beneficiaries.csv on disk
    # covers 1997-01 through 2026-02; ~80-day lag is typical). Registering
    # here makes future re-fetches go through the standard pipeline runner
    # rather than relying on the lift script for refresh cadence.
    "ei_regular_beneficiaries":    StatcanSpec(
        "ei_regular_beneficiaries", 64549350, "14-10-0011-01",
        "Persons", "monthly", "labour", sa=True,
        notes=(
            "EI regular benefits recipients, Canada total, SA. "
            "Demand-side cyclical-inflection signal (Wave 5 Panel 7 Labour). "
            "StatCan publishes raw counts in persons; chart-side display divides "
            "by 1000 to render in thousands. ~80-day publication lag from "
            "reference month. Lifted 2026-05-11 from boc-tracker."
        ),
    ),

    # ----- Housing (Section 4.4) ------------------------------------------
    "housing_starts": StatcanSpec("housing_starts", 52300157, "34-10-0158-01",
                                  "Units (SAAR)", "monthly", "housing", sa=True),
    "residential_permits": StatcanSpec("residential_permits", 1675119646, "34-10-0292-01",
                                       "C$ thousands", "monthly", "housing", sa=True),
    "new_housing_price_index": StatcanSpec("new_housing_price_index", 111955442, "18-10-0205-01",
                                           "Index, Dec 2016=100", "monthly", "housing", sa=False),
    # Completions (canon 4.4 element 2)
    # Table 34-10-0135-01 publishes "Housing completions, by intended market". Specific intended-market
    # vectors require getCubeMetadata; for v1 we register the headline total. Researcher confirmed the
    # table exists; vector ID below is the total-all-areas, all-intended-market candidate (probe-pending).
    "housing_completions_total": StatcanSpec("housing_completions_total", 100036095, "34-10-0135-01",
                                             "Units", "monthly", "housing", sa=False,
                                             notes="Total housing completions, all CMAs/areas (probe-pending)."),
    # Starts by intended market (rental vs ownership). Same caveat as completions.
    "housing_starts_homeowner": StatcanSpec("housing_starts_homeowner", 52300158, "34-10-0158-01",
                                            "Units (SAAR)", "monthly", "housing", sa=True,
                                            notes="Homeowner starts (intended market) (probe-pending)."),
    "housing_starts_rental":    StatcanSpec("housing_starts_rental", 52300159, "34-10-0158-01",
                                            "Units (SAAR)", "monthly", "housing", sa=True,
                                            notes="Rental starts (intended market) (probe-pending)."),
    "housing_starts_condo":     StatcanSpec("housing_starts_condo", 52300160, "34-10-0158-01",
                                            "Units (SAAR)", "monthly", "housing", sa=True,
                                            notes="Condo starts (intended market) (probe-pending)."),
    # CMA annual population for the population-to-stock ratio (canon 4.4 element 6).
    # Resolved 2026-05-11: Table 17-10-0135 is ARCHIVED (2016 boundaries, last refPer 2022-07-01);
    # successor is 17-10-0148-01 ("Population estimates, July 1, by CMA/CA, 2021 boundaries"),
    # CURRENT, runs 2001-2025. Coord template: {GEO}.1.1.0.0.0.0.0.0.0 = CMA; Total-gender; All ages.
    "pop_cma_toronto":  StatcanSpec("pop_cma_toronto", 1589887692, "17-10-0148-01",
                                    "Persons", "annual", "housing", sa=False,
                                    notes=(
                                        "Toronto CMA annual population, July 1. Table 17-10-0148 (2021 boundaries) -- "
                                        "the previously-wired Table 17-10-0135 is archived. "
                                        "Cube coord 22.1.1.0.0.0.0.0.0.0. Resolved 2026-05-11."
                                    )),
    "pop_cma_vancouver": StatcanSpec("pop_cma_vancouver", 1589917707, "17-10-0148-01",
                                    "Persons", "annual", "housing", sa=False,
                                    notes=(
                                        "Vancouver CMA annual population, July 1. Cube coord 44.1.1.0.0.0.0.0.0.0. "
                                        "Resolved 2026-05-11 (companion vector to Toronto resolution)."
                                    )),
    "pop_cma_montreal":  StatcanSpec("pop_cma_montreal", 1589878032, "17-10-0148-01",
                                    "Persons", "annual", "housing", sa=False,
                                    notes=(
                                        "Montreal CMA annual population, July 1. Cube coord 14.1.1.0.0.0.0.0.0.0. "
                                        "Resolved 2026-05-11 (companion vector to Toronto resolution)."
                                    )),
    "pop_cma_calgary":   StatcanSpec("pop_cma_calgary", 1589908737, "17-10-0148-01",
                                    "Persons", "annual", "housing", sa=False,
                                    notes=(
                                        "Calgary CMA annual population, July 1. Cube coord 37.1.1.0.0.0.0.0.0.0. "
                                        "Resolved 2026-05-11."
                                    )),
    "pop_cma_ottawa_gatineau": StatcanSpec("pop_cma_ottawa_gatineau", 1589930472, "17-10-0148-01",
                                    "Persons", "annual", "housing", sa=False,
                                    notes=(
                                        "Ottawa-Gatineau CMA annual population, July 1. Cube coord 15.1.1.0.0.0.0.0.0.0. "
                                        "Resolved 2026-05-11."
                                    )),
    # Housing stock by CMA (Table 36-10-0688). Annual; probe-pending.
    "housing_stock_canada": StatcanSpec("housing_stock_canada", 1234567890, "36-10-0688-01",
                                        "Dwellings", "annual", "housing", sa=False,
                                        notes="Canada-wide housing stock (probe-pending; placeholder vector — verify via getCubeMetadata)."),

    # Household debt service ratio (Table 11-10-0065-01). Quarterly, SA.
    # Resolved 2026-05-13 via bulk CSV download (11100065-eng.zip). The WDS
    # getCubeMetadata endpoint returns 404 for this product ID -- a known quirk
    # of post-2020 NBSA-revision tables in the WDS REST API. The batch POST
    # endpoint (getDataFromVectorsAndLatestNPeriods) works normally.
    #
    # Series: coord 1.1.22 = "Debt service ratio"; Seasonally adjusted at annual
    # rates; Canada; UOM=Ratio; SCALAR=units (no scaling); Decimals=2.
    # "Ratio" is StatCan's UOM label for percent of disposable income --
    # values are already in percent (14.57 = 14.57% of income). Date range:
    # 1990-Q1 through 2025-Q4 (144 obs; latest refPer 2025-10-01).
    #
    # Companion series available in the same table if needed later:
    #   v1001696814 = Mortgage DSR (SA)             coord 1.1.23
    #   v1001696815 = Non-mortgage DSR (SA)         coord 1.1.24
    #   v1001696816 = DSR interest only (SA)        coord 1.1.25
    "household_dsr": StatcanSpec(
        name="household_dsr",
        vector_id=1001696813, table_id="11-10-0065-01",
        units="% of disposable income (SA)",
        frequency="quarterly", section="housing",
        sa=True,
        notes=(
            "Household total debt service ratio (principal + interest payments as "
            "a share of disposable income before interest), Canada, seasonally "
            "adjusted at annual rates. StatCan Table 11-10-0065-01 coordinate 1.1.22. "
            "Resolved 2026-05-13 via bulk CSV download (getCubeMetadata returns 404 "
            "for this post-2020 NBSA-revision table; vector fetch works normally). "
            "Values already in percent units (14.57 = 14.57%); no scaling required. "
            "Backfill: 1990-Q1 to present (~144 quarterly obs). "
            "Companion mortgage-only DSR = v1001696814."
        ),
    ),

    # ----- Trade (Section 4.7) --------------------------------------------
    "trade_balance_total": StatcanSpec("trade_balance_total", 87008984, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True,
                                       notes="Trade balance, BOP basis, all countries."),
    "trade_exports_total": StatcanSpec("trade_exports_total", 87008897, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True),
    "trade_imports_total": StatcanSpec("trade_imports_total", 87008781, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True),
    "trade_balance_us":    StatcanSpec("trade_balance_us", 87008985, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True),
    "trade_exports_us":    StatcanSpec("trade_exports_us", 87008898, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True),
    "trade_imports_us":    StatcanSpec("trade_imports_us", 87008782, "12-10-0119-01",
                                       "C$ millions", "monthly", "trade", sa=True),
    # ---------------------------------------------------------------------------
    # By-partner bilateral flows: Table 12-10-0011-01
    # ---------------------------------------------------------------------------
    # "International merchandise trade for all countries and by Principal Trading
    # Partners, monthly" (CANSIM 228-0069). Customs basis, unadjusted. Starts
    # 1997-01. Latest available: 2026-03 (released 2026-05-05).
    #
    # DIMENSION STRUCTURE (verified 2026-05-14 via bulk CSV download):
    #   Dim1: Geography        (1=Canada -- only value)
    #   Dim2: Trade            (1=Import, 2=Export, 3=Trade Balance)
    #   Dim3: Basis            (1=Customs, 2=Balance of payments)
    #   Dim4: Seasonal adjust  (1=Unadjusted, 2=Seasonally adjusted)
    #   Dim5: Partner country  (member IDs below)
    #
    # All vectors registered here are Customs basis, Unadjusted (dim3=1, dim4=1)
    # so series are strictly comparable across countries. SA variant exists only
    # on the BOP basis; for SA bilateral data use the BOP-basis table 12-10-0119-01
    # (the trade_exports_us / trade_imports_us entries already in catalog above).
    #
    # COVERAGE GAPS -- countries NOT in this table's 27-partner list:
    #   Vietnam, Thailand (ASEAN), UAE, Qatar, Kuwait, Bahrain, Oman (GCC).
    # The table covers "top 27 principal trading partners based on annual 2012
    # total merchandise trade data." UAE/GCC partners were below the 2012 cutoff.
    # For these missing countries, no StatCan vector-based alternative exists
    # in the WDS; they would require manual import from UN Comtrade or bulk CSV
    # filtering on the all-countries (dim5=1) aggregate (not per-country).
    # Flag surfaced; frontend can render "data not available" for GCC except
    # Saudi Arabia.
    #
    # SA BOP-basis counterparts also exist in Table 12-10-0011-01 (dim3=2,
    # dim4=2) for all 27 countries; not registered here to avoid doubling the
    # catalog. The SA US vectors already registered above under 12-10-0119-01
    # are the canonical SA headline series.
    #
    # Vector IDs resolved from primary source bulk CSV download 2026-05-14.
    # No placeholder IDs -- all verified.
    # Coordinates listed in notes as: geo.trade.basis.sa.partner (dim1-5).

    # --- United States ---
    "trade_exports_us_customs": StatcanSpec(
        "trade_exports_us_customs", 87008869, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to United States, customs basis, unadjusted. "
            "Coord 1.2.1.1.2. Mar-2026: C$49,494M. "
            "Companion BOP SA: trade_exports_us (v87008898 in Table 12-10-0119-01). "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    "trade_imports_us_customs": StatcanSpec(
        "trade_imports_us_customs", 87008753, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from United States, customs basis, unadjusted. "
            "Coord 1.1.1.1.2. Mar-2026: C$33,930M. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),

    # --- China ---
    "trade_exports_chn": StatcanSpec(
        "trade_exports_chn", 87008878, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to China, customs basis, unadjusted. "
            "Coord 1.2.1.1.11. Mar-2026: C$3,687M. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    "trade_imports_chn": StatcanSpec(
        "trade_imports_chn", 87008762, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from China, customs basis, unadjusted. "
            "Coord 1.1.1.1.11. Mar-2026: C$7,152M. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),

    # --- United Kingdom ---
    "trade_exports_gbr": StatcanSpec(
        "trade_exports_gbr", 87008871, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to United Kingdom, customs basis, unadjusted. "
            "Coord 1.2.1.1.4. "
            "Note: UK was part of EU aggregate (dim5=3) through Dec-2020; "
            "from Jan-2021 UK flows are counted separately. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    "trade_imports_gbr": StatcanSpec(
        "trade_imports_gbr", 87008755, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from United Kingdom, customs basis, unadjusted. "
            "Coord 1.1.1.1.4. UK left EU aggregate Jan-2021. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),

    # --- Germany ---
    "trade_exports_deu": StatcanSpec(
        "trade_exports_deu", 87008872, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to Germany, customs basis, unadjusted. Coord 1.2.1.1.5. Resolved 2026-05-14.",
    ),
    "trade_imports_deu": StatcanSpec(
        "trade_imports_deu", 87008756, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Germany, customs basis, unadjusted. Coord 1.1.1.1.5. Resolved 2026-05-14.",
    ),

    # --- France ---
    "trade_exports_fra": StatcanSpec(
        "trade_exports_fra", 87008874, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to France, customs basis, unadjusted. Coord 1.2.1.1.7. Resolved 2026-05-14.",
    ),
    "trade_imports_fra": StatcanSpec(
        "trade_imports_fra", 87008758, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from France, customs basis, unadjusted. Coord 1.1.1.1.7. Resolved 2026-05-14.",
    ),

    # --- Netherlands ---
    "trade_exports_nld": StatcanSpec(
        "trade_exports_nld", 87008873, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to Netherlands, customs basis, unadjusted. Coord 1.2.1.1.6. Resolved 2026-05-14.",
    ),
    "trade_imports_nld": StatcanSpec(
        "trade_imports_nld", 87008757, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Netherlands, customs basis, unadjusted. Coord 1.1.1.1.6. Resolved 2026-05-14.",
    ),

    # --- Japan ---
    "trade_exports_jpn": StatcanSpec(
        "trade_exports_jpn", 87008880, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Japan, customs basis, unadjusted. "
            "Coord 1.2.1.1.13. Mar-2026: C$1,216M. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    "trade_imports_jpn": StatcanSpec(
        "trade_imports_jpn", 87008764, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from Japan, customs basis, unadjusted. "
            "Coord 1.1.1.1.13. Mar-2026: C$2,007M. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),

    # --- Mexico ---
    "trade_exports_mex": StatcanSpec(
        "trade_exports_mex", 87008879, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to Mexico, customs basis, unadjusted. Coord 1.2.1.1.12. Resolved 2026-05-14.",
    ),
    "trade_imports_mex": StatcanSpec(
        "trade_imports_mex", 87008763, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Mexico, customs basis, unadjusted. Coord 1.1.1.1.12. Resolved 2026-05-14.",
    ),

    # --- South Korea ---
    "trade_exports_kor": StatcanSpec(
        "trade_exports_kor", 87008881, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to South Korea, customs basis, unadjusted. Coord 1.2.1.1.14. Resolved 2026-05-14.",
    ),
    "trade_imports_kor": StatcanSpec(
        "trade_imports_kor", 87008765, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from South Korea, customs basis, unadjusted. Coord 1.1.1.1.14. Resolved 2026-05-14.",
    ),

    # --- India ---
    "trade_exports_ind": StatcanSpec(
        "trade_exports_ind", 87008886, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to India, customs basis, unadjusted. "
            "Coord 1.2.1.1.19. Mar-2026: C$503M. "
            "Carney diplomatic-focus target. Resolved 2026-05-14."
        ),
    ),
    "trade_imports_ind": StatcanSpec(
        "trade_imports_ind", 87008770, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from India, customs basis, unadjusted. "
            "Coord 1.1.1.1.19. Mar-2026: C$897M. "
            "Carney diplomatic-focus target. Resolved 2026-05-14."
        ),
    ),

    # --- Australia ---
    "trade_exports_aus": StatcanSpec(
        "trade_exports_aus", 87008892, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Australia, customs basis, unadjusted. "
            "Coord 1.2.1.1.25. Carney diplomatic-focus target. Resolved 2026-05-14."
        ),
    ),
    "trade_imports_aus": StatcanSpec(
        "trade_imports_aus", 87008776, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Australia, customs basis, unadjusted. Coord 1.1.1.1.25. Resolved 2026-05-14.",
    ),

    # --- Indonesia ---
    "trade_exports_idn": StatcanSpec(
        "trade_exports_idn", 87008894, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Indonesia, customs basis, unadjusted. "
            "Coord 1.2.1.1.27. ASEAN; Carney diplomatic-focus target. Resolved 2026-05-14."
        ),
    ),
    "trade_imports_idn": StatcanSpec(
        "trade_imports_idn", 87008778, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Indonesia, customs basis, unadjusted. Coord 1.1.1.1.27. Resolved 2026-05-14.",
    ),

    # --- Singapore ---
    "trade_exports_sgp": StatcanSpec(
        "trade_exports_sgp", 87008895, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Singapore, customs basis, unadjusted. "
            "Coord 1.2.1.1.28. ASEAN hub; Carney diplomatic-focus target. Resolved 2026-05-14."
        ),
    ),
    "trade_imports_sgp": StatcanSpec(
        "trade_imports_sgp", 87008779, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Singapore, customs basis, unadjusted. Coord 1.1.1.1.28. Resolved 2026-05-14.",
    ),

    # --- Saudi Arabia (only available GCC member in table) ---
    "trade_exports_sau": StatcanSpec(
        "trade_exports_sau", 87008888, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Saudi Arabia, customs basis, unadjusted. "
            "Coord 1.2.1.1.21. Only GCC member in Table 12-10-0011-01 (UAE, Qatar, "
            "Kuwait, Bahrain, Oman not in the 27-partner list). Resolved 2026-05-14."
        ),
    ),
    "trade_imports_sau": StatcanSpec(
        "trade_imports_sau", 87008772, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Imports from Saudi Arabia, customs basis, unadjusted. "
            "Coord 1.1.1.1.21. Resolved 2026-05-14."
        ),
    ),

    # --- Additional partners with regional relevance ---
    # Taiwan: tech/semiconductor supply chain; Hong Kong: China re-export proxy
    "trade_exports_twn": StatcanSpec(
        "trade_exports_twn", 87008890, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Exports to Taiwan, customs basis, unadjusted. Coord 1.2.1.1.23. Resolved 2026-05-14.",
    ),
    "trade_imports_twn": StatcanSpec(
        "trade_imports_twn", 87008774, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Taiwan, customs basis, unadjusted. Coord 1.1.1.1.23. Resolved 2026-05-14.",
    ),
    "trade_exports_hkg": StatcanSpec(
        "trade_exports_hkg", 87008882, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Exports to Hong Kong, customs basis, unadjusted. Coord 1.2.1.1.15. "
            "Useful as China re-export proxy. Resolved 2026-05-14."
        ),
    ),
    "trade_imports_hkg": StatcanSpec(
        "trade_imports_hkg", 87008766, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes="Imports from Hong Kong, customs basis, unadjusted. Coord 1.1.1.1.15. Resolved 2026-05-14.",
    ),

    # --- All-countries aggregate (customs basis, unadjusted total) ---
    # Note: the catalog already has BOP-SA totals (trade_exports_total,
    # trade_imports_total) from Table 12-10-0119-01 (v87008897, v87008781).
    # These customs-basis totals are the matching denominators for computing
    # per-country shares on a customs basis.
    "trade_exports_all_customs": StatcanSpec(
        "trade_exports_all_customs", 87008868, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Total exports, all countries, customs basis, unadjusted. "
            "Coord 1.2.1.1.1. Denominator for customs-basis partner-share computation. "
            "Distinct from trade_exports_total (BOP SA, Table 12-10-0119-01). "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    "trade_imports_all_customs": StatcanSpec(
        "trade_imports_all_customs", 87008752, "12-10-0011-01",
        "C$ millions", "monthly", "trade", sa=False,
        notes=(
            "Total imports, all countries, customs basis, unadjusted. "
            "Coord 1.1.1.1.1. Denominator for customs-basis partner-share computation. "
            "Resolved 2026-05-14 via bulk CSV."
        ),
    ),
    # Current account balances (Table 36-10-0014, annual). Resolved 2026-05-11
    # (research/wave2_vector_resolutions.md). Dim2 = 3 returns the BALANCE (net = receipts -
    # payments), not just receipts. Series labels: Canada; Balances; {Goods | Services |
    # Primary income | Secondary income}; All countries. UOM 81 ($M, decimals 0). Annual,
    # runs 1981-2025. The legacy v121079..v121082 (CANSIM 376-0001 vintage) were retired in
    # the BOP migration to the 36-10-00xx product family, which is why they returned
    # responseStatusCode=4 ("vector not found") on the 2026-05-11 probe.
    #
    # Quarterly alternative for the same dimensions is Table 36-10-0016 ->
    # v61915093/v61915103/v61915151/v61915199; lift those to a quarterly companion set
    # only when chart panels need quarterly cadence (canon 4.7 currently calls for annual).
    "ca_goods_income":     StatcanSpec("ca_goods_income", 61914625, "36-10-0014-01",
                                        "C$ millions", "annual", "trade", sa=False,
                                        notes=(
                                            "Current-account goods balance (annual). Coord 1.3.3.1.0.0.0.0.0.0. "
                                            "Note: slug uses '_income' for parallelism with the four-component decomp; "
                                            "this is net trade in goods (balance), not goods receipts. Resolved 2026-05-11."
                                        )),
    "ca_services_income":  StatcanSpec("ca_services_income", 61914635, "36-10-0014-01",
                                        "C$ millions", "annual", "trade", sa=False,
                                        notes=(
                                            "Current-account services balance (annual). Coord 1.3.5.1.0.0.0.0.0.0. "
                                            "Resolved 2026-05-11."
                                        )),
    "ca_primary_income":   StatcanSpec("ca_primary_income", 61914683, "36-10-0014-01",
                                        "C$ millions", "annual", "trade", sa=False,
                                        notes=(
                                            "Current-account primary income balance (annual). Coord 1.3.11.1.0.0.0.0.0.0. "
                                            "Resolved 2026-05-11."
                                        )),
    "ca_secondary_income": StatcanSpec("ca_secondary_income", 61914731, "36-10-0014-01",
                                        "C$ millions", "annual", "trade", sa=False,
                                        notes=(
                                            "Current-account secondary income balance (annual). Coord 1.3.17.1.0.0.0.0.0.0. "
                                            "Resolved 2026-05-11."
                                        )),
    # Exports / imports by HS section product (Tables 12-10-0121-01 / 12-10-0122-01). ~12 sections each.
    # Vectors are HS-section coded; probe-pending; registered as placeholders for now.
    # The intent here is to give the catalog a slot per section; backend will resolve actual vectors via
    # one-time getCubeMetadata probe and update the vector_id field.
    "trade_exports_energy":     StatcanSpec("trade_exports_energy", 1001212101, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Energy exports HS section (probe-pending)."),
    "trade_exports_metals":     StatcanSpec("trade_exports_metals", 1001212102, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Metals exports HS section (probe-pending)."),
    "trade_exports_autos":      StatcanSpec("trade_exports_autos", 1001212103, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Autos exports HS section (probe-pending)."),
    "trade_exports_machinery":  StatcanSpec("trade_exports_machinery", 1001212104, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Machinery exports HS section (probe-pending)."),
    "trade_exports_consumer":   StatcanSpec("trade_exports_consumer", 1001212105, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Consumer goods exports HS section (probe-pending)."),
    "trade_exports_agri":       StatcanSpec("trade_exports_agri", 1001212106, "12-10-0121-01", "C$ millions", "monthly", "trade", sa=True, notes="Agriculture exports HS section (probe-pending)."),
    "trade_imports_energy":     StatcanSpec("trade_imports_energy", 1001212201, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Energy imports HS section (probe-pending)."),
    "trade_imports_metals":     StatcanSpec("trade_imports_metals", 1001212202, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Metals imports HS section (probe-pending)."),
    "trade_imports_autos":      StatcanSpec("trade_imports_autos", 1001212203, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Autos imports HS section (probe-pending)."),
    "trade_imports_machinery":  StatcanSpec("trade_imports_machinery", 1001212204, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Machinery imports HS section (probe-pending)."),
    "trade_imports_consumer":   StatcanSpec("trade_imports_consumer", 1001212205, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Consumer goods imports HS section (probe-pending)."),
    "trade_imports_agri":       StatcanSpec("trade_imports_agri", 1001212206, "12-10-0122-01", "C$ millions", "monthly", "trade", sa=True, notes="Agriculture imports HS section (probe-pending)."),
    # Terms of trade. Resolved 2026-05-11: there is no StatCan-published "ToT"
    # standalone series; the canonical national-accounts ToT is the ratio of
    # the export goods-and-services implicit price index to the import
    # goods-and-services implicit price index, both from Table 36-10-0106
    # (GDP price indexes, quarterly). The prior catalog entry pointed at
    # v62305749 in Table 36-10-0103 ("GDP income-based") which was a value
    # in C$ millions, not an index -- wrong cube entirely. Now we register
    # the two underlying IPI vectors as raw inputs and derive the ratio in
    # pipeline.build.derive_terms_of_trade -> data/processed/terms_of_trade.csv.
    "tot_exports_ipi": StatcanSpec(
        "tot_exports_ipi", 62307276, "36-10-0106-01",
        "Index, 2017=100 (SA)", "quarterly", "trade", sa=True,
        notes=(
            "Implicit price index, exports of goods and services, quarterly SA. "
            "Numerator for the national-accounts terms-of-trade ratio. "
            "Cube coord 1.1.11.0.0.0.0.0.0.0 (Geography=1, Implicit price index, "
            "Exports of goods and services). Resolved 2026-05-11."
        ),
    ),
    "tot_imports_ipi": StatcanSpec(
        "tot_imports_ipi", 62307279, "36-10-0106-01",
        "Index, 2017=100 (SA)", "quarterly", "trade", sa=True,
        notes=(
            "Implicit price index, imports of goods and services, quarterly SA. "
            "Denominator for the national-accounts terms-of-trade ratio. "
            "Cube coord 1.1.15.0.0.0.0.0.0.0. Resolved 2026-05-11."
        ),
    ),
    # Quarterly current-account components (Table 36-10-0018, SA quarterly).
    # Resolved 2026-05-11. The four sub-component balances sum to the headline
    # current_account_balance (Total current account). UOM is C$ millions.
    # Companion to the annual ca_*_income set (Table 36-10-0014) above; the
    # quarterly cadence is what the Trade Panel 2 stacked-bar decomposition
    # needs.
    "current_account_balance": StatcanSpec(
        "current_account_balance", 61915304, "36-10-0018-01",
        "C$ millions", "quarterly", "trade", sa=True,
        notes=(
            "Total current account balance (headline), quarterly SA. "
            "Coord 1.3.1.0.0.0.0.0.0.0. Equals goods + services + primary income + "
            "secondary income to within statistical-discrepancy. Resolved 2026-05-11."
        ),
    ),
    "ca_goods_balance_q": StatcanSpec(
        "ca_goods_balance_q", 61915306, "36-10-0018-01",
        "C$ millions", "quarterly", "trade", sa=True,
        notes="Current-account goods balance, quarterly SA. Coord 1.3.23.0.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "ca_services_balance_q": StatcanSpec(
        "ca_services_balance_q", 61915308, "36-10-0018-01",
        "C$ millions", "quarterly", "trade", sa=True,
        notes="Current-account services balance, quarterly SA. Coord 1.3.35.0.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "ca_primary_income_q": StatcanSpec(
        "ca_primary_income_q", 61915313, "36-10-0018-01",
        "C$ millions", "quarterly", "trade", sa=True,
        notes="Current-account primary income balance, quarterly SA. Coord 1.3.2.0.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    "ca_secondary_income_q": StatcanSpec(
        "ca_secondary_income_q", 61915327, "36-10-0018-01",
        "C$ millions", "quarterly", "trade", sa=True,
        notes="Current-account secondary income balance, quarterly SA. Coord 1.3.17.0.0.0.0.0.0.0. Resolved 2026-05-11.",
    ),
    # Energy supply and disposition (Table 25-10-0044-01) — monthly.
    "energy_supply_disposition": StatcanSpec("energy_supply_disposition", 5000044, "25-10-0044-01",
                                              "Cubic metres", "monthly", "trade", sa=False,
                                              notes="Energy supply and disposition headline series (probe-pending)."),
    # FDI by industry, inward (FDIC) and outward (CDIA) — annual, C$ millions.
    # Source: StatCan Table 36-10-0659-01 ("International investment position,
    # Canadian direct investment abroad and foreign direct investment in Canada,
    # by industry and select countries"). Annual. scalarFactorCode=6 (millions);
    # values arrive already in C$ millions — no additional scale needed.
    # Dimension structure: Geo(1=Canada) . Industry . Country(1=All) . Direction
    #   Direction dim4=1 = CDIA (Canadian direct investment abroad, outward)
    #   Direction dim4=2 = FDIC (Foreign direct investment in Canada, inward)
    # Resolved 2026-05-13 via POST getSeriesInfoFromCubePidCoord on productId=36100659.
    # Full industry enumeration: d2=1..40; key top-level NAICS aggregates registered here.
    # NOTE: The previously-cataloged fdi_total stub (62800001 in Table 36-10-0008-01)
    # was pointing at the by-COUNTRY table (not by industry); replaced by the correct
    # Table 36-10-0659-01 entries below.
    #
    # --- Inward (FDIC) total and key sectors ---
    "fdi_inward_total": StatcanSpec(
        "fdi_inward_total", 1271722443, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "Foreign direct investment in Canada (FDIC) — total, all industries. "
            "Coord 1.1.1.2.0.0.0.0.0.0 (Canada; Total all industries; All countries; FDIC total book value). "
            "Annual. 2025 value: C$1,600,470M. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_mining_oil_gas": StatcanSpec(
        "fdi_inward_mining_oil_gas", 1271722563, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Mining, quarrying, and oil and gas extraction. "
            "Coord 1.3.1.2.0.0.0.0.0.0. Annual. 2025: C$183,153M. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_manufacturing": StatcanSpec(
        "fdi_inward_manufacturing", 1271722923, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Manufacturing (NAICS 31-33 aggregate). "
            "Coord 1.9.1.2.0.0.0.0.0.0. Annual. 2025: C$258,253M. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_finance_insurance": StatcanSpec(
        "fdi_inward_finance_insurance", 1271724483, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Finance and insurance (NAICS 52). "
            "Coord 1.35.1.2.0.0.0.0.0.0. Annual. 2025: C$205,577M. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_real_estate": StatcanSpec(
        "fdi_inward_real_estate", 1271724543, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Real estate and rental and leasing (NAICS 53). "
            "Coord 1.36.1.2.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_professional_services": StatcanSpec(
        "fdi_inward_professional_services", 1271724603, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Professional, scientific and technical services (NAICS 54). "
            "Coord 1.37.1.2.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),
    "fdi_inward_wholesale_trade": StatcanSpec(
        "fdi_inward_wholesale_trade", 1271724243, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "FDIC — Wholesale trade (NAICS 41). "
            "Coord 1.31.1.2.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),
    #
    # --- Outward (CDIA) total and key sectors ---
    "fdi_outward_total": StatcanSpec(
        "fdi_outward_total", 1271722442, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "Canadian direct investment abroad (CDIA) — total, all industries. "
            "Coord 1.1.1.1.0.0.0.0.0.0 (Canada; Total all industries; All countries; CDIA total book value). "
            "Annual. 2025 value: C$2,428,900M. Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_mining_oil_gas": StatcanSpec(
        "fdi_outward_mining_oil_gas", 1271722562, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Mining, quarrying, and oil and gas extraction. "
            "Coord 1.3.1.1.0.0.0.0.0.0. Annual. 2025: C$225,065M. Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_manufacturing": StatcanSpec(
        "fdi_outward_manufacturing", 1271722922, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Manufacturing (NAICS 31-33 aggregate). "
            "Coord 1.9.1.1.0.0.0.0.0.0. Annual. 2025: C$137,095M. Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_finance_insurance": StatcanSpec(
        "fdi_outward_finance_insurance", 1271724482, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Finance and insurance (NAICS 52). "
            "Coord 1.35.1.1.0.0.0.0.0.0. Annual. 2025: C$845,069M. "
            "Finance is by far the largest outward FDI sector (35% of CDIA total). "
            "Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_real_estate": StatcanSpec(
        "fdi_outward_real_estate", 1271724542, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Real estate and rental and leasing (NAICS 53). "
            "Coord 1.36.1.1.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_professional_services": StatcanSpec(
        "fdi_outward_professional_services", 1271724602, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Professional, scientific and technical services (NAICS 54). "
            "Coord 1.37.1.1.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),
    "fdi_outward_wholesale_trade": StatcanSpec(
        "fdi_outward_wholesale_trade", 1271724242, "36-10-0659-01",
        "C$ millions", "annual", "trade", sa=False,
        notes=(
            "CDIA — Wholesale trade (NAICS 41). "
            "Coord 1.31.1.1.0.0.0.0.0.0. Annual. Resolved 2026-05-13."
        ),
    ),

    # -----------------------------------------------------------------------
    # Sectoral merchandise exports by destination (US vs non-US) — tariff-
    # exposed sectors: steel, aluminum, softwood lumber, autos.
    #
    # SOURCE: StatCan Table 12-10-0182-01
    #   "Canadian international merchandise trade for total exports, domestic
    #    exports and re-exports, monthly"
    # Title as returned by WDS: same. Current through 2026-03-01.
    # Start date: 1997-01-01 (351 monthly observations to 2026-03).
    #
    # DIMENSIONS
    #   Dim 1 (Geography)      : 1 = Canada
    #   Dim 2 (NAPCS)          : commodity, 113 members (sub-chapter granularity)
    #   Dim 3 (Trade)          : 1=Export, 2=Domestic exports, 3=Re-exports
    #   Dim 4 (Partner dest.)  : 1=All countries, 2=US, ...29 total
    #   Dim 5 (Partner origin) : 1=All countries origin (not used editorially)
    #
    # UNIT / SCALE
    #   scalarFactorCode=3 (thousands), UOM=81 (C$).
    #   Raw values are in C$ thousands; scale=0.001 normalises to C$ millions
    #   for unit-consistency with the existing trade_exports_us / trade_exports_total
    #   series (scalarFactorCode=6, already in C$M).
    #
    # HS-CODE / NAPCS MAPPING
    #   The WDS vector API (getDataFromVectorsAndLatestNPeriods) does NOT expose
    #   data from the CIMT tables (12100147/12100148) which have native HS-chapter
    #   structure. Those tables return vid=0 for all coordinates (confirmed via
    #   POST getSeriesInfoFromCubePidCoord 2026-05-14). Table 12-10-0182-01 is the
    #   finest-grained WDS-accessible trade table with a partner-country dimension
    #   that is current (end=2026-03). Its NAPCS commodity classification maps to
    #   HS chapters at the sub-chapter level as follows:
    #
    #   STEEL (HS 72 — Iron and steel):
    #     NAPCS 30 = Unwrought iron, steel and ferro-alloys   (HS 7201-7206)
    #     NAPCS 31 = Basic and semi-finished iron/steel products (HS 7207-7229)
    #     Pipeline sums NAPCS 30 + NAPCS 31 to produce a Steel aggregate.
    #     Caveat: NAPCS 30+31 excludes downstream fabricated steel products
    #     (HS 73xx, fabricated metal products), which fall under NAPCS 39.
    #     For the Section 232 tariff scope (primary steel mill products), this
    #     is the editorially correct boundary.
    #
    #   ALUMINUM (HS 76 — Aluminum and articles thereof):
    #     NAPCS 32 = Unwrought aluminum and aluminum alloys   (HS 7601)
    #     NAPCS 38 = Basic and semi-finished products of aluminum (HS 7602-7616)
    #     Pipeline sums NAPCS 32 + NAPCS 38. Excludes fabricated aluminum
    #     articles under NAPCS 39 (fabricated metal products) — consistent with
    #     Section 232 tariff scope (primary aluminum).
    #
    #   SOFTWOOD LUMBER (HS 4407.10 — Sawn coniferous wood):
    #     NAPCS 55 = Lumber and other sawmill products
    #     This is a single NAPCS sub-chapter. It bundles coniferous and
    #     non-coniferous sawn lumber; there is no finer NAPCS cut at this
    #     granularity. Editorially acceptable: >95% of Canadian lumber exports
    #     are softwood (BC interior spruce-pine-fir, Quebec SPF, etc.).
    #     The US CVD/AD duties target "softwood lumber products" as defined
    #     by the US International Trade Commission; NAPCS 55 is the
    #     closest publicly available aggregate.
    #
    #   AUTOS (HS 8703 + HS 8708 — Motor cars + Vehicle parts):
    #     NAPCS 81 = Passenger cars and light trucks   (HS 8703 + 8704 light)
    #     NAPCS 84 = Motor vehicle engines and motor vehicle parts (HS 8707-8708)
    #     Pipeline sums NAPCS 81 + NAPCS 84. This covers the two sub-sectors
    #     that dominate Canada-US automotive trade flows (assembled vehicles
    #     and CUSMA-qualifying parts). Excludes NAPCS 82 (medium/heavy trucks)
    #     and NAPCS 83 (tires) which are not the primary Section 232 / IEEPA
    #     auto-tariff scope. Add NAPCS 82 if editorial scope widens to
    #     all motor vehicles.
    #
    #   COPPER (HS 7401-7403 — Unwrought copper and copper alloys):
    #     NAPCS 33 = Unwrought copper and copper alloys (HS 7401-7403)
    #     Single sub-chapter; no finer copper-only NAPCS cut available.
    #     Section 232 tariff exposure since April 2026 copper proclamation.
    #     US share ~82% (March 2026); reflects Horne smelter (QC) + Trail (BC)
    #     refinery exports concentrated to US buyers.
    #
    # DERIVATION ARCHITECTURE
    #   The pipeline stores the 16 raw vectors below (2 NAPCS sub-components ×
    #   2 destinations × 3 sectors, plus 1 NAPCS × 2 destinations each for
    #   softwood and copper). A single derivation step
    #   (derive_sectoral_exports_by_destination() in pipeline/build.py) sums
    #   sub-components per sector and computes non-US as (total - US) for each
    #   of the five sectors. Output slugs:
    #
    #     data/processed/exports_steel_us.csv         (NAPCS 30+31 → US)
    #     data/processed/exports_steel_nonus.csv       (total - US)
    #     data/processed/exports_aluminum_us.csv       (NAPCS 32+38 → US)
    #     data/processed/exports_aluminum_nonus.csv
    #     data/processed/exports_softwood_us.csv       (NAPCS 55 → US)
    #     data/processed/exports_softwood_nonus.csv
    #     data/processed/exports_autos_us.csv          (NAPCS 81+84 → US)
    #     data/processed/exports_autos_nonus.csv
    #     data/processed/exports_copper_us.csv         (NAPCS 33 → US)
    #     data/processed/exports_copper_nonus.csv      (total - US)
    #
    #   All outputs in C$ millions. Monthly, NSA (Table 12-10-0182 publishes
    #   NSA only at NAPCS sub-chapter level; SA is not available at this
    #   commodity granularity).
    #
    # VECTOR RESOLUTION (2026-05-14 via POST getSeriesInfoFromCubePidCoord)
    #   Coord format: 1.{napcs}.1.{partner}.1.0.0.0.0.0 (10-part, trailing 0s)
    #   responseStatusCode=0 for all resolved vectors (confirmed data available).
    #   NOTE: correct WDS body format is [{productId: int, coordinate: str}]
    #   (array-wrapped, 'productId' key — not 'pid').
    # -----------------------------------------------------------------------

    # Steel sub-component A: Unwrought iron, steel and ferro-alloys (NAPCS 30)
    "exports_steel_unwrought_all": StatcanSpec(
        "exports_steel_unwrought_all",
        vector_id=1863612523, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought iron, steel and ferro-alloys (NAPCS 30), total exports, "
            "all countries of destination. Table 12-10-0182-01 coord "
            "1.30.1.1.1.0.0.0.0.0. scalarFactorCode=3; scale=0.001 -> C$M. "
            "Start 1997-01-01; NSA only at this NAPCS granularity. "
            "Resolved 2026-05-14. See catalog comment block for HS-NAPCS mapping."
        ),
    ),
    "exports_steel_unwrought_us": StatcanSpec(
        "exports_steel_unwrought_us",
        vector_id=1863612553, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought iron, steel and ferro-alloys (NAPCS 30), total exports, "
            "United States destination. Coord 1.30.1.2.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),
    # Steel sub-component B: Basic and semi-finished iron/steel products (NAPCS 31)
    "exports_steel_semifin_all": StatcanSpec(
        "exports_steel_semifin_all",
        vector_id=1863615133, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished iron or steel products (NAPCS 31), total "
            "exports, all countries. Coord 1.31.1.1.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),
    "exports_steel_semifin_us": StatcanSpec(
        "exports_steel_semifin_us",
        vector_id=1863615163, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished iron or steel products (NAPCS 31), total "
            "exports, United States. Coord 1.31.1.2.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),

    # Aluminum sub-component A: Unwrought aluminum and alloys (NAPCS 32)
    "exports_aluminum_unwrought_all": StatcanSpec(
        "exports_aluminum_unwrought_all",
        vector_id=1863617743, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "all countries. Coord 1.32.1.1.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_us": StatcanSpec(
        "exports_aluminum_unwrought_us",
        vector_id=1863617773, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "United States. Coord 1.32.1.2.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    # Aluminum sub-component B: Semi-finished aluminum products (NAPCS 38)
    "exports_aluminum_semifin_all": StatcanSpec(
        "exports_aluminum_semifin_all",
        vector_id=1863633403, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, all countries. "
            "Coord 1.38.1.1.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_us": StatcanSpec(
        "exports_aluminum_semifin_us",
        vector_id=1863633433, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, United States. "
            "Coord 1.38.1.2.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),

    # Softwood lumber: Lumber and other sawmill products (NAPCS 55)
    # Single sub-chapter; no further split available in WDS-accessible tables.
    "exports_softwood_all": StatcanSpec(
        "exports_softwood_all",
        vector_id=1863677773, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Lumber and other sawmill products (NAPCS 55), total exports, all "
            "countries. Coord 1.55.1.1.1.0.0.0.0.0. Closest WDS-accessible "
            "proxy for HS 4407.10 (sawn coniferous wood). >95pct of Canadian "
            "lumber exports are softwood; the NAPCS aggregate is the correct "
            "editorial boundary for the US CVD/AD duty scope. "
            "Resolved 2026-05-14."
        ),
    ),
    "exports_softwood_us": StatcanSpec(
        "exports_softwood_us",
        vector_id=1863677803, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Lumber and other sawmill products (NAPCS 55), total exports, "
            "United States. Coord 1.55.1.2.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),

    # Autos sub-component A: Passenger cars and light trucks (NAPCS 81)
    "exports_autos_cars_all": StatcanSpec(
        "exports_autos_cars_all",
        vector_id=1863745633, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Passenger cars and light trucks (NAPCS 81), total exports, all "
            "countries. Coord 1.81.1.1.1.0.0.0.0.0. Covers assembled vehicles "
            "under HS 8703 and light commercial (8704). Resolved 2026-05-14."
        ),
    ),
    "exports_autos_cars_us": StatcanSpec(
        "exports_autos_cars_us",
        vector_id=1863745663, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Passenger cars and light trucks (NAPCS 81), total exports, United "
            "States. Coord 1.81.1.2.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    # Autos sub-component B: Motor vehicle engines and parts (NAPCS 84)
    "exports_autos_parts_all": StatcanSpec(
        "exports_autos_parts_all",
        vector_id=1863753463, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Motor vehicle engines and motor vehicle parts (NAPCS 84), total "
            "exports, all countries. Coord 1.84.1.1.1.0.0.0.0.0. Covers "
            "HS 8707-8708. Resolved 2026-05-14."
        ),
    ),
    "exports_autos_parts_us": StatcanSpec(
        "exports_autos_parts_us",
        vector_id=1863753493, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Motor vehicle engines and motor vehicle parts (NAPCS 84), total "
            "exports, United States. Coord 1.84.1.2.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),

    # -----------------------------------------------------------------------
    # Copper exports by destination (NAPCS 33)
    #
    # NAPCS 33 = "Unwrought copper and copper alloys" (HS 7401-7403).
    # Confirmed 2026-05-14 via POST getSeriesInfoFromCubePidCoord on
    # productId=12100182, coord 1.33.1.1.1.0.0.0.0.0.
    # SeriesTitleEn: "Canada;Unwrought copper and copper alloys;Export;
    # All countries, country of destination;All countries, country of origin"
    #
    # This is a single NAPCS sub-chapter covering primary copper — refined
    # copper cathodes (HS 7403.11-7403.19), wire bar (HS 7403.21-7403.29),
    # and blister copper (HS 7402). This is the correct scope for Section 232
    # tariff exposure (April 2026 copper proclamation).
    #
    # Coverage: NAPCS 33 covers unwrought copper only. It does not include:
    #   - Copper wire/rod (HS 7408) — falls under NAPCS 37 (basic/semi-finished
    #     non-ferrous metals, except aluminum)
    #   - Copper tubes and fittings (HS 7411-7412) — also NAPCS 37
    #   - Fabricated copper articles (HS 7419) — NAPCS 39
    # For the Section 232 tariff scope (primary copper mill products), NAPCS 33
    # is the editorially correct boundary, consistent with the aluminum and
    # steel sub-chapter treatment.
    #
    # Data characteristics:
    #   - 351 monthly observations, 1997-01-01 to 2026-03-01
    #   - scalarFactorCode=3 (C$ thousands); scale=0.001 -> C$M
    #   - NSA only (no SA available at NAPCS sub-chapter granularity in this table)
    #   - March 2026: all-countries C$346.2M, US C$282.8M (US share ~82%)
    #     The high US share reflects Canada's concentrated copper refining
    #     exports via Glencore's Horne smelter (QC) and Teck's Trail ops (BC).
    #
    # Coord format: 1.{napcs}.1.{partner}.1.0.0.0.0.0 (10-part, trailing 0s)
    # Vectors resolved 2026-05-14 via POST getSeriesInfoFromCubePidCoord
    # (productId key, array-wrapped body).
    # -----------------------------------------------------------------------

    # Copper: Unwrought copper and copper alloys (NAPCS 33)
    # Single sub-chapter; no finer copper-only NAPCS cut available in WDS at
    # partner-country granularity. Coord 1.33.1.1.1.0.0.0.0.0 (all countries).
    "exports_copper_all": StatcanSpec(
        "exports_copper_all",
        vector_id=1863620353, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought copper and copper alloys (NAPCS 33, HS 7401-7403), total "
            "exports, all countries of destination. Coord 1.33.1.1.1.0.0.0.0.0. "
            "scalarFactorCode=3; scale=0.001 -> C$M. Start 1997-01-01; NSA only "
            "at this NAPCS granularity. Section 232 tariff scope (April 2026 "
            "copper proclamation). Resolved 2026-05-14."
        ),
    ),
    "exports_copper_us": StatcanSpec(
        "exports_copper_us",
        vector_id=1863620383, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought copper and copper alloys (NAPCS 33, HS 7401-7403), total "
            "exports, United States destination. Coord 1.33.1.2.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),

    # -----------------------------------------------------------------------
    # Gold / precious-metals exports by destination (NAPCS 35)
    #
    # NAPCS 35 = "Unwrought gold, silver, and platinum group metals, and
    # their alloys" (HS 7106 silver + HS 7108 gold + HS 7110 platinum group).
    # This is the editorially-correct sub-chapter for Canadian gold bullion
    # export flows. No finer gold-only NAPCS cut is available in the WDS-
    # accessible tables at this partner-country granularity.
    #
    # Editorial note: UK (London Bullion Market) absorbs ~95-97% of Canadian
    # precious-metals exports in most months. US is a minor destination.
    # The spike in Canada-UK merchandise trade flows in early 2026 is almost
    # entirely explained by gold/PGM re-routing through the London market
    # away from NY (COMEX) as US tariff risk rose.
    #
    # scalarFactorCode=3 (C$ thousands); scale=0.001 -> C$M, consistent with
    # all other 12-10-0182-01 entries.
    # Vectors resolved 2026-05-14 via POST getSeriesInfoFromCubePidCoord.
    # -----------------------------------------------------------------------
    "exports_gold_total": StatcanSpec(
        "exports_gold_total",
        vector_id=1863625573, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought gold, silver, and platinum group metals, and their alloys "
            "(NAPCS 35), total exports, all countries of destination. "
            "Coord 1.35.1.1.1.0.0.0.0.0. scalarFactorCode=3; scale=0.001 -> C$M. "
            "Start 1997-01-01; NSA only at this NAPCS granularity. "
            "Resolved 2026-05-14."
        ),
    ),
    "exports_gold_us": StatcanSpec(
        "exports_gold_us",
        vector_id=1863625603, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought gold, silver, and platinum group metals, and their alloys "
            "(NAPCS 35), total exports, United States of destination. "
            "Coord 1.35.1.2.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_gold_uk": StatcanSpec(
        "exports_gold_uk",
        vector_id=1863625693, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought gold, silver, and platinum group metals, and their alloys "
            "(NAPCS 35), total exports, United Kingdom of destination. "
            "Coord 1.35.1.5.1.0.0.0.0.0. Resolved 2026-05-14. "
            "UK (London Bullion Market) is consistently the dominant destination; "
            "typically absorbs 90-97% of all-countries total."
        ),
    ),

    # -----------------------------------------------------------------------
    # Aluminum exports by partner country (NAPCS 32 + NAPCS 38)
    #
    # These are the per-partner raw sub-components feeding the
    # derive_aluminum_by_partner() derivation in pipeline/build.py. That
    # function sums NAPCS 32 (unwrought) + NAPCS 38 (semi-finished) per
    # partner to produce the editorial "aluminum exports to <country>" series.
    #
    # Partners available in 12-10-0182-01 (29-member list, different from
    # Table 12-10-0011-01's 27-member list): All, US, China, Mexico, UK,
    # Japan, Germany, South Korea, Italy, France, Netherlands, Belgium,
    # Norway, Algeria, Hong Kong, Brazil, India, Switzerland, Saudi Arabia,
    # Turkey, Taiwan, Peru, Australia, Iraq, Indonesia, Singapore,
    # Russian Federation, Other countries.
    #
    # COVERAGE GAP: UAE, Qatar, Kuwait, Bahrain, Oman are NOT in this table's
    # partner dimension (same gap as 12-10-0011-01). No StatCan WDS alternative.
    # Data confirms aluminum flows to UAE/GCC are negligible in any case (the
    # editorial non-US story is Netherlands >> Mexico >> everyone else).
    #
    # All: scalarFactorCode=3; scale=0.001 -> C$M. Resolved 2026-05-14.
    # -----------------------------------------------------------------------

    # --- NAPCS 32: Unwrought aluminum and aluminum alloys ---
    "exports_aluminum_unwrought_gbr": StatcanSpec(
        "exports_aluminum_unwrought_gbr",
        vector_id=1863617863, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "United Kingdom destination. Coord 1.32.1.5.1.0.0.0.0.0. "
            "Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_chn": StatcanSpec(
        "exports_aluminum_unwrought_chn",
        vector_id=1863617803, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "China destination. Coord 1.32.1.3.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_jpn": StatcanSpec(
        "exports_aluminum_unwrought_jpn",
        vector_id=1863617893, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Japan destination. Coord 1.32.1.6.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_deu": StatcanSpec(
        "exports_aluminum_unwrought_deu",
        vector_id=1863617923, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Germany destination. Coord 1.32.1.7.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_kor": StatcanSpec(
        "exports_aluminum_unwrought_kor",
        vector_id=1863617953, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "South Korea destination. Coord 1.32.1.8.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_fra": StatcanSpec(
        "exports_aluminum_unwrought_fra",
        vector_id=1863618013, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "France destination. Coord 1.32.1.10.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_nld": StatcanSpec(
        "exports_aluminum_unwrought_nld",
        vector_id=1863618043, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Netherlands destination. Coord 1.32.1.11.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_bel": StatcanSpec(
        "exports_aluminum_unwrought_bel",
        vector_id=1863618073, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Belgium destination. Coord 1.32.1.12.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_mex": StatcanSpec(
        "exports_aluminum_unwrought_mex",
        vector_id=1863617833, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Mexico destination. Coord 1.32.1.4.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_ind": StatcanSpec(
        "exports_aluminum_unwrought_ind",
        vector_id=1863618253, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "India destination. Coord 1.32.1.18.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_unwrought_sgp": StatcanSpec(
        "exports_aluminum_unwrought_sgp",
        vector_id=1863618523, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Unwrought aluminum and aluminum alloys (NAPCS 32), total exports, "
            "Singapore destination. Coord 1.32.1.27.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),

    # --- NAPCS 38: Semi-finished aluminum products (by partner) ---
    "exports_aluminum_semifin_gbr": StatcanSpec(
        "exports_aluminum_semifin_gbr",
        vector_id=1863633523, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, United Kingdom destination. "
            "Coord 1.38.1.5.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_chn": StatcanSpec(
        "exports_aluminum_semifin_chn",
        vector_id=1863633463, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, China destination. "
            "Coord 1.38.1.3.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_jpn": StatcanSpec(
        "exports_aluminum_semifin_jpn",
        vector_id=1863633553, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Japan destination. "
            "Coord 1.38.1.6.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_deu": StatcanSpec(
        "exports_aluminum_semifin_deu",
        vector_id=1863633583, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Germany destination. "
            "Coord 1.38.1.7.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_kor": StatcanSpec(
        "exports_aluminum_semifin_kor",
        vector_id=1863633613, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, South Korea destination. "
            "Coord 1.38.1.8.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_fra": StatcanSpec(
        "exports_aluminum_semifin_fra",
        vector_id=1863633673, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, France destination. "
            "Coord 1.38.1.10.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_nld": StatcanSpec(
        "exports_aluminum_semifin_nld",
        vector_id=1863633703, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Netherlands destination. "
            "Coord 1.38.1.11.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_bel": StatcanSpec(
        "exports_aluminum_semifin_bel",
        vector_id=1863633733, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Belgium destination. "
            "Coord 1.38.1.12.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_mex": StatcanSpec(
        "exports_aluminum_semifin_mex",
        vector_id=1863633493, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Mexico destination. "
            "Coord 1.38.1.4.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_ind": StatcanSpec(
        "exports_aluminum_semifin_ind",
        vector_id=1863633913, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, India destination. "
            "Coord 1.38.1.18.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
    "exports_aluminum_semifin_sgp": StatcanSpec(
        "exports_aluminum_semifin_sgp",
        vector_id=1863634183, table_id="12-10-0182-01",
        units="C$ millions", frequency="monthly", section="trade",
        scale=0.001, sa=False,
        notes=(
            "Basic and semi-finished products of aluminum and aluminum alloys "
            "(NAPCS 38), total exports, Singapore destination. "
            "Coord 1.38.1.27.1.0.0.0.0.0. Resolved 2026-05-14."
        ),
    ),
}


def get_url(spec: StatcanSpec) -> str:
    """Human-readable StatCan table URL for .meta.json provenance."""
    return _table_url(spec.table_id)
