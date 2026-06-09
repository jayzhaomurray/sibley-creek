"""Bank of Canada MPR projection vintages: Jan 2023 - Jul 2024 (batch).

Transcribed from the BoC Monetary Policy Report archive
(https://www.bankofcanada.ca/publications/mpr/). Each dict captures the
projection summary tables (Table 2 contributions/memo + Table 3 quarterly
summary) and the Canadian-economy output-gap statement for one MPR.

Conventions (shared schema, see pipeline/shadow_rate/inputs.py):
- Percent units as printed (2.5 == 2.5%). Negative output gap = excess supply.
- ``quarterly`` carries near-term direct quarters (where the MPR prints a
  q/q annualized GDP value) plus the Q4/Q4 anchor rows (fourth-quarter-over-
  fourth-quarter memo values) at each year's Q4.
- ``annual`` carries one row per projection year: potential-output range,
  Q4/Q4 GDP, and annual-average GDP growth (Table 2 GDP line).

Core-inflation note: BoC's Table 3 did NOT print a "Core inflation" row until
the July 2024 MPR. For the six earlier vintages (Jan 2023 - Apr 2024) the
quarterly summary table reports only total CPI, so ``core_cpi_yoy`` is filled
with the total-CPI value and ``total_cpi_fallback`` is set True on those rows.
Only the July 2024 vintage has genuine core (CPI-trim/CPI-median average) rows.

Potential-output note: the BoC reassesses potential output / the neutral rate
in the April MPR each year. Non-April vintages carry forward the prevailing
ranges; the Table 2 "Range for potential output" memo line is transcribed
as-printed for each vintage regardless (the BoC reprints the current ranges
every Report), so each ``annual`` row uses that vintage's own printed range.
"""

VINTAGES = [
    # ----------------------------------------------------------------- #
    # July 2024 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2024-07-24",
        "projection_end_quarter": "2026Q4",
        "neutral_range": (2.25, 3.25),  # unchanged from Apr 2024 reassessment
        "output_gap_range": (-1.75, -0.75),  # "between -0.75% and -1.75%"
        "output_gap_quarter": "2024Q2",
        "current_overnight_rate": 4.50,  # cut 25bp to 4.50% on 2024-07-24
        "quarterly": [
            # Table 3: 2023Q4 + 2024 Q1/Q2/Q3 direct, then Q4/Q4 anchors.
            {"quarter": "2023Q4", "core_cpi_yoy": 3.4, "total_cpi_yoy": 3.3},
            {"quarter": "2024Q1", "core_cpi_yoy": 3.1, "total_cpi_yoy": 2.8, "gdp_qq_ann": 1.7},
            {"quarter": "2024Q2", "core_cpi_yoy": 2.7, "total_cpi_yoy": 2.7, "gdp_qq_ann": 1.5},
            {"quarter": "2024Q3", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.3, "gdp_qq_ann": 2.8},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.4, "total_cpi_yoy": 2.4},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0},
            {"quarter": "2026Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0},
        ],
        "annual": [
            # Q4/Q4 GDP from Table 3 real-GDP-yoy row at Q4; annual avg from Table 2 GDP line.
            {"year": 2024, "potential_low": 2.1, "potential_high": 2.8, "gdp_q4q4": 2.0, "gdp_annual_avg": 1.2},
            {"year": 2025, "potential_low": 1.1, "potential_high": 2.4, "gdp_q4q4": 2.1, "gdp_annual_avg": 2.1},
            {"year": 2026, "potential_low": 0.9, "potential_high": 2.2, "gdp_q4q4": 2.5, "gdp_annual_avg": 2.4},
        ],
        "core_concept": "trim_median_avg",  # footnote: avg of CPI-trim and CPI-median
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2024/07/mpr-2024-07-24.pdf",
        "notes": "First vintage in this batch with a genuine Core-inflation row in Table 3. "
                 "Output gap stated for 2024Q2 (current quarter), not a near-term forecast quarter.",
    },
    # ----------------------------------------------------------------- #
    # April 2024 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2024-04-10",
        "projection_end_quarter": "2026Q4",
        "neutral_range": (2.25, 3.25),  # raised 25bp from Jan 2024 (Apr 2024 reassessment)
        "output_gap_range": (-1.5, -0.5),  # "between -0.5% and -1.5%"
        "output_gap_quarter": "2024Q1",
        "current_overnight_rate": 5.00,  # held at 5.00% on 2024-04-10
        "quarterly": [
            # Table 3: 2023 Q3/Q4 + 2024 Q1/Q2 direct, then Q4/Q4 anchors. No core row.
            {"quarter": "2023Q3", "core_cpi_yoy": 3.7, "total_cpi_yoy": 3.7, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 3.3, "total_cpi_yoy": 3.3, "total_cpi_fallback": True},
            {"quarter": "2024Q1", "core_cpi_yoy": 2.8, "total_cpi_yoy": 2.8, "gdp_qq_ann": 2.8, "total_cpi_fallback": True},
            {"quarter": "2024Q2", "core_cpi_yoy": 2.9, "total_cpi_yoy": 2.9, "gdp_qq_ann": 1.5, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.2, "total_cpi_yoy": 2.2, "total_cpi_fallback": True},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
            {"quarter": "2026Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
        ],
        "annual": [
            {"year": 2024, "potential_low": 2.1, "potential_high": 2.8, "gdp_q4q4": 2.1, "gdp_annual_avg": 1.5},
            {"year": 2025, "potential_low": 1.1, "potential_high": 2.4, "gdp_q4q4": 2.2, "gdp_annual_avg": 2.2},
            {"year": 2026, "potential_low": 0.9, "potential_high": 2.2, "gdp_q4q4": 1.9, "gdp_annual_avg": 1.9},
        ],
        "core_concept": "total_cpi_fallback",  # Table 3 has no core row; total CPI used
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2024/04/mpr-2024-04-10.pdf",
        "notes": "April reassessment: nominal neutral range raised to 2.25-3.25 (from 2.0-3.0). "
                 "Table 3 prints only total CPI (no core row) -> core_cpi_yoy is total-CPI fallback. "
                 "Output gap stated for 2024Q1 (current quarter).",
    },
    # ----------------------------------------------------------------- #
    # January 2024 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2024-01-24",
        "projection_end_quarter": "2025Q4",
        "neutral_range": (2.0, 3.0),  # prior to Apr 2024 reassessment
        "output_gap_range": (-1.25, -0.25),  # "between -0.25% and -1.25%"
        "output_gap_quarter": "2023Q4",
        "current_overnight_rate": 5.00,  # held at 5.00% on 2024-01-24
        "quarterly": [
            # Table 3: 2023 Q2/Q3/Q4 + 2024Q1 direct, then Q4/Q4 anchors. No core row.
            {"quarter": "2023Q2", "core_cpi_yoy": 3.6, "total_cpi_yoy": 3.6, "gdp_qq_ann": 1.4, "total_cpi_fallback": True},
            {"quarter": "2023Q3", "core_cpi_yoy": 3.7, "total_cpi_yoy": 3.7, "gdp_qq_ann": -1.1, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 3.3, "total_cpi_yoy": 3.3, "gdp_qq_ann": 0.0, "total_cpi_fallback": True},
            {"quarter": "2024Q1", "core_cpi_yoy": 3.2, "total_cpi_yoy": 3.2, "gdp_qq_ann": 0.5, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.4, "total_cpi_yoy": 2.4, "total_cpi_fallback": True},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
        ],
        "annual": [
            # Table 2 columns 2022/2023/2024/2025; carry projection years 2023-2025.
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.2, "gdp_q4q4": 0.7, "gdp_annual_avg": 1.0},
            {"year": 2024, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 1.6, "gdp_annual_avg": 0.8},
            {"year": 2025, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 2.7, "gdp_annual_avg": 2.4},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2024/01/mpr-2024-01-24.pdf",
        "notes": "Table 3 prints only total CPI (no core row) -> core_cpi_yoy is total-CPI fallback. "
                 "Output gap stated for 2023Q4 (current quarter). Neutral range 2.0-3.0 (pre-Apr-2024 reassessment).",
    },
    # ----------------------------------------------------------------- #
    # October 2023 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2023-10-25",
        "projection_end_quarter": "2025Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (-0.75, 0.25),  # "between -0.75% and 0.25%"
        "output_gap_quarter": "2023Q3",
        "current_overnight_rate": 5.00,  # held at 5.00% on 2023-10-25
        "quarterly": [
            # Table 3: 2023 Q1/Q2/Q3/Q4 direct (Q3/Q4 have GDP), then Q4/Q4 anchors. No core row.
            {"quarter": "2023Q1", "core_cpi_yoy": 5.2, "total_cpi_yoy": 5.2, "gdp_qq_ann": 2.6, "total_cpi_fallback": True},
            {"quarter": "2023Q2", "core_cpi_yoy": 3.6, "total_cpi_yoy": 3.6, "gdp_qq_ann": -0.2, "total_cpi_fallback": True},
            {"quarter": "2023Q3", "core_cpi_yoy": 3.7, "total_cpi_yoy": 3.7, "gdp_qq_ann": 0.8, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 3.3, "total_cpi_yoy": 3.3, "gdp_qq_ann": 0.8, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.5, "total_cpi_fallback": True},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
        ],
        "annual": [
            # Table 2 columns 2022/2023/2024/2025; carry projection years 2023-2025.
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.2, "gdp_q4q4": 1.0, "gdp_annual_avg": 1.2},
            {"year": 2024, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 1.3, "gdp_annual_avg": 0.9},
            {"year": 2025, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 3.0, "gdp_annual_avg": 2.5},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2023/10/mpr-2023-10-25.pdf",
        "notes": "Table 3 prints only total CPI (no core row) -> core_cpi_yoy is total-CPI fallback. "
                 "Output gap stated for 2023Q3 (current quarter); economy near balance (gap straddles zero).",
    },
    # ----------------------------------------------------------------- #
    # July 2023 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2023-07-12",
        "projection_end_quarter": "2025Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (0.0, 1.0),  # "between 0% and 1%" (excess demand)
        "output_gap_quarter": "2023Q2",
        "current_overnight_rate": 5.00,  # hiked 25bp to 5.00% on 2023-07-12
        "quarterly": [
            # Table 3: 2022Q4 + 2023 Q1/Q2/Q3 direct (Q2/Q3 have GDP), then Q4/Q4 anchors. No core row.
            {"quarter": "2022Q4", "core_cpi_yoy": 6.7, "total_cpi_yoy": 6.7, "gdp_qq_ann": -0.1, "total_cpi_fallback": True},
            {"quarter": "2023Q1", "core_cpi_yoy": 5.2, "total_cpi_yoy": 5.2, "gdp_qq_ann": 3.1, "total_cpi_fallback": True},
            {"quarter": "2023Q2", "core_cpi_yoy": 3.6, "total_cpi_yoy": 3.6, "gdp_qq_ann": 1.5, "total_cpi_fallback": True},
            {"quarter": "2023Q3", "core_cpi_yoy": 3.3, "total_cpi_yoy": 3.3, "gdp_qq_ann": 1.5, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.9, "total_cpi_yoy": 2.9, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.2, "total_cpi_yoy": 2.2, "total_cpi_fallback": True},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
        ],
        "annual": [
            # Table 2 columns 2022/2023/2024/2025; carry projection years 2023-2025.
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.2, "gdp_q4q4": 1.8, "gdp_annual_avg": 1.8},
            {"year": 2024, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 1.5, "gdp_annual_avg": 1.2},
            {"year": 2025, "potential_low": 1.2, "potential_high": 2.8, "gdp_q4q4": 2.5, "gdp_annual_avg": 2.4},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2023/07/mpr-2023-07-12.pdf",
        "notes": "Table 3 prints only total CPI (no core row) -> core_cpi_yoy is total-CPI fallback. "
                 "Output gap stated for 2023Q2 (current quarter), still modest excess demand (positive gap).",
    },
    # ----------------------------------------------------------------- #
    # April 2023 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2023-04-12",
        "projection_end_quarter": "2025Q4",
        "neutral_range": (2.0, 3.0),  # Apr 2023 reassessment kept range at 2.0-3.0
        "output_gap_range": (0.25, 1.25),  # "between 0.25% and 1.25%" (excess demand)
        "output_gap_quarter": "2023Q1",
        "current_overnight_rate": 4.50,  # held at 4.50% on 2023-04-12
        "quarterly": [
            # Table 3: 2022 Q3/Q4 + 2023 Q1/Q2 direct (Q1/Q2 have GDP), then Q4/Q4 anchors. No core row.
            {"quarter": "2022Q3", "core_cpi_yoy": 7.2, "total_cpi_yoy": 7.2, "gdp_qq_ann": 2.3, "total_cpi_fallback": True},
            {"quarter": "2022Q4", "core_cpi_yoy": 6.7, "total_cpi_yoy": 6.7, "gdp_qq_ann": 0.0, "total_cpi_fallback": True},
            {"quarter": "2023Q1", "core_cpi_yoy": 5.2, "total_cpi_yoy": 5.2, "gdp_qq_ann": 2.3, "total_cpi_fallback": True},
            {"quarter": "2023Q2", "core_cpi_yoy": 3.3, "total_cpi_yoy": 3.3, "gdp_qq_ann": 1.0, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.5, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1, "total_cpi_fallback": True},
            {"quarter": "2025Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0, "total_cpi_fallback": True},
        ],
        "annual": [
            # Table 2 columns 2022/2023/2024/2025; carry projection years 2023-2025.
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.2, "gdp_q4q4": 1.1, "gdp_annual_avg": 1.4},
            {"year": 2024, "potential_low": 1.0, "potential_high": 3.2, "gdp_q4q4": 1.9, "gdp_annual_avg": 1.3},
            {"year": 2025, "potential_low": 1.2, "potential_high": 2.8, "gdp_q4q4": 2.6, "gdp_annual_avg": 2.5},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2023/04/mpr-2023-04-12.pdf",
        "notes": "April reassessment kept nominal neutral range at 2.0-3.0. "
                 "Table 3 prints only total CPI (no core row) -> core_cpi_yoy is total-CPI fallback. "
                 "Output gap stated for 2023Q1 (current quarter), excess demand (positive gap).",
    },
    # ----------------------------------------------------------------- #
    # January 2023 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2023-01-25",
        "projection_end_quarter": "2024Q4",
        "neutral_range": (2.0, 3.0),  # last reassessed April 2022
        "output_gap_range": (0.50, 1.50),  # "between 0.50% and 1.50%" (excess demand)
        "output_gap_quarter": "2022Q4",
        "current_overnight_rate": 4.50,  # hiked 25bp to 4.50% on 2023-01-25
        "quarterly": [
            # Table 3: 2022 Q2/Q3/Q4 + 2023Q1 direct (Q4 + 2023Q1 have GDP), then Q4/Q4 anchors. No core row.
            {"quarter": "2022Q2", "core_cpi_yoy": 7.5, "total_cpi_yoy": 7.5, "gdp_qq_ann": 3.2, "total_cpi_fallback": True},
            {"quarter": "2022Q3", "core_cpi_yoy": 7.2, "total_cpi_yoy": 7.2, "gdp_qq_ann": 2.9, "total_cpi_fallback": True},
            {"quarter": "2022Q4", "core_cpi_yoy": 6.7, "total_cpi_yoy": 6.7, "gdp_qq_ann": 1.3, "total_cpi_fallback": True},
            {"quarter": "2023Q1", "core_cpi_yoy": 5.4, "total_cpi_yoy": 5.4, "gdp_qq_ann": 0.5, "total_cpi_fallback": True},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.6, "total_cpi_yoy": 2.6, "total_cpi_fallback": True},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0, "total_cpi_fallback": True},
        ],
        "annual": [
            # 2022 row carried from the Oct-2022 vintage for anchor-year coverage only
            # (gap anchor sits at 2022Q4; the level is given, so 2022 potential never
            # enters the roll-forward arithmetic — first step uses 2023 values).
            {"year": 2022, "potential_low": 1.3, "potential_high": 2.3, "gdp_q4q4": 1.3, "gdp_annual_avg": 3.6},
            # Table 2 columns 2021/2022/2023/2024; carry projection years 2023-2024.
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.3, "gdp_q4q4": 0.5, "gdp_annual_avg": 1.0},
            {"year": 2024, "potential_low": 1.4, "potential_high": 3.5, "gdp_q4q4": 2.4, "gdp_annual_avg": 1.8},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/wp-content/uploads/2023/01/mpr-2023-01-25.pdf",
        "notes": "Shortest horizon in batch: projection runs only to 2024Q4. Neutral range 2.0-3.0 "
                 "(last reassessed April 2022). Table 3 prints only total CPI (no core row) -> "
                 "core_cpi_yoy is total-CPI fallback. Output gap stated for 2022Q4 (current quarter).",
    },
]
