"""Indeed Hiring Lab series catalog.

Indeed Hiring Lab is the canonical complement to StatCan JVWS for the
labour panel-4 (vacancies + slack): a daily-cadence Canadian job-postings
index, SA, with Feb 1 2020 = 100. JVWS is monthly and was suspended
April-September 2020; the Indeed index bridges that gap and gives the
dashboard a daily-fresh vacancies read between JVWS prints.

License: CC BY 4.0; cite as "Source: Indeed Hiring Lab".

Source: GitHub `hiring-lab/job_postings_tracker`, default branch `master`.
Pulled as plain CSV; no API key required.

The fetcher lives at `pipeline.fetch.indeed_hiring_lab`. The orchestrator
in `pipeline.build_financial` runs the aggregate fetch alongside FRED +
Yahoo + BoC daily series and writes:
    data/raw/indeed_postings_ca.csv          (daily SA total postings)
    data/raw/indeed_postings_ca_monthly.csv  (monthly mean -- feeds panel-4)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndeedSpec:
    name: str
    filename: str           # source CSV file under hiring-lab/job_postings_tracker/CA/
    variable: str           # which `variable` slice ("total postings" / "new postings")
    measure: str            # "SA" or "NSA"
    units: str
    section: str
    cadence: str
    notes: str = ""


# Only the aggregate-Canada series is wired by default. Provincial breakdown
# is available via `pipeline.fetch.indeed_hiring_lab.fetch_provincial_postings`
# but is not registered here because no v1 panel consumes it; if a future
# chart-builder dispatch wants per-province coverage we add it then.
INDEED_SERIES: dict[str, IndeedSpec] = {
    "indeed_postings_ca": IndeedSpec(
        name="indeed_postings_ca",
        filename="aggregate_job_postings_CA.csv",
        variable="total postings",
        measure="SA",
        units="Index, Feb 1 2020 = 100",
        section="labour",
        cadence="daily",
        notes=(
            "Indeed Hiring Lab Canada total postings index, seasonally "
            "adjusted (Deutsche Bundesbank method per Hiring Lab data "
            "dictionary). Daily. Complements StatCan JVWS (monthly, "
            "April-September 2020 suspended). License: CC BY 4.0; cite "
            "as 'Source: Indeed Hiring Lab'."
        ),
    ),
}
