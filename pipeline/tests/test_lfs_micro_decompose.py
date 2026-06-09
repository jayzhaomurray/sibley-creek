"""Tests for pipeline.lfs_micro.decompose.

Verifies O-B identities exactly on synthetic two-period panels with known
coefficients. The two-fold decomposition must satisfy:

  composition + underlying = total_fitted (the interaction is zero for the
  two-fold; we store it for diagnostics but exclude from the identity).

Actually: composition + underlying + interaction = total_fitted ALWAYS.
We verify:
  1. C + U + interaction = total_fitted  (always exact by construction)
  2. Group contributions sum to total C  (exact)
  3. Reference convention changes C and U but their sum = total_fitted - interaction
  4. ValueError when col_names don't match
"""

from __future__ import annotations

import numpy as np
import pytest

from pipeline.lfs_micro.decompose import oaxaca_blinder, OBDecomposition
from pipeline.lfs_micro.regression import RegressionResult


# ---------------------------------------------------------------------------
# Helper: build a RegressionResult with exact known values
# ---------------------------------------------------------------------------

def _make_result(
    coef: np.ndarray,
    mean_X: np.ndarray,
    col_names: list[str],
    mean_log_wage: float = 0.0,
    n_obs: int = 1000,
    category_universe: dict | None = None,
) -> RegressionResult:
    return RegressionResult(
        coef=coef,
        col_names=col_names,
        mean_log_wage=mean_log_wage,
        mean_X=mean_X,
        n_obs=n_obs,
        r_squared=0.5,
        dropped_cells={},
        category_universe=category_universe if category_universe is not None else {},
    )


# ---------------------------------------------------------------------------
# Identity: C + U + interaction = total_fitted
# ---------------------------------------------------------------------------

def test_ob_identity_holds():
    """C + U + interaction = total_fitted exactly."""
    col_names = ["intercept", "gender_2", "educ_1", "educ_2"]
    n = len(col_names)

    rng = np.random.default_rng(0)
    B_base = rng.normal(0, 0.3, n)
    B_curr = rng.normal(0, 0.3, n)
    X_base = rng.uniform(0, 1, n)
    X_curr = rng.uniform(0, 1, n)
    # Intercept mean must be 1 (constant column)
    X_base[0] = 1.0
    X_curr[0] = 1.0

    r_base = _make_result(B_base, X_base, col_names)
    r_curr = _make_result(B_curr, X_curr, col_names)

    for ref in ("base", "current"):
        ob = oaxaca_blinder(r_base, r_curr, ob_reference=ref)
        # C + U + interaction = total_fitted (by construction)
        residual = ob.total_fitted - (ob.composition + ob.underlying + ob.interaction)
        assert abs(residual) < 1e-12, (
            f"O-B identity violated (ref={ref}): "
            f"C={ob.composition:.6f}, U={ob.underlying:.6f}, "
            f"I={ob.interaction:.6f}, total={ob.total_fitted:.6f}, "
            f"residual={residual:.2e}"
        )


# ---------------------------------------------------------------------------
# Identity: group contributions sum to total composition
# ---------------------------------------------------------------------------

def test_group_contributions_sum_to_composition():
    """Sum of per-group composition contributions equals the total composition effect."""
    from pipeline.lfs_micro.regression import REGRESSOR_GROUPS

    # Build col_names matching the REGRESSOR_GROUPS pattern
    col_names = ["intercept"]
    groups_used = []
    for col, grp in REGRESSOR_GROUPS[:4]:   # use first 4 groups for speed
        col_names.extend([f"{col}_2", f"{col}_3"])
        groups_used.append(grp)

    n = len(col_names)
    rng = np.random.default_rng(1)
    B_base = rng.normal(0, 0.2, n)
    B_curr = rng.normal(0, 0.2, n)
    X_base = np.concatenate([[1.0], rng.uniform(0, 0.5, n - 1)])
    X_curr = np.concatenate([[1.0], rng.uniform(0, 0.5, n - 1)])

    cat_u = {col: [1, 2, 3] for col, _ in REGRESSOR_GROUPS[:4]}
    r_base = _make_result(B_base, X_base, col_names, category_universe=cat_u)
    r_curr = _make_result(B_curr, X_curr, col_names, category_universe=cat_u)

    ob = oaxaca_blinder(r_base, r_curr, ob_reference="base")

    contrib_sum = sum(ob.group_contributions.values())
    # Group contributions only cover named regressor groups; intercept excluded.
    # The residual (intercept's delta_X * B_ref) should be close to 0 since
    # intercept mean_X is 1 in both periods (delta=0).
    # Total composition = sum of group contribs + intercept contrib (=0 ideally)
    # We check that contrib_sum ≈ composition (within floating point of the intercept term)
    intercept_contrib = (X_curr[0] - X_base[0]) * B_base[0]  # should be 0
    assert abs(contrib_sum - ob.composition + intercept_contrib) < 1e-10, (
        f"Group contributions ({contrib_sum:.6f}) don't sum to "
        f"composition ({ob.composition:.6f})"
    )


# ---------------------------------------------------------------------------
# Known-coefficient exact test
# ---------------------------------------------------------------------------

def test_ob_exact_known_values():
    """O-B decomposition on manually computed example gives exact result.

    Setup:
      col_names = ["intercept", "gender_2"]
      B_base = [log(25), log(35)-log(25)]   # men earn $25, women earn $35
      B_curr = [log(28), log(35)-log(28)]   # next year: men $28, women $35
      X_base = [1, 0.4]                     # 40% women in base
      X_curr = [1, 0.5]                     # 50% women in current

    Expected (base reference):
      composition = delta_X' * B_base = (0.1) * (log(35)-log(25))
      underlying  = X_base' * delta_B  = 1*(log(28)-log(25)) + 0.4*(log(35/28)-log(35/25))
                  = log(28/25) + 0.4*log((35/28)/(35/25))
                  = log(28/25) + 0.4*log(25/28)
                  = log(28/25) - 0.4*log(28/25)
                  = 0.6 * log(28/25)
    """
    col_names = ["intercept", "gender_2"]

    # Base period
    B_base = np.array([np.log(25.0), np.log(35.0) - np.log(25.0)])
    X_base = np.array([1.0, 0.4])
    mean_lw_base = float(X_base @ B_base)

    # Current period
    B_curr = np.array([np.log(28.0), np.log(35.0) - np.log(28.0)])
    X_curr = np.array([1.0, 0.5])
    mean_lw_curr = float(X_curr @ B_curr)

    r_base = _make_result(B_base, X_base, col_names, mean_log_wage=mean_lw_base)
    r_curr = _make_result(B_curr, X_curr, col_names, mean_log_wage=mean_lw_curr)

    ob = oaxaca_blinder(r_base, r_curr, ob_reference="base")

    # Expected composition (base reference)
    delta_X = X_curr - X_base
    expected_composition = float(delta_X @ B_base)

    # Expected underlying (base reference)
    delta_B = B_curr - B_base
    expected_underlying = float(X_base @ delta_B)

    assert abs(ob.composition - expected_composition) < 1e-12
    assert abs(ob.underlying - expected_underlying) < 1e-12

    # Total fitted
    expected_total = float(X_curr @ B_curr) - float(X_base @ B_base)
    assert abs(ob.total_fitted - expected_total) < 1e-12


# ---------------------------------------------------------------------------
# Current reference convention
# ---------------------------------------------------------------------------

def test_ob_current_reference_different_from_base():
    """'current' reference produces different C and U than 'base', same total."""
    col_names = ["intercept", "gender_2", "educ_2"]
    n = len(col_names)
    rng = np.random.default_rng(5)
    B_base = rng.normal(0, 0.5, n)
    B_curr = rng.normal(0, 0.5, n)
    X_base = np.array([1.0] + list(rng.uniform(0.1, 0.9, n - 1)))
    X_curr = np.array([1.0] + list(rng.uniform(0.1, 0.9, n - 1)))

    r_base = _make_result(B_base, X_base, col_names)
    r_curr = _make_result(B_curr, X_curr, col_names)

    ob_base = oaxaca_blinder(r_base, r_curr, ob_reference="base")
    ob_curr = oaxaca_blinder(r_base, r_curr, ob_reference="current")

    # Total fitted is the same regardless of reference
    assert abs(ob_base.total_fitted - ob_curr.total_fitted) < 1e-12

    # C and U differ (unless B_base == B_curr by chance)
    assert abs(ob_base.composition - ob_curr.composition) > 1e-6 or np.allclose(B_base, B_curr)


# ---------------------------------------------------------------------------
# Error: mismatched col_names
# ---------------------------------------------------------------------------

def test_ob_mismatched_col_names_raises():
    """ValueError when result_base and result_current have different col_names."""
    col_a = ["intercept", "gender_2"]
    col_b = ["intercept", "gender_2", "educ_2"]
    r_a = _make_result(np.zeros(2), np.zeros(2), col_a)
    r_b = _make_result(np.zeros(3), np.zeros(3), col_b)
    with pytest.raises(ValueError, match="col_names.*do not match"):
        oaxaca_blinder(r_a, r_b)
