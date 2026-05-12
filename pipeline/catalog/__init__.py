"""Series catalogs.

One submodule per upstream source. Each catalog is a dict of
`{name: SeriesSpec}` that the build orchestrator iterates over. Series are
grouped by section (gdp, inflation, labour, housing, financial, trade,
policy) so the orchestrator can selectively run a subset (e.g. only the
daily-cadence Financial section in `build_financial.py`).

Editorial scope decisions (which series to include) live in the catalogs.
The fetcher modules under `pipeline/fetch/` are scope-agnostic; they take
IDs as arguments.
"""

from pipeline.catalog.statcan_series import STATCAN_SERIES
from pipeline.catalog.boc_series import BOC_VALET_SERIES
from pipeline.catalog.fred_series import FRED_SERIES
from pipeline.catalog.indeed_series import INDEED_SERIES
from pipeline.catalog.yahoo_series import YAHOO_SERIES

__all__ = [
    "STATCAN_SERIES",
    "BOC_VALET_SERIES",
    "FRED_SERIES",
    "INDEED_SERIES",
    "YAHOO_SERIES",
]
