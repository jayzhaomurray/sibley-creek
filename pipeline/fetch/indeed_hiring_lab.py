"""Indeed Hiring Lab Canadian job-postings fetcher.

Indeed Hiring Lab publishes a daily index of Canadian job postings,
seasonally adjusted (and an NSA companion), as a plain-CSV bulk file on
GitHub:

    https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/
        master/CA/aggregate_job_postings_CA.csv

The series is the canonical Indeed postings index referenced as the
complement to StatCan JVWS in the labour panel-4 (vacancies + slack); JVWS
suspended publication April-September 2020 during COVID and the Indeed
index is the only daily-cadence Canadian vacancies signal that bridges
that gap.

Source quirks
-------------
- License: CC BY 4.0; cite as "Source: Indeed Hiring Lab".
- Methodology: Deutsche Bundesbank seasonal adjustment per the repo's
  data dictionary; daily SA values reset Feb 1 2020 = 100.
- Repo identity: `hiring-lab/job_postings_tracker`, default branch
  `master` (not `main`). The previous static lift hard-coded
  `hiring-lab/data`, which 404s; this fetcher uses the correct path.
- Schema (aggregate CSV):
    date, jobcountry, indeed_job_postings_index_SA,
    indeed_job_postings_index_NSA, variable
  where `variable` is either "total postings" (the canonical SA index)
  or "new postings" (new posts created within the trailing 7 days,
  surfaced as a leading-indicator companion). We extract the SA total
  postings series by default; callers can flip to NSA / new postings.
- Schema (provincial CSV):
    date, province, indeed_job_postings_index
  Province codes are lowercase two-letter (ab, bc, mb, nb, nl, ns, on,
  pe, qc, sk). YT / NT / NU are not published. Single index column with
  no SA / NSA split.
- Refresh cadence: refreshed weekly (typically Thursdays). Running the
  daily orchestrator against it is fine -- most days the pull returns
  identical bytes and the git commit step in CI is a no-op.
- Rate limit: GitHub raw is unauthenticated and free for typical project
  scale. The 60 req/hour anonymous limit on `api.github.com` does NOT
  apply to `raw.githubusercontent.com`; raw enforces a much higher
  unauthenticated quota (per GitHub docs, "thousands per hour" for
  ordinary file fetches) and we hit it at most twice per daily run.
  If we ever do see 429s, the shared `_http` retry policy already
  backs off; raising the cadence beyond daily is unnecessary.

Boundary validation: we parse the CSV head and assert the expected
columns are present before extracting, so a silent upstream schema
rename surfaces as a clear ValueError rather than an empty DataFrame.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from pipeline.fetch._http import get_client, get_text

logger = logging.getLogger(__name__)

GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/master/CA"
)
AGGREGATE_FILENAME = "aggregate_job_postings_CA.csv"
PROVINCIAL_FILENAME = "provincial_postings_ca.csv"

# Human-facing repo URLs for .meta.json provenance.
REPO_HTML_BASE = "https://github.com/hiring-lab/job_postings_tracker"


@dataclass(frozen=True)
class IndeedFetchResult:
    """Result of one Indeed aggregate or provincial fetch."""

    name: str
    source_url: str
    data: pd.DataFrame
    source_column: str   # the upstream column name we extracted
    variable: Optional[str] = None  # for aggregate: "total postings" / "new postings"


def aggregate_url() -> str:
    """Raw URL for the Canada aggregate postings CSV."""
    return f"{GITHUB_RAW_BASE}/{AGGREGATE_FILENAME}"


def provincial_url() -> str:
    """Raw URL for the Canada provincial breakdown CSV."""
    return f"{GITHUB_RAW_BASE}/{PROVINCIAL_FILENAME}"


def aggregate_html_url() -> str:
    """Human-readable GitHub URL for the aggregate file (for .meta.json)."""
    return f"{REPO_HTML_BASE}/blob/master/CA/{AGGREGATE_FILENAME}"


def provincial_html_url() -> str:
    """Human-readable GitHub URL for the provincial file (for .meta.json)."""
    return f"{REPO_HTML_BASE}/blob/master/CA/{PROVINCIAL_FILENAME}"


# Expected columns for boundary validation. If Indeed ever renames these
# (it has been stable since 2020, but the API is not contractual) the
# fetcher fails loud with a precise error instead of returning empty.
_AGGREGATE_REQUIRED_COLS = {
    "date",
    "jobcountry",
    "indeed_job_postings_index_SA",
    "indeed_job_postings_index_NSA",
    "variable",
}
_PROVINCIAL_REQUIRED_COLS = {
    "date",
    "province",
    "indeed_job_postings_index",
}


def _parse_csv(text: str) -> pd.DataFrame:
    """Parse CSV text into a DataFrame with no extra type coercion."""
    return pd.read_csv(io.StringIO(text))


def fetch_aggregate_postings(
    *,
    variable: str = "total postings",
    measure: str = "SA",
) -> IndeedFetchResult:
    """Fetch the Canada aggregate Indeed postings index.

    Args:
        variable: which `variable` slice to extract from the upstream CSV.
            "total postings" (default) -- canonical index; matches the
                                          Plate 3 prose ("Feb 2020 = 100").
            "new postings"             -- new posts within trailing 7 days;
                                          leading-indicator companion.
        measure: which measure column to extract.
            "SA"  (default) -- seasonally adjusted index.
            "NSA"           -- non-seasonally-adjusted index.

    Returns:
        IndeedFetchResult with `.data` columns `[date, value]`, sorted
        ascending by date. The `value` column is the Feb 1 2020 = 100
        index level (floats; the upstream rounds to two decimals).

    Raises:
        ValueError if the upstream schema drifts, if no rows match the
        requested variable, or if measure is not one of {"SA", "NSA"}.
    """
    if measure not in ("SA", "NSA"):
        raise ValueError(f"measure must be 'SA' or 'NSA', got {measure!r}")
    col = f"indeed_job_postings_index_{measure}"

    url = aggregate_url()
    with get_client(headers={"Accept": "text/csv,text/plain,*/*"}) as client:
        text = get_text(client, url)

    df = _parse_csv(text)

    missing = _AGGREGATE_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(
            f"Indeed aggregate CSV schema drift: missing columns {sorted(missing)}. "
            f"Got columns: {list(df.columns)}"
        )

    slice_df = df[df["variable"] == variable].copy()
    if slice_df.empty:
        available = sorted(df["variable"].dropna().unique().tolist())
        raise ValueError(
            f"Indeed aggregate CSV had no rows for variable={variable!r}. "
            f"Available variables: {available}"
        )

    slice_df["date"] = pd.to_datetime(slice_df["date"], errors="coerce")
    out = (
        slice_df[["date", col]]
        .dropna(subset=["date", col])
        .rename(columns={col: "value"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["value"]).reset_index(drop=True)

    return IndeedFetchResult(
        name="indeed_postings_ca",
        source_url=url,
        data=out,
        source_column=col,
        variable=variable,
    )


def fetch_provincial_postings() -> IndeedFetchResult:
    """Fetch the Canada provincial Indeed postings breakdown.

    Returns:
        IndeedFetchResult with `.data` columns `[date, province, value]`
        in long form, ascending by date then province. Province codes
        are lowercase two-letter (`ab`, `bc`, `mb`, `nb`, `nl`, `ns`,
        `on`, `pe`, `qc`, `sk`). Splitting to per-province CSVs is left
        to downstream callers; the wide-format pivot is not the
        publication's storage convention.

    Raises:
        ValueError if the upstream schema drifts.
    """
    url = provincial_url()
    with get_client(headers={"Accept": "text/csv,text/plain,*/*"}) as client:
        text = get_text(client, url)

    df = _parse_csv(text)

    missing = _PROVINCIAL_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(
            f"Indeed provincial CSV schema drift: missing columns {sorted(missing)}. "
            f"Got columns: {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    out = (
        df[["date", "province", "indeed_job_postings_index"]]
        .rename(columns={"indeed_job_postings_index": "value"})
        .dropna(subset=["date", "value"])
        .sort_values(["date", "province"])
        .reset_index(drop=True)
    )
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["value"]).reset_index(drop=True)

    return IndeedFetchResult(
        name="indeed_postings_ca_provincial",
        source_url=url,
        data=out,
        source_column="indeed_job_postings_index",
        variable=None,
    )


def aggregate_monthly_mean(daily: pd.DataFrame) -> pd.DataFrame:
    """Aggregate a daily {date, value} frame to monthly means (month-start convention).

    Mirrors the existing `indeed_postings_ca_monthly` series the labour
    panel-4 consumes: each month-start date carries the mean of that
    month's daily SA values. JVWS publishes monthly; matching cadence
    lets the panel overlay them on a single axis without resampling at
    the chart layer.

    Args:
        daily: DataFrame with columns [date, value], one row per day.

    Returns:
        DataFrame with columns [date, value], one row per month, date
        set to the month-start (first of the month).
    """
    if daily.empty:
        return daily.copy()
    s = daily.set_index("date")["value"].sort_index()
    monthly = s.resample("MS").mean()
    out = monthly.reset_index()
    out.columns = ["date", "value"]
    return out.dropna(subset=["value"]).reset_index(drop=True)
