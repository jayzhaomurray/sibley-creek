"""Bank of Canada MPR projection vintages, October 2024 through January 2026.

Transcribed from the published Monetary Policy Reports (six issues). Each dict is
a point-in-time snapshot of the projection tables (contributions-to-growth table
with the potential-output memo, and the quarterly projection summary) plus the
output-gap statement from the Canadian-economy text and the post-decision target
overnight rate on the MPR date.

Conventions:
- Percent units exactly as printed in the MPR tables.
- Negative output_gap_range = excess supply.
- core_cpi_yoy is the "Core inflation" row = average of CPI-trim and CPI-median.
- Q4/Q4 rows (no gdp_qq_ann) carry the fourth-quarter-over-fourth-quarter memo
  values; gdp_q4q4 in the annual block is the same Q4/Q4 GDP growth.
- April 2025 and July 2025 were scenario reports (no single base-case projection);
  see per-dict notes for how the scenario tables were mapped.

April 2026 is intentionally absent (handled separately as the live vintage).
"""

VINTAGES = [
    # ------------------------------------------------------------------ #
    # October 2024 MPR
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2024-10-23",
        "projection_end_quarter": "2026Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.75, -0.75),
        "output_gap_quarter": "2024Q3",
        "current_overnight_rate": 3.75,
        "quarterly": [
            # Near-term quarterly (q/q annualized), 2024 Q1-Q4
            {"quarter": "2024Q1", "gdp_qq_ann": 1.8},
            {"quarter": "2024Q2", "gdp_qq_ann": 2.1},
            {"quarter": "2024Q3", "gdp_qq_ann": 1.5},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.3, "total_cpi_yoy": 2.1, "gdp_qq_ann": 2.0},
            # Q4/Q4 anchors
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.0, "gdp_q4q4": 2.3},
            {"quarter": "2026Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0, "gdp_q4q4": 2.3},
        ],
        "annual": [
            {"year": 2024, "potential_low": 2.1, "potential_high": 2.8, "gdp_q4q4": 1.8, "gdp_annual_avg": 1.2},
            {"year": 2025, "potential_low": 1.1, "potential_high": 2.4, "gdp_q4q4": 2.3, "gdp_annual_avg": 2.1},
            {"year": 2026, "potential_low": 0.9, "potential_high": 2.2, "gdp_q4q4": 2.3, "gdp_annual_avg": 2.3},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2024/10/mpr-2024-10-23.pdf",
        "notes": "Standard base-case projection. Table 1/Table 2 style. CPI annual 2025=2.2, 2026=2.0.",
    },
    # ------------------------------------------------------------------ #
    # January 2025 MPR
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2025-01-29",
        "projection_end_quarter": "2026Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.25, -0.25),
        "output_gap_quarter": "2024Q4",
        "current_overnight_rate": 3.00,
        "quarterly": [
            # Near-term quarterly (q/q annualized), 2024 Q2 - 2025 Q1
            {"quarter": "2024Q2", "gdp_qq_ann": 2.2},
            {"quarter": "2024Q3", "gdp_qq_ann": 1.0},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.6, "total_cpi_yoy": 1.9, "gdp_qq_ann": 1.8},
            {"quarter": "2025Q1", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.1, "gdp_qq_ann": 2.0},
            # Q4/Q4 anchors
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.4, "gdp_q4q4": 1.9},
            {"quarter": "2026Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "gdp_q4q4": 1.7},
        ],
        "annual": [
            {"year": 2024, "potential_low": 2.1, "potential_high": 2.8, "gdp_q4q4": 1.8, "gdp_annual_avg": 1.3},
            {"year": 2025, "potential_low": 1.1, "potential_high": 2.4, "gdp_q4q4": 1.9, "gdp_annual_avg": 1.8},
            {"year": 2026, "potential_low": 0.9, "potential_high": 2.2, "gdp_q4q4": 1.7, "gdp_annual_avg": 1.8},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2025/01/mpr-2025-01-29.pdf",
        "notes": "Standard base-case projection. Potential-output ranges unchanged from Oct 2024. "
                 "CPI annual 2025=2.3, 2026=2.1.",
    },
    # ------------------------------------------------------------------ #
    # April 2025 MPR  (two-scenario report, no base case)
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2025-04-16",
        "exclude": True,
        "exclude_reason": (
            "two-scenario Report with no base-case projection and no Q4/Q4 anchors; "
            "the hold-at-last-value rule on the truncated near-term profile produces "
            "an artifact path (terminal ~6%), not a usable rule-implied vintage"
        ),
        "projection_end_quarter": "2027Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.0, 0.0),
        "output_gap_quarter": "2025Q1",
        "current_overnight_rate": 2.75,
        "quarterly": [
            # Only near-term quarters published (Table 2), 2024Q3 - 2025Q2; Scenario 1.
            # No Q4/Q4 core/CPI/GDP anchors were published in this scenario report.
            {"quarter": "2024Q3", "core_cpi_yoy": 2.7, "total_cpi_yoy": 2.1, "gdp_qq_ann": 2.2},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.7, "total_cpi_yoy": 1.9, "gdp_qq_ann": 2.6},
            {"quarter": "2025Q1", "core_cpi_yoy": 2.9, "total_cpi_yoy": 2.4, "gdp_qq_ann": 1.8},
            {"quarter": "2025Q2", "core_cpi_yoy": 2.9, "total_cpi_yoy": 1.5, "gdp_qq_ann": 0.0},
        ],
        "annual": [
            # Potential output: point estimates per scenario (Table A-1). Range here spans
            # Scenario 2 (low) to Scenario 1 (high) for each year. gdp_q4q4 = annual-average
            # GDP (Scenario 1) because no Q4/Q4 GDP was published. core_cpi_yoy Q4 anchors
            # were not published; carried as None (see notes).
            {"year": 2025, "potential_low": 1.2, "potential_high": 1.8, "gdp_q4q4": 1.6, "gdp_annual_avg": 1.6,
             "core_cpi_yoy": None},
            {"year": 2026, "potential_low": 0.4, "potential_high": 1.3, "gdp_q4q4": 1.4, "gdp_annual_avg": 1.4,
             "core_cpi_yoy": None},
            {"year": 2027, "potential_low": 1.0, "potential_high": 1.4, "gdp_q4q4": 1.6, "gdp_annual_avg": 1.6,
             "core_cpi_yoy": None},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2025/04/mpr-2025-04-16.pdf",
        "notes": "SCENARIO REPORT: two illustrative scenarios instead of a base case. Annual GDP/CPI and "
                 "potential output mapped from Scenario 1 (most tariffs negotiated away); Scenario 2 used for "
                 "the potential-output low bound. Scenario 1 GDP avg 2025/26/27 = 1.6/1.4/1.6, CPI = 1.8/2.0/2.1; "
                 "Scenario 2 GDP avg 2025/26/27 = 0.8/-0.2/1.7 (partial), CPI = 2.0/2.7/2.3. "
                 "Potential output point estimates: S1 2025/26/27 = 1.8/1.3/1.4, S2 = 1.2/0.4/1.0. "
                 "No Q4/Q4 core, CPI, or GDP anchors published; gdp_q4q4 set to annual average as proxy; "
                 "annual core_cpi_yoy is None (unavailable). Neutral rate held at 2.25-3.25% (stated unchanged).",
    },
    # ------------------------------------------------------------------ #
    # July 2025 MPR  (single "current tariff scenario", no base case)
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2025-07-30",
        "projection_end_quarter": "2027Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.5, -0.5),
        "output_gap_quarter": "2025Q2",
        "current_overnight_rate": 2.75,
        "quarterly": [
            # Near-term quarterly (q/q annualized), 2025 Q1-Q4 (current tariff scenario)
            {"quarter": "2024Q4", "core_cpi_yoy": 2.6, "total_cpi_yoy": 1.9, "gdp_qq_ann": 2.1},
            {"quarter": "2025Q1", "core_cpi_yoy": 2.8, "total_cpi_yoy": 2.3, "gdp_qq_ann": 2.2},
            {"quarter": "2025Q2", "core_cpi_yoy": 3.1, "total_cpi_yoy": 1.7, "gdp_qq_ann": -1.5},
            {"quarter": "2025Q3", "core_cpi_yoy": 3.1, "total_cpi_yoy": 1.8, "gdp_qq_ann": 1.0},
            # Q4/Q4 anchors
            {"quarter": "2025Q4", "core_cpi_yoy": 3.1, "total_cpi_yoy": 1.9, "gdp_q4q4": 0.7},
            {"quarter": "2026Q4", "core_cpi_yoy": 2.4, "total_cpi_yoy": 2.1, "gdp_q4q4": 1.4},
            {"quarter": "2027Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 1.9, "gdp_q4q4": 2.1},
        ],
        "annual": [
            # No potential-output range table in this scenario report; ranges carried from
            # April 2025 (the latest reassessment). gdp_q4q4 from Table 3 Q4/Q4 figures.
            {"year": 2025, "potential_low": 1.2, "potential_high": 1.8, "gdp_q4q4": 0.7, "gdp_annual_avg": 1.3},
            {"year": 2026, "potential_low": 0.4, "potential_high": 1.3, "gdp_q4q4": 1.4, "gdp_annual_avg": 1.1},
            {"year": 2027, "potential_low": 1.0, "potential_high": 1.4, "gdp_q4q4": 2.1, "gdp_annual_avg": 1.8},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2025/07/mpr-2025-07-30.pdf",
        "notes": "SCENARIO REPORT: single 'current tariff scenario' instead of a base case (full Table 2/Table 3 "
                 "with Q4/Q4 anchors published). CPI annual 2025/26/27 = 1.9/2.0/2.0. No potential-output range "
                 "table; potential ranges carried from April 2025. Output gap widened to -1.5%/-0.5% in 2025Q2 "
                 "from -1.0%/0% in 2025Q1.",
    },
    # ------------------------------------------------------------------ #
    # October 2025 MPR
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2025-10-29",
        "projection_end_quarter": "2027Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.5, -0.5),
        "output_gap_quarter": "2025Q3",
        "current_overnight_rate": 2.25,
        "quarterly": [
            # Near-term quarterly (q/q annualized), 2025 Q1-Q4
            {"quarter": "2025Q1", "gdp_qq_ann": 2.0},
            {"quarter": "2025Q2", "core_cpi_yoy": 3.1, "total_cpi_yoy": 1.7, "gdp_qq_ann": -1.6},
            {"quarter": "2025Q3", "core_cpi_yoy": 3.2, "total_cpi_yoy": 2.0, "gdp_qq_ann": 0.5},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.9, "total_cpi_yoy": 2.0, "gdp_qq_ann": 1.0},
            # Q4/Q4 anchors
            {"quarter": "2026Q4", "core_cpi_yoy": 2.3, "total_cpi_yoy": 2.2, "gdp_q4q4": 1.6},
            {"quarter": "2027Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "gdp_q4q4": 1.6},
        ],
        "annual": [
            # Potential-output ranges reassessed this Report (carried into Jan 2026 parentheticals).
            {"year": 2025, "potential_low": 1.2, "potential_high": 2.0, "gdp_q4q4": 0.5, "gdp_annual_avg": 1.2},
            {"year": 2026, "potential_low": 0.4, "potential_high": 1.4, "gdp_q4q4": 1.6, "gdp_annual_avg": 1.1},
            {"year": 2027, "potential_low": 1.3, "potential_high": 2.3, "gdp_q4q4": 1.6, "gdp_annual_avg": 1.6},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2025/10/mpr-2025-10-29.pdf",
        "notes": "Standard base-case projection resumes (Table 3/Table 4 style). 2025Q4 core Q4/Q4 = 2.9. "
                 "CPI annual 2025/26/27 = 2.0/2.1/2.1. Output gap broadly unchanged within -1.5%/-0.5% range, "
                 "referencing Q3 (and Q2) 2025.",
    },
    # ------------------------------------------------------------------ #
    # January 2026 MPR
    # ------------------------------------------------------------------ #
    {
        "mpr_date": "2026-01-28",
        "projection_end_quarter": "2027Q4",
        "neutral_range": (2.25, 3.25),
        "output_gap_range": (-1.5, -0.5),
        "output_gap_quarter": "2025Q4",
        "current_overnight_rate": 2.25,
        "quarterly": [
            # Near-term quarterly (q/q annualized), 2025 Q2-Q4 + 2026 Q1
            {"quarter": "2025Q2", "core_cpi_yoy": 3.1, "total_cpi_yoy": 1.7, "gdp_qq_ann": -1.8},
            {"quarter": "2025Q3", "core_cpi_yoy": 3.1, "total_cpi_yoy": 2.0, "gdp_qq_ann": 2.6},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.9, "total_cpi_yoy": 2.2, "gdp_qq_ann": 0.0},
            {"quarter": "2026Q1", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.0, "gdp_qq_ann": 1.8},
            # Q4/Q4 anchors
            {"quarter": "2026Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 1.9, "gdp_q4q4": 1.4},
            {"quarter": "2027Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "gdp_q4q4": 1.7},
        ],
        "annual": [
            {"year": 2025, "potential_low": 1.9, "potential_high": 2.7, "gdp_q4q4": 0.7, "gdp_annual_avg": 1.7},
            {"year": 2026, "potential_low": 0.6, "potential_high": 1.6, "gdp_q4q4": 1.4, "gdp_annual_avg": 1.1},
            {"year": 2027, "potential_low": 0.7, "potential_high": 1.7, "gdp_q4q4": 1.7, "gdp_annual_avg": 1.5},
        ],
        "core_concept": "trim_median_avg",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2026/01/mpr-2026-01-28.pdf",
        "notes": "Standard base-case projection (Table 2/Table 3 style). CPI annual 2025/26/27 = 2.1/2.0/2.1. "
                 "Consistent with April 2026 parentheticals: 2026 GDP avg 1.1, CPI 2.0, core Q4/Q4 2026 = 2.1, "
                 "potential 2026 0.6-1.6, 2027 0.7-1.7. Output gap estimate -1.5%/-0.5% for 2025Q4, unchanged "
                 "from October Report.",
    },
]
