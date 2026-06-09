"""MPR projection vintages — batch 2021-2022 (six MPRs).

Transcribed from the Bank of Canada Monetary Policy Reports:
July 2021, October 2021, January 2022, April 2022, July 2022, October 2022.

Source tables per MPR (the projection summary tables are rasterized in the
HTML pages, so all figures below were read from the official PDFs at
wp-content/uploads/<yyyy>/<mm>/<file>.pdf):
  - Table 3 "Summary of the quarterly projection for Canada"
      -> near-term quarterly CPI (yoy) + real GDP (qoq annualized),
         plus fourth-quarter-over-fourth-quarter (Q4/Q4) CPI and GDP anchors.
  - Table 2 "Contributions to average annual real GDP growth"
      -> annual-average real GDP growth, annual CPI, and the
         "Range for potential output" memo row (low-high per year).
  - "Key inputs to the projection" box + Canadian-economy text
      -> output-gap range/quarter and the nominal neutral-rate range.

Units: percent as printed (2.5 == 2.5%). Negative output gap == excess supply.

Core concept: the 2021-22 MPR projection summary tables publish only TOTAL CPI
(no CPI-trim / CPI-median forecast rows). Every vintage therefore uses total
CPI for both core_cpi_yoy and total_cpi_yoy and is flagged "total_cpi_fallback".

Neutral range provenance: 1.75-2.75 was set in the April 2021 reassessment and
carried by the Jul 2021, Oct 2021 and Jan 2022 vintages. The April 2022 MPR
reassessed it 0.25pp higher to 2.0-3.0; the Apr/Jul/Oct 2022 vintages carry that.

Overnight-rate seeds (target ON the MPR/decision date, post-decision), verified
against data/processed/overnight_rate_target.csv and the Bank's decision pages:
  Jul 14 2021: 0.25 (held at ELB)   Apr 13 2022: 1.00 (+50bp)
  Oct 27 2021: 0.25 (held at ELB)   Jul 13 2022: 2.50 (+100bp)
  Jan 26 2022: 0.25 (held at ELB)   Oct 26 2022: 3.75 (+50bp)
"""

VINTAGES = [
    # ----------------------------------------------------------------- #
    # October 2022 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2022-10-26",
        "projection_end_quarter": "2024Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (0.25, 1.25),
        "output_gap_quarter": "2022Q3",
        "current_overnight_rate": 3.75,
        "quarterly": [
            # near-term quarterly rows (Table 3, 2022 columns)
            {"quarter": "2022Q1", "core_cpi_yoy": 5.8, "total_cpi_yoy": 5.8, "gdp_qq_ann": 3.1},
            {"quarter": "2022Q2", "core_cpi_yoy": 7.5, "total_cpi_yoy": 7.5, "gdp_qq_ann": 3.3},
            {"quarter": "2022Q3", "core_cpi_yoy": 7.2, "total_cpi_yoy": 7.2, "gdp_qq_ann": 1.5},
            # Q4/Q4 anchor rows (Table 3 right block)
            {"quarter": "2022Q4", "core_cpi_yoy": 7.1, "total_cpi_yoy": 7.1, "gdp_qq_ann": 0.5},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.8, "total_cpi_yoy": 2.8},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0},
        ],
        "annual": [
            # potential_low/high from Table 2 "Range for potential output";
            # gdp_q4q4 from Table 3 GDP yoy Q4/Q4; gdp_annual_avg from Table 2 GDP.
            {"year": 2022, "potential_low": 0.5, "potential_high": 2.0, "gdp_q4q4": 2.1, "gdp_annual_avg": 3.3},
            {"year": 2023, "potential_low": 1.4, "potential_high": 3.3, "gdp_q4q4": 1.0, "gdp_annual_avg": 0.9},
            {"year": 2024, "potential_low": 1.4, "potential_high": 3.5, "gdp_q4q4": 2.3, "gdp_annual_avg": 2.0},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2022/10/mpr-2022-10-26/",
        "notes": (
            "PDF: wp-content/uploads/2022/10/mpr-2022-10-26.pdf. Output gap 'between "
            "0.25% and 1.25% in the third quarter of 2022'. Neutral 2-3% (reassessed Apr 2022). "
            "With this Report the Bank ended the supply/potential-output distinction; the "
            "potential-output range now also reflects supply. Tables publish total CPI only "
            "(no trim/median rows). GDP coverage via Q4/Q4 anchors."
        ),
    },
    # ----------------------------------------------------------------- #
    # July 2022 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2022-07-13",
        "projection_end_quarter": "2024Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (0.5, 1.5),
        "output_gap_quarter": "2022Q2",
        "current_overnight_rate": 2.50,
        "quarterly": [
            {"quarter": "2021Q4", "core_cpi_yoy": 4.7, "total_cpi_yoy": 4.7, "gdp_qq_ann": 6.6},
            {"quarter": "2022Q1", "core_cpi_yoy": 5.8, "total_cpi_yoy": 5.8, "gdp_qq_ann": 3.1},
            {"quarter": "2022Q2", "core_cpi_yoy": 7.6, "total_cpi_yoy": 7.6, "gdp_qq_ann": 4.0},
            {"quarter": "2022Q3", "core_cpi_yoy": 8.0, "total_cpi_yoy": 8.0, "gdp_qq_ann": 2.0},
            # Q4/Q4 anchors
            {"quarter": "2022Q4", "core_cpi_yoy": 7.5, "total_cpi_yoy": 7.5},
            {"quarter": "2023Q4", "core_cpi_yoy": 3.2, "total_cpi_yoy": 3.2},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0},
        ],
        "annual": [
            {"year": 2022, "potential_low": 0.5, "potential_high": 2.0, "gdp_q4q4": 2.6, "gdp_annual_avg": 3.5},
            {"year": 2023, "potential_low": 1.8, "potential_high": 3.3, "gdp_q4q4": 1.8, "gdp_annual_avg": 1.8},
            {"year": 2024, "potential_low": 2.0, "potential_high": 3.5, "gdp_q4q4": 2.7, "gdp_annual_avg": 2.4},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2022/07/mpr-2022-07-13/",
        "notes": (
            "PDF: wp-content/uploads/2022/07/mpr-2022-07-13.pdf. Output gap 'between 0.5% and "
            "1.5% in the second quarter'. Neutral 2-3% (reassessed Apr 2022). Potential-output "
            "range is the Table 2 'including temporary factors' memo row. Tables publish total "
            "CPI only. GDP coverage via Q4/Q4 anchors. 2021Q4 quarterly row carried for context."
        ),
    },
    # ----------------------------------------------------------------- #
    # April 2022 MPR  (annual reassessment of potential output + neutral rate)
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2022-04-13",
        "projection_end_quarter": "2024Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (-0.25, 0.75),
        "output_gap_quarter": "2022Q1",
        "current_overnight_rate": 1.00,
        "quarterly": [
            {"quarter": "2021Q3", "core_cpi_yoy": 4.1, "total_cpi_yoy": 4.1, "gdp_qq_ann": 5.5},
            {"quarter": "2021Q4", "core_cpi_yoy": 4.7, "total_cpi_yoy": 4.7, "gdp_qq_ann": 6.7},
            {"quarter": "2022Q1", "core_cpi_yoy": 5.6, "total_cpi_yoy": 5.6, "gdp_qq_ann": 3.0},
            {"quarter": "2022Q2", "core_cpi_yoy": 5.8, "total_cpi_yoy": 5.8, "gdp_qq_ann": 6.0},
            # Q4/Q4 anchors
            {"quarter": "2022Q4", "core_cpi_yoy": 4.5, "total_cpi_yoy": 4.5},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.4, "total_cpi_yoy": 2.4},
            {"quarter": "2024Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1},
        ],
        "annual": [
            {"year": 2022, "potential_low": 1.3, "potential_high": 2.3, "gdp_q4q4": 3.8, "gdp_annual_avg": 4.2},
            {"year": 2023, "potential_low": 2.9, "potential_high": 3.9, "gdp_q4q4": 2.9, "gdp_annual_avg": 3.2},
            {"year": 2024, "potential_low": 2.3, "potential_high": 2.9, "gdp_q4q4": 1.7, "gdp_annual_avg": 2.2},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2022/04/mpr-2022-04-13/",
        "notes": (
            "PDF: wp-content/uploads/2022/04/mpr-2022-04-13.pdf. ANNUAL REASSESSMENT vintage: "
            "neutral nominal rate revised UP 0.25pp to 2-3% (from the 1.75-2.75 set in Apr 2021); "
            "potential output also reassessed. Output gap 'between -0.25% and 0.75% in the first "
            "quarter', up from -0.75% to 0.25% in 2021Q4. Potential-output range is the Table 2 "
            "'including temporary factors' memo row. Tables publish total CPI only. "
            "GDP coverage via Q4/Q4 anchors."
        ),
    },
    # ----------------------------------------------------------------- #
    # January 2022 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2022-01-26",
        "projection_end_quarter": "2023Q4",
        "neutral_range": (1.75, 2.75),
        "output_gap_range": (-0.75, 0.25),
        "output_gap_quarter": "2021Q4",
        "current_overnight_rate": 0.25,
        "quarterly": [
            {"quarter": "2021Q2", "core_cpi_yoy": 3.4, "total_cpi_yoy": 3.4, "gdp_qq_ann": -3.2},
            {"quarter": "2021Q3", "core_cpi_yoy": 4.1, "total_cpi_yoy": 4.1, "gdp_qq_ann": 5.4},
            {"quarter": "2021Q4", "core_cpi_yoy": 4.7, "total_cpi_yoy": 4.7, "gdp_qq_ann": 5.8},
            {"quarter": "2022Q1", "core_cpi_yoy": 5.1, "total_cpi_yoy": 5.1, "gdp_qq_ann": 2.0},
            # Q4/Q4 anchors
            {"quarter": "2022Q4", "core_cpi_yoy": 3.0, "total_cpi_yoy": 3.0},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.2, "total_cpi_yoy": 2.2},
        ],
        "annual": [
            # 2021 row carried from the Oct-2021 vintage for anchor-year coverage only
            # (gap anchor sits at 2021Q4; the level is given, so 2021 potential never
            # enters the roll-forward arithmetic — first step uses 2022 values).
            {"year": 2021, "potential_low": 0.8, "potential_high": 2.2, "gdp_q4q4": 3.4, "gdp_annual_avg": 4.6},
            {"year": 2022, "potential_low": 0.4, "potential_high": 2.2, "gdp_q4q4": 4.2, "gdp_annual_avg": 4.0},
            {"year": 2023, "potential_low": 1.0, "potential_high": 3.0, "gdp_q4q4": 2.7, "gdp_annual_avg": 3.5},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2022/01/mpr-2022-01-26/",
        "notes": (
            "PDF: wp-content/uploads/2022/01/mpr-2022-01-26.pdf. Held at 0.25% ELB (removed "
            "exceptional forward guidance). Neutral 1.75-2.75 (carried from Apr 2021 reassessment). "
            "Output gap 'between -0.75% and 0.25% in the fourth quarter of 2021'. Projection ends "
            "2023Q4. Potential-output range from Table 2 memo row. Tables publish total CPI only. "
            "GDP coverage via Q4/Q4 anchors."
        ),
    },
    # ----------------------------------------------------------------- #
    # October 2021 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2021-10-27",
        "projection_end_quarter": "2023Q4",
        "neutral_range": (1.75, 2.75),
        "output_gap_range": (-2.25, -1.25),
        "output_gap_quarter": "2021Q3",
        "current_overnight_rate": 0.25,
        "quarterly": [
            {"quarter": "2021Q1", "core_cpi_yoy": 1.5, "total_cpi_yoy": 1.5, "gdp_qq_ann": 5.5},
            {"quarter": "2021Q2", "core_cpi_yoy": 3.4, "total_cpi_yoy": 3.4, "gdp_qq_ann": -1.1},
            {"quarter": "2021Q3", "core_cpi_yoy": 4.1, "total_cpi_yoy": 4.1, "gdp_qq_ann": 5.5},
            {"quarter": "2021Q4", "core_cpi_yoy": 4.8, "total_cpi_yoy": 4.8, "gdp_qq_ann": 4.0},
            # Q4/Q4 anchors
            {"quarter": "2022Q4", "core_cpi_yoy": 2.1, "total_cpi_yoy": 2.1},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.5, "total_cpi_yoy": 2.5},
        ],
        "annual": [
            {"year": 2021, "potential_low": 0.8, "potential_high": 2.2, "gdp_q4q4": 3.4, "gdp_annual_avg": 5.1},
            {"year": 2022, "potential_low": 0.4, "potential_high": 2.2, "gdp_q4q4": 4.6, "gdp_annual_avg": 4.3},
            {"year": 2023, "potential_low": 1.0, "potential_high": 3.0, "gdp_q4q4": 3.0, "gdp_annual_avg": 3.7},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2021/10/mpr-2021-10-27/",
        "notes": (
            "PDF: wp-content/uploads/2021/10/mpr-2021-10-27.pdf. Held at 0.25% ELB; ended QE. "
            "Neutral 1.75-2.75 (carried from Apr 2021 reassessment). Output gap 'between -2.25 and "
            "-1.25 percent in the third quarter' (excess supply). Projection ends 2023Q4. "
            "Potential-output range from Table 2 memo row. Tables publish total CPI only. "
            "GDP coverage via Q4/Q4 anchors."
        ),
    },
    # ----------------------------------------------------------------- #
    # July 2021 MPR
    # ----------------------------------------------------------------- #
    {
        "mpr_date": "2021-07-14",
        "projection_end_quarter": "2023Q4",
        "neutral_range": (1.75, 2.75),
        "output_gap_range": (-3.0, -2.0),
        "output_gap_quarter": "2021Q2",
        "current_overnight_rate": 0.25,
        "quarterly": [
            {"quarter": "2020Q4", "core_cpi_yoy": 0.7, "total_cpi_yoy": 0.7, "gdp_qq_ann": 9.3},
            {"quarter": "2021Q1", "core_cpi_yoy": 1.5, "total_cpi_yoy": 1.5, "gdp_qq_ann": 5.6},
            {"quarter": "2021Q2", "core_cpi_yoy": 3.4, "total_cpi_yoy": 3.4, "gdp_qq_ann": 2.0},
            {"quarter": "2021Q3", "core_cpi_yoy": 3.9, "total_cpi_yoy": 3.9, "gdp_qq_ann": 7.3},
            # Q4/Q4 anchors
            {"quarter": "2021Q4", "core_cpi_yoy": 3.5, "total_cpi_yoy": 3.5},
            {"quarter": "2022Q4", "core_cpi_yoy": 2.0, "total_cpi_yoy": 2.0},
            {"quarter": "2023Q4", "core_cpi_yoy": 2.4, "total_cpi_yoy": 2.4},
        ],
        "annual": [
            {"year": 2021, "potential_low": 0.8, "potential_high": 2.2, "gdp_q4q4": 4.9, "gdp_annual_avg": 6.0},
            {"year": 2022, "potential_low": 0.4, "potential_high": 2.2, "gdp_q4q4": 4.2, "gdp_annual_avg": 4.6},
            {"year": 2023, "potential_low": 1.0, "potential_high": 3.0, "gdp_q4q4": 2.9, "gdp_annual_avg": 3.3},
        ],
        "core_concept": "total_cpi_fallback",
        "source_url": "https://www.bankofcanada.ca/2021/07/mpr-2021-07-14/",
        "notes": (
            "PDF: wp-content/uploads/2021/07/mpr-2021-07-14.pdf. Held at 0.25% ELB. Neutral "
            "1.75-2.75 (reassessed in Apr 2021, restated here). Output gap 'between -3.0 and -2.0 "
            "percent in the second quarter of 2021' (excess supply). Projection ends 2023Q4. "
            "Potential-output range from Table 2 memo row. Tables publish total CPI only. "
            "GDP coverage via Q4/Q4 anchors. 2020Q4 quarterly row carried for context; 2021 annual "
            "row included so the seed year has potential + GDP coverage."
        ),
    },
]
