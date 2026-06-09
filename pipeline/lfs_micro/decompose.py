"""Oaxaca-Blinder two-fold decomposition for LFS-micro wage growth.

The two-fold Oaxaca-Blinder decomposition splits y/y log-wage growth into:

  Total growth = Composition effect + Underlying wage growth (+ Interaction)

We EXCLUDE the interaction term (standard for the two-fold "pure" O-B):

  Composition effect (C): ΔE(X)' * B_ref
    = (mean_X_t - mean_X_{t-12})' * B_ref
    Captures the contribution of shifts in the employment distribution
    (e.g. more college-educated workers) to measured wage growth.

  Underlying wage growth (U): E(X_ref)' * ΔB
    = mean_X_ref' * (B_t - B_{t-12})
    Captures the contribution of changes in wage returns for a given worker
    type, holding composition fixed.

Where B_ref and mean_X_ref are determined by ob_reference:
  "base"    -> B_ref = B_{t-12}, mean_X_ref = mean_X_{t-12}
  "current" -> B_ref = B_t,      mean_X_ref = mean_X_t

The sum C + U equals the fitted log-wage gap (E(X_t)'*B_t - E(X_{t-12})'*B_{t-12}),
which approximates the raw mean log-wage change modulo residual variation.

Note on log-point vs percent:
  The output is in log-points (natural log). To convert to percent change:
    pct = exp(log_points) - 1.0
  For small values (<5%), log_points ≈ pct. The BoC publishes in percent y/y,
  so engine.py applies exp()-1 before writing the output series.

Per-characteristic-group contributions:
  The composition effect can be decomposed into per-group contributions:
    C_j = (mean_X_t_j - mean_X_{t-12}_j)' * B_ref_j
  where j indexes one regressor group (e.g. occupation, education).
  These contributions sum to C exactly (no approximation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from .regression import RegressionResult, REGRESSOR_GROUPS


@dataclass
class OBDecomposition:
    """Result of one Oaxaca-Blinder decomposition (one y/y pair).

    Attributes:
        total_fitted:    E(X_t)'*B_t - E(X_{t-12})'*B_{t-12} (log-points).
                         This is the fitted/predicted log-wage change.
        composition:     ΔE(X)' * B_ref (log-points).
        underlying:      E(X_ref)' * ΔB (log-points).
        interaction:     Residual = total_fitted - composition - underlying
                         (excluded from the two-fold; stored for diagnostics).
        raw_mean_change: Actual mean log-wage change (not decomposed).
        group_contributions: Per-characteristic-group contribution to the
                             composition effect {group_label: log-points}.
        ob_reference:    "base" or "current" (stored for provenance).
    """
    total_fitted: float
    composition: float
    underlying: float
    interaction: float
    raw_mean_change: float
    group_contributions: dict[str, float] = field(default_factory=dict)
    ob_reference: str = "base"


def oaxaca_blinder(
    result_base: RegressionResult,
    result_current: RegressionResult,
    ob_reference: Literal["base", "current"] = "base",
) -> OBDecomposition:
    """Two-fold Oaxaca-Blinder decomposition for one y/y pair.

    Both result_base (t-12) and result_current (t) must have been estimated
    on the SAME design matrix (same col_names in the same order). Use
    regression.union_category_universe() + regression.run_wls(..., category_universe=...)
    to ensure conformability before calling this function.

    Args:
        result_base:    RegressionResult for the base month (t-12).
        result_current: RegressionResult for the current month (t).
        ob_reference:   "base" -> B_ref = B_{t-12}, mean_X_ref = mean_X_{t-12}.
                        "current" -> B_ref = B_t, mean_X_ref = mean_X_t.

    Returns:
        OBDecomposition with all fields populated.

    Raises:
        ValueError: If col_names of the two results do not match.
    """
    if result_base.col_names != result_current.col_names:
        raise ValueError(
            "Oaxaca-Blinder: col_names of result_base and result_current do not match. "
            "Run both regressions with the same category_universe."
        )

    B_base = result_base.coef        # B_{t-12}
    B_curr = result_current.coef     # B_t
    X_base = result_base.mean_X      # E(X)_{t-12}
    X_curr = result_current.mean_X   # E(X)_t

    delta_X = X_curr - X_base        # ΔE(X)
    delta_B = B_curr - B_base        # ΔB

    # Reference period vectors
    if ob_reference == "base":
        B_ref = B_base
        X_ref = X_base
    else:  # "current"
        B_ref = B_curr
        X_ref = X_curr

    # Two-fold decomposition (no interaction term)
    composition = float(delta_X @ B_ref)   # ΔE(X)' * B_ref
    underlying  = float(X_ref @ delta_B)   # E(X_ref)' * ΔB

    # Fitted total (using the full dot products, not the two-fold sum)
    fitted_curr = float(X_curr @ B_curr)
    fitted_base = float(X_base @ B_base)
    total_fitted = fitted_curr - fitted_base

    # Interaction = total - composition - underlying (stored for diagnostics)
    interaction = total_fitted - composition - underlying

    # Raw mean log-wage change (actual, not fitted)
    raw_mean_change = result_current.mean_log_wage - result_base.mean_log_wage

    # Per-characteristic-group contributions to composition effect
    group_contributions = _group_contributions(
        result_base, result_current, B_ref
    )

    return OBDecomposition(
        total_fitted=total_fitted,
        composition=composition,
        underlying=underlying,
        interaction=interaction,
        raw_mean_change=raw_mean_change,
        group_contributions=group_contributions,
        ob_reference=ob_reference,
    )


# ---------------------------------------------------------------------------
# Per-group contributions
# ---------------------------------------------------------------------------

def _group_contributions(
    result_base: RegressionResult,
    result_current: RegressionResult,
    B_ref: np.ndarray,
) -> dict[str, float]:
    """Compute per-characteristic-group contribution to the composition effect.

    For group j (e.g. occupation):
      C_j = (mean_X_t_j - mean_X_{t-12}_j)' * B_ref_j

    where the subscript _j denotes the sub-vector of the design matrix
    corresponding to group j's dummy columns.

    The contributions sum to the total composition effect exactly.

    Returns:
        Dict {group_label: contribution_in_log_points}
    """
    contributions: dict[str, float] = {}
    col_names = result_base.col_names

    for col, group_label in REGRESSOR_GROUPS:
        # Find column indices belonging to this group
        prefix = f"{col}_"
        indices = [i for i, n in enumerate(col_names) if n.startswith(prefix)]
        if not indices:
            continue

        delta_X_j = result_current.mean_X[indices] - result_base.mean_X[indices]
        B_ref_j = B_ref[indices]
        contributions[group_label] = float(delta_X_j @ B_ref_j)

    # Intercept has no group — absorbs any unaccounted portion
    # (should be zero for composition effect since intercept mean_X is always 1)
    return contributions
