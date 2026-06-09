"""Frozen Pydantic Spec for the LFS-micro Oaxaca-Blinder engine.

The Spec captures every free parameter of the model so calibration results
are reproducible. Frozen after creation — create a new instance to change
parameters.

Parameters:

  weighted (bool):
    True  -> WLS using FINALWT as regression weights (recommended;
             matches BoC SAN 2024-23 implicit convention).
    False -> unweighted OLS (for calibration comparison only).

  smoothing (str):
    "raw" -> use raw monthly values; y/y is point-to-point.
    "ma3" -> 3-month centred moving average applied to the underlying
             and composition series before differencing.

  ob_reference (str):
    "base"    -> Oaxaca-Blinder reference = base period (t-12).
                 Composition = delta_X' * B_{t-12}
                 Underlying  = X_{t-12}' * delta_B
    "current" -> Reference = current period (t).
                 Composition = delta_X' * B_t
                 Underlying  = X_t' * delta_B
    Both are valid; the note doesn't specify explicitly. Calibration picks.

  tenure_bins (list[float]):
    Bin edges for tenure in months. Default: [0, 12, 36, 60, 120, inf].
    Must have at least 2 edges. The resulting labels are auto-derived from
    the edges by harmonize.py (_TENURE_BINS / _TENURE_LABELS).
    Note: changing bins invalidates existing parquet caches (re-harmonize needed).

  min_cell_count (int):
    Minimum number of observations required in a tenure bin (or any other
    categorical cell) for it to be included in the regression. Cells with
    fewer observations are dropped and their dummy is excluded from the
    design matrix. Logged when triggered.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Spec(BaseModel, frozen=True):
    """Frozen specification for the LFS-micro O-B engine."""

    weighted: bool = True
    smoothing: Literal["raw", "ma3"] = "raw"
    ob_reference: Literal["base", "current"] = "base"
    tenure_bins: tuple[float, ...] = (0.0, 12.0, 36.0, 60.0, 120.0, float("inf"))
    min_cell_count: int = Field(default=30, ge=1)

    @model_validator(mode="after")
    def validate_tenure_bins(self) -> "Spec":
        if len(self.tenure_bins) < 2:
            raise ValueError("tenure_bins must have at least 2 edges.")
        for i in range(1, len(self.tenure_bins)):
            if self.tenure_bins[i] <= self.tenure_bins[i - 1]:
                raise ValueError(
                    f"tenure_bins must be strictly increasing; "
                    f"got {self.tenure_bins[i-1]} >= {self.tenure_bins[i]}."
                )
        return self

    @property
    def tenure_labels(self) -> list[str]:
        """Human-readable label for each tenure bracket (n_bins - 1 labels)."""
        edges = self.tenure_bins
        labels = []
        for i in range(len(edges) - 1):
            lo = int(edges[i])
            hi = edges[i + 1]
            if hi == float("inf"):
                labels.append(f"{lo}m+")
            else:
                labels.append(f"{lo}-{int(hi)-1}m")
        return labels

    def as_dict(self) -> dict:
        """Return a JSON-serializable dict of all parameters."""
        d = self.model_dump()
        # Convert tuple to list and handle inf for JSON
        d["tenure_bins"] = [
            v if v != float("inf") else None for v in self.tenure_bins
        ]
        return d


# Default Spec — recalibrated 2026-06-05 PM on CLEAN data.
# The original 2026-06-05 AM grid picked smoothing=ma3, but that grid ran on
# data later found corrupted (wrong-month parquets): the corruption created
# huge single-month outliers that MA3 diluted, making MA3 look better. On
# clean data the unsmoothed series wins decisively:
#   raw: RMSE=0.1181 pp, corr=0.9966 (n=122)   ma3: RMSE=0.1804 pp, corr=0.9860
# Roughness check confirms the BoC does not smooth: std of m/m changes is
# 0.295 pp (BoC) vs 0.293 pp (ours raw) vs 0.165 pp (ours ma3), and the BoC
# series' change autocorrelation is ~0 (white) — no MA signature.
# WLS (weighted) strongly preferred over unweighted. Base vs current
# reference: ~0.001 pp difference; base matches the note's framing.
# UNITS (2026-06-09 audit): the BoC publishes the series in log points
# (100*dlog); compared same-units (lp-vs-lp) this spec's fit is RMSE
# 0.0885 pp, bias +0.037 pp — the 0.1178 figure above mixed conventions
# (our exp()-1 vs their lp). lp-vs-lp is the canonical fidelity metric.
# See: claude-ref/research/lfs_micro/calibration_report.md for full diagnosis.
DEFAULT_SPEC = Spec(
    weighted=True,
    smoothing="raw",
    ob_reference="base",
    min_cell_count=30,
)
