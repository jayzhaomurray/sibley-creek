"""Reusable analytical transforms.

These are transforms that are not chart-specific: rolling means, YoY / QoQ
/ MoM deltas, base-year indexing, smoothing, annualization. Chart-shape
transforms (histogram binning, geographic projections, treemap layouts)
belong with the chart components in `charts/`, not here.

Editorial interpretation does NOT live here. A function returns the math;
the researcher / editorial-director decides what to call "high" or "hot".
"""

from pipeline.transform.timeseries import (
    annualize_period_growth,
    index_to_base,
    moving_average,
    pct_change_at_horizon,
    qoq_annualized_pct,
    rebase_to_first,
    yoy_pct,
)

__all__ = [
    "annualize_period_growth",
    "index_to_base",
    "moving_average",
    "pct_change_at_horizon",
    "qoq_annualized_pct",
    "rebase_to_first",
    "yoy_pct",
]
