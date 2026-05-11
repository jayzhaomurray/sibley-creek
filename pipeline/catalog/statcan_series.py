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

    # ----- Inflation (Section 4.2) ----------------------------------------
    "cpi_all_items":     StatcanSpec("cpi_all_items", 41690914, "18-10-0006-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=True),
    "cpi_all_items_nsa": StatcanSpec("cpi_all_items_nsa", 41690973, "18-10-0004-01",
                                     "Index, 2002=100", "monthly", "inflation", sa=False),
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
                                            notes="Mortgage interest cost component; load-bearing for shelter decomposition."),

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
                                          notes="Employed persons, scaled thousands -> millions. Numerator for per-capita employment growth (Pillar E)."),
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
                                          notes="JVWS publishes NSA only; chart-side 3M MA is the editorial convention."),
    "job_vacancy_level":      StatcanSpec("job_vacancy_level", 1212389364, "14-10-0371-01",
                                          "Millions", "monthly", "labour", scale=1e-6, sa=False),
    # Aggregate hours (Table 14-10-0289). Resolved 2026-05-11 (research/wave2_vector_resolutions.md):
    # Canada; Total actual hours worked, all industries; Estimate (coord 1.1.1.0.0.0.0.0.0.0).
    "aggregate_hours":        StatcanSpec("aggregate_hours", 4391505, "14-10-0289-01",
                                          "Thousands of hours", "monthly", "labour", sa=True,
                                          notes=(
                                              "Canada; total actual hours worked, all industries; Estimate; SA monthly. "
                                              "Cube coord 1.1.1.0.0.0.0.0.0.0; UOM 152 (thousands of hours), decimals 1. "
                                              "Resolved 2026-05-11 via getCubeMetadata on 14-10-0289."
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
    # By-partner: China, UK, Japan, Mexico, Germany. Table 12-10-0119-01, country-coded vectors.
    # Vectors are probe-pending: WDS country-code dimension lookup would resolve these; in absence
    # of getCubeMetadata access, registered as best-guess sequential vectors and marked probe-pending.
    "trade_exports_china":   StatcanSpec("trade_exports_china", 1001135501, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="China exports (probe-pending)."),
    "trade_imports_china":   StatcanSpec("trade_imports_china", 1001135502, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="China imports (probe-pending)."),
    "trade_exports_uk":      StatcanSpec("trade_exports_uk", 1001135503, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="UK exports (probe-pending)."),
    "trade_imports_uk":      StatcanSpec("trade_imports_uk", 1001135504, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="UK imports (probe-pending)."),
    "trade_exports_japan":   StatcanSpec("trade_exports_japan", 1001135505, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Japan exports (probe-pending)."),
    "trade_imports_japan":   StatcanSpec("trade_imports_japan", 1001135506, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Japan imports (probe-pending)."),
    "trade_exports_mexico":  StatcanSpec("trade_exports_mexico", 1001135507, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Mexico exports (probe-pending)."),
    "trade_imports_mexico":  StatcanSpec("trade_imports_mexico", 1001135508, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Mexico imports (probe-pending)."),
    "trade_exports_germany": StatcanSpec("trade_exports_germany", 1001135509, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Germany exports (probe-pending)."),
    "trade_imports_germany": StatcanSpec("trade_imports_germany", 1001135510, "12-10-0119-01",
                                         "C$ millions", "monthly", "trade", sa=True, notes="Germany imports (probe-pending)."),
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
    # Terms of trade (Table 36-10-0103-01) — quarterly.
    "terms_of_trade": StatcanSpec("terms_of_trade", 62305749, "36-10-0103-01", "Index, 2017=100", "quarterly", "trade", sa=True,
                                  notes="Terms-of-trade index, quarterly (probe-pending)."),
    # Energy supply and disposition (Table 25-10-0044-01) — monthly.
    "energy_supply_disposition": StatcanSpec("energy_supply_disposition", 5000044, "25-10-0044-01",
                                              "Cubic metres", "monthly", "trade", sa=False,
                                              notes="Energy supply and disposition headline series (probe-pending)."),
    # FDI by industry (Table 36-10-0008-01) — quarterly.
    "fdi_total": StatcanSpec("fdi_total", 62800001, "36-10-0008-01", "C$ millions", "quarterly", "trade", sa=True,
                              notes="FDI total inflows by industry headline (probe-pending)."),
}


def get_url(spec: StatcanSpec) -> str:
    """Human-readable StatCan table URL for .meta.json provenance."""
    return _table_url(spec.table_id)
