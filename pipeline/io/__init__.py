"""On-disk IO for the pipeline.

The on-disk contract is the public API between the Python pipeline and the
Astro site (see ARCHITECTURE.md ADR-0002). Every dataset emits two files:

    data/<area>/<name>.csv          tidy long-format CSV (or wide where natural)
    data/<area>/<name>.meta.json    sibling metadata: source, fetched-at,
                                    release date, reference period, units,
                                    schema version

Consumers (charts, blurbs, the Astro build) must be able to answer
"where did this number come from on this date?" from the .meta.json alone.
"""

from pipeline.io.meta import (
    SCHEMA_VERSION,
    SeriesMeta,
    write_series,
    write_series_merge,
)
from pipeline.io.site_data import build_site_data

__all__ = [
    "SCHEMA_VERSION",
    "SeriesMeta",
    "write_series",
    "write_series_merge",
    "build_site_data",
]
