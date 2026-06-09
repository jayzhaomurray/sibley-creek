"""Bank of Canada Market Participants Survey (MPS): median expected
overnight-rate paths, one record per published survey.

Source archive: https://www.bankofcanada.ca/publications/market-participants-survey/

The MPS is conducted quarterly. Bank of Canada staff poll ~30 financial-market
participants (banks, dealers, pension funds, insurers, asset managers) on their
expectations for monetary policy and financial variables. Question 2.1 asks for
each respondent's forecast of the Bank's policy (overnight target) rate at a
sequence of future points; the Bank publishes the MEDIAN of those responses.

Publication timing (important for the backtest's information-advantage note):
results are released "approximately two weeks after the January, April, July and
October monetary policy decision announcements" — i.e. roughly two weeks AFTER
the corresponding Monetary Policy Report (MPR). The same-quarter survey therefore
sees the MPR's decision and projection before responding. The backtest matches
each MPR vintage to the MPS of the SAME reference quarter and flags this small
information advantage in favour of the survey.

First published survey: 2023Q1 (released 2023-04-24). This is the earliest MPS on
the archive; the survey programme launched in 2023 (staff analytical note
2023-1). MPR vintages before 2023Q1 therefore have no matched market path.

Transcription convention (see the brief):
- The published path mixes specific future MONTHS (near term) with QUARTER-ends
  and YEAR-ends (further out). Each point is recorded here as a calendar-quarter
  string "YYYYQn":
    * a month point -> the quarter that contains it (Jan-Mar=Q1, ... Oct-Dec=Q4),
    * a published "Qn YYYY" point -> that quarter,
    * a year-end point -> Q4 of that year.
- When several published month points fall in the SAME quarter, the LAST month in
  that quarter is kept (the quarter-END value), because the realized comparison
  series (overnight_rate_target.csv) is itself sampled at quarter-end. The path
  lists therefore carry at most one (quarter, rate) point per quarter, in
  chronological order, exactly as published for that quarter-end month.
- Rates are percent, exactly as published (e.g. 2.88 where the Bank printed a
  median of 2.88%).

Each record:
    {
      "survey": "YYYYQn",            # MPS reference quarter
      "published": "YYYY-MM-DD",     # release date as printed
      "source_url": "https://...",   # the survey results page
      "path": [("YYYYQn", rate), ...]  # median expected ON rate, quarter-end
    }

These are consumed by pipeline.shadow_rate.backtest (MARKET_PATHS), which
interpolates the sparse points linearly across quarters to evaluate the market
expectation at each scored horizon.
"""

from __future__ import annotations

MARKET_PATHS: list[dict] = [
    # ----------------------------------------------------------------- #
    # 2023Q1 — first published MPS (survey conducted Mar 9-23, 2023)
    # ----------------------------------------------------------------- #
    {
        "survey": "2023Q1",
        "published": "2023-04-24",
        "source_url": "https://www.bankofcanada.ca/2023/04/market-participants-survey-first-quarter-of-2023/",
        # Published: Apr/Jun/Jul/Sep/Oct/Dec 2023 all 4.50; Jan/Mar 2024 4.00;
        # Q2 2024 3.50; Q3 2024 3.25; Q4 2024 3.00; Q1 2025 2.88; Q2 2025 2.88.
        "path": [
            ("2023Q2", 4.50),
            ("2023Q3", 4.50),
            ("2023Q4", 4.50),
            ("2024Q1", 4.00),
            ("2024Q2", 3.50),
            ("2024Q3", 3.25),
            ("2024Q4", 3.00),
            ("2025Q1", 2.88),
            ("2025Q2", 2.88),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2023Q2 (survey conducted Jun 8-19, 2023)
    # ----------------------------------------------------------------- #
    {
        "survey": "2023Q2",
        "published": "2023-07-24",
        "source_url": "https://www.bankofcanada.ca/2023/07/market-participants-survey-second-quarter-of-2023/",
        # Jul/Sep/Oct/Dec 2023 5.00; Jan 2024 5.00, Mar 4.75, Apr 4.50, Jun 4.25;
        # Q3 2024 3.75; Q4 2024 3.50; Q1 2025 3.25; Q2 2025 2.75; Q3 2025 2.50.
        "path": [
            ("2023Q3", 5.00),
            ("2023Q4", 5.00),
            ("2024Q1", 4.75),
            ("2024Q2", 4.25),
            ("2024Q3", 3.75),
            ("2024Q4", 3.50),
            ("2025Q1", 3.25),
            ("2025Q2", 2.75),
            ("2025Q3", 2.50),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2023Q3 (survey conducted Sep 20-28, 2023; BoC slug typo "markets-")
    # ----------------------------------------------------------------- #
    {
        "survey": "2023Q3",
        "published": "2023-11-06",
        "source_url": "https://www.bankofcanada.ca/2023/11/markets-participants-survey-third-quarter-of-2023/",
        # Oct/Dec 2023 5.00; Jan/Mar 2024 5.00, Apr/Jun 4.75, Jul 4.50, Sep 4.25;
        # Q4 2024 4.00; Q1 2025 3.50; Q2 2025 3.25; Q3 2025 3.00; Q4 2025 2.88.
        "path": [
            ("2023Q4", 5.00),
            ("2024Q1", 5.00),
            ("2024Q2", 4.75),
            ("2024Q3", 4.25),
            ("2024Q4", 4.00),
            ("2025Q1", 3.50),
            ("2025Q2", 3.25),
            ("2025Q3", 3.00),
            ("2025Q4", 2.88),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2023Q4 (survey conducted Dec 2023 - early Jan 2024)
    # ----------------------------------------------------------------- #
    {
        "survey": "2023Q4",
        "published": "2024-02-05",
        "source_url": "https://www.bankofcanada.ca/2024/02/market-participants-survey-fourth-quarter-of-2023/",
        # Jan/Mar 2024 5.00, Apr/Jun 4.75, Jul 4.50, Sep 4.25, Oct/Dec 4.00;
        # Q1 2025 3.50; Q2 2025 3.00; Q3 2025 3.00; Q4 2025 3.00; Q1 2026 2.88.
        "path": [
            ("2024Q1", 5.00),
            ("2024Q2", 4.75),
            ("2024Q3", 4.25),
            ("2024Q4", 4.00),
            ("2025Q1", 3.50),
            ("2025Q2", 3.00),
            ("2025Q3", 3.00),
            ("2025Q4", 3.00),
            ("2026Q1", 2.88),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2024Q1 (survey conducted Mar 2024)
    # ----------------------------------------------------------------- #
    {
        "survey": "2024Q1",
        "published": "2024-04-22",
        "source_url": "https://www.bankofcanada.ca/2024/04/market-participants-survey-first-quarter-of-2024/",
        # Apr 2024 5.00, Jun 4.75, Jul 4.50, Sep 4.50, Oct 4.25, Dec 4.00;
        # Jan 2025 4.00, Mar 3.75; Q2 2025 3.50; Q3 2025 3.25; Q4 2025 3.00;
        # Q1 2026 2.88; Q2 2026 2.75.
        "path": [
            ("2024Q2", 4.75),
            ("2024Q3", 4.50),
            ("2024Q4", 4.00),
            ("2025Q1", 3.75),
            ("2025Q2", 3.50),
            ("2025Q3", 3.25),
            ("2025Q4", 3.00),
            ("2026Q1", 2.88),
            ("2026Q2", 2.75),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2024Q2 (survey conducted Jun 25 - Jul 3, 2024)
    # ----------------------------------------------------------------- #
    {
        "survey": "2024Q2",
        "published": "2024-08-02",
        "source_url": "https://www.bankofcanada.ca/2024/08/market-participants-survey-second-quarter-of-2024/",
        # Jul 2024 4.50, Sep 4.50, Oct 4.25, Dec 4.00; Jan 2025 4.00, Mar 3.75,
        # Apr 3.50, Jun 3.25; Q3 2025 3.00; Q4 2025 3.00; Q1 2026 3.00;
        # Q2 2026 2.94; Q3 2026 2.88.
        "path": [
            ("2024Q3", 4.50),
            ("2024Q4", 4.00),
            ("2025Q1", 3.75),
            ("2025Q2", 3.25),
            ("2025Q3", 3.00),
            ("2025Q4", 3.00),
            ("2026Q1", 3.00),
            ("2026Q2", 2.94),
            ("2026Q3", 2.88),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2024Q3 (survey conducted Sep 18-27, 2024)
    # ----------------------------------------------------------------- #
    {
        "survey": "2024Q3",
        "published": "2024-11-04",
        "source_url": "https://www.bankofcanada.ca/2024/11/market-participants-survey-third-quarter-of-2024/",
        # Oct 2024 4.00, Dec 3.75; Jan 2025 3.50, Mar 3.25, Apr 3.00, Jun 2.75,
        # Jul 2.75, Sep 2.75; Q4 2025 2.75; Q1-Q4 2026 all 2.75.
        "path": [
            ("2024Q4", 3.75),
            ("2025Q1", 3.25),
            ("2025Q2", 2.75),
            ("2025Q3", 2.75),
            ("2025Q4", 2.75),
            ("2026Q1", 2.75),
            ("2026Q2", 2.75),
            ("2026Q3", 2.75),
            ("2026Q4", 2.75),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2024Q4 (survey conducted Dec 17, 2024 - Jan 6, 2025)
    # ----------------------------------------------------------------- #
    {
        "survey": "2024Q4",
        "published": "2025-02-10",
        "source_url": "https://www.bankofcanada.ca/2025/02/market-participants-survey-fourth-quarter-of-2024/",
        # Jan 2025 3.00, Mar 3.00, Apr 2.75, Jun 2.75, Jul 2.50, Sep 2.50,
        # Oct 2.50, Dec 2.50; Q1-Q4 2026 all 2.50; Q1 2027 2.75.
        "path": [
            ("2025Q1", 3.00),
            ("2025Q2", 2.75),
            ("2025Q3", 2.50),
            ("2025Q4", 2.50),
            ("2026Q1", 2.50),
            ("2026Q2", 2.50),
            ("2026Q3", 2.50),
            ("2026Q4", 2.50),
            ("2027Q1", 2.75),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2025Q1 (survey conducted Mar 13-20, 2025)
    # ----------------------------------------------------------------- #
    {
        "survey": "2025Q1",
        "published": "2025-04-28",
        "source_url": "https://www.bankofcanada.ca/2025/04/market-participants-survey-first-quarter-of-2025/",
        # Apr 2025 2.75, Jun 2.50, Jul 2.25, Sep 2.25, Oct 2.25, Dec 2.25;
        # Jan 2026 2.13, Mar 2.13; Q2 2026 2.00; Q3 2026 2.13; Q4 2026 2.13;
        # Q1 2027 2.25; Q2 2027 2.50.
        "path": [
            ("2025Q2", 2.50),
            ("2025Q3", 2.25),
            ("2025Q4", 2.25),
            ("2026Q1", 2.13),
            ("2026Q2", 2.00),
            ("2026Q3", 2.13),
            ("2026Q4", 2.13),
            ("2027Q1", 2.25),
            ("2027Q2", 2.50),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2025Q2 (survey conducted Jun 25 - Jul 3, 2025)
    # ----------------------------------------------------------------- #
    {
        "survey": "2025Q2",
        "published": "2025-08-11",
        "source_url": "https://www.bankofcanada.ca/2025/08/market-participants-survey-second-quarter-of-2025/",
        # Jul 2025 2.75, Sep 2.50, Oct 2.50, Dec 2.25; Jan/Mar/Apr/Jun 2026 2.25;
        # Q3 2026 2.25; Q4 2026 2.25; Q1 2027 2.25; Q2 2027 2.25; Q3 2027 2.50.
        "path": [
            ("2025Q3", 2.50),
            ("2025Q4", 2.25),
            ("2026Q1", 2.25),
            ("2026Q2", 2.25),
            ("2026Q3", 2.25),
            ("2026Q4", 2.25),
            ("2027Q1", 2.25),
            ("2027Q2", 2.25),
            ("2027Q3", 2.50),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2025Q3 (survey conducted Sep 2025)
    # ----------------------------------------------------------------- #
    {
        "survey": "2025Q3",
        "published": "2025-11-10",
        "source_url": "https://www.bankofcanada.ca/2025/11/market-participants-survey-third-quarter-of-2025/",
        # Oct/Dec 2025 2.25; Jan/Mar/Apr/Jun/Jul/Sep 2026 2.25; Q4 2026 2.25;
        # Q1 2027 2.25; Q2 2027 2.25; Q3 2027 2.50; Q4 2027 2.50.
        "path": [
            ("2025Q4", 2.25),
            ("2026Q1", 2.25),
            ("2026Q2", 2.25),
            ("2026Q3", 2.25),
            ("2026Q4", 2.25),
            ("2027Q1", 2.25),
            ("2027Q2", 2.25),
            ("2027Q3", 2.50),
            ("2027Q4", 2.50),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2025Q4 (survey conducted Dec 2025 - early Jan 2026)
    # ----------------------------------------------------------------- #
    {
        "survey": "2025Q4",
        "published": "2026-02-09",
        "source_url": "https://www.bankofcanada.ca/2026/02/market-participants-survey-fourth-quarter-of-2025/",
        # Jan/Mar/Apr/Jun/Jul/Sep/Oct/Dec 2026 all 2.25; Q1 2027 2.25;
        # Q2 2027 2.50; Q3 2027 2.50; Q4 2027 2.75; Q1 2028 2.75.
        "path": [
            ("2026Q1", 2.25),
            ("2026Q2", 2.25),
            ("2026Q3", 2.25),
            ("2026Q4", 2.25),
            ("2027Q1", 2.25),
            ("2027Q2", 2.50),
            ("2027Q3", 2.50),
            ("2027Q4", 2.75),
            ("2028Q1", 2.75),
        ],
    },
    # ----------------------------------------------------------------- #
    # 2026Q1 — most recent (survey conducted Mar 2026)
    # ----------------------------------------------------------------- #
    {
        "survey": "2026Q1",
        "published": "2026-05-11",
        "source_url": "https://www.bankofcanada.ca/2026/05/market-participants-survey-first-quarter-of-2026/",
        # Apr/Jun/Jul/Sep/Oct/Dec 2026 all 2.25; Jan 2027 2.25, Mar 2.50;
        # Q2 2027 2.50; Q3 2027 2.50; Q4 2027 2.75; Q1 2028 2.75; Q2 2028 2.75.
        "path": [
            ("2026Q2", 2.25),
            ("2026Q3", 2.25),
            ("2026Q4", 2.25),
            ("2027Q1", 2.50),
            ("2027Q2", 2.50),
            ("2027Q3", 2.50),
            ("2027Q4", 2.75),
            ("2028Q1", 2.75),
            ("2028Q2", 2.75),
        ],
    },
]
