# Perturbation experiment: how much does the underlying estimate move per unit
# of data degradation? Bounds the PUMF-vs-master irreducible floor.
#
# SAFETY: in-memory only. Calls _compute_one_yoy (no cache writes) on frames
# loaded via harmonize() (read-only parquet read). Never calls _save_cache,
# get_month, or anything that writes under data/.
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
sys.path.insert(0, str(ROOT))
OUT = ROOT / "claude-ref" / "research" / "lfs_micro" / "audit_2026-06-09" / "forensics"

from pipeline.lfs_pumf.harmonize import harmonize  # noqa: E402
from pipeline.lfs_micro.engine import _compute_one_yoy, _subtract_12_months  # noqa: E402
from pipeline.lfs_micro.spec import DEFAULT_SPEC  # noqa: E402

PUMF = ROOT / "data" / "raw" / "lfs_pumf"

# Stratified sample of month-pairs (incl. worst-miss months 2018-05, 2020-06)
MONTHS = ["2016-06", "2018-05", "2019-08", "2020-06",
          "2021-09", "2023-03", "2024-07", "2025-10"]

def degrade(df, mode):
    d = df.copy()
    if mode == "base":
        return d
    if mode == "wage_round_50c":
        d["wage"] = (d["wage"] * 2).round() / 2
    elif mode == "wage_round_1d":
        d["wage"] = d["wage"].round()
    elif mode == "topcode_p99":
        cap = d["wage"].quantile(0.99)
        d["wage"] = d["wage"].clip(upper=cap)
    elif mode == "coarse_noc9":
        # collapse 43 occupation sub-major groups into 9 bands (~one notch of
        # category detail, simulating PUMF-vs-master granularity in reverse)
        d["noc_43"] = (d["noc_43"] - 1) // 5 + 1
    elif mode == "coarse_noc9_naics7":
        d["noc_43"] = (d["noc_43"] - 1) // 5 + 1
        d["naics_21"] = (d["naics_21"] - 1) // 3 + 1
    else:
        raise ValueError(mode)
    return d

MODES = ["base", "wage_round_50c", "wage_round_1d", "topcode_p99",
         "coarse_noc9", "coarse_noc9_naics7"]

rows = []
for key in MONTHS:
    kb = _subtract_12_months(key)
    pc, pb = PUMF / f"{key}.parquet", PUMF / f"{kb}.parquet"
    if not pc.exists() or not pb.exists():
        print(f"skip {key}: parquet missing", flush=True)
        continue
    fc, fb = harmonize(pc), harmonize(pb)
    for mode in MODES:
        t0 = time.time()
        row = _compute_one_yoy(key, degrade(fc, mode), degrade(fb, mode),
                               DEFAULT_SPEC)
        el = time.time() - t0
        if row is None:
            print(f"{key} {mode}: FAILED", flush=True)
            continue
        rows.append({"month": key, "mode": mode,
                     "underlying_lp": row["underlying_lp"],
                     "composition_lp": row["composition_lp"],
                     "n_obs": row["n_obs_curr"]})
        print(f"{key} {mode:20s} underlying={row['underlying_lp']*100:.4f}lp "
              f"comp={row['composition_lp']*100:.4f}lp ({el:.0f}s)", flush=True)

df = pd.DataFrame(rows)
df.to_csv(OUT / "perturbation_results.csv", index=False)

print("\n=== Deltas vs base (pp, log-points x100) ===")
piv = df.pivot(index="month", columns="mode", values="underlying_lp") * 100
for mode in MODES[1:]:
    if mode in piv:
        d = piv[mode] - piv["base"]
        print(f"{mode:20s} mean={d.mean():+.4f} sd={d.std(ddof=1):.4f} "
              f"max|d|={d.abs().max():.4f}")
print("\nComposition deltas:")
pivc = df.pivot(index="month", columns="mode", values="composition_lp") * 100
for mode in MODES[1:]:
    if mode in pivc:
        d = pivc[mode] - pivc["base"]
        print(f"{mode:20s} mean={d.mean():+.4f} sd={d.std(ddof=1):.4f} "
              f"max|d|={d.abs().max():.4f}")
print("\nWrote", OUT / "perturbation_results.csv")
