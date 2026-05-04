"""Run the computation for preset configs and print a summary.

Run from the repo root:

    .venv/bin/python app/computation.test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.computations.computation import RunComputation  # noqa: E402
from app.plots import RunConfig  # noqa: E402

CASES = [
    # ("n3", [1, -1, 1]),
    ("n4", [1, 1, -1, -1]),
    # ("n5", [2, -2, 1, -1, 1]),
]
PRIMES = [2, 3, 5]
BETA_STEP = 0.05


def run_case(label: str, charges: list[int]) -> None:
    config = RunConfig(charges=charges, primes=PRIMES, beta_step=BETA_STEP)
    computation = RunComputation(config)
    df = computation.run()

    print(f"\n{'='*60}")
    print(f"{label}: charges={charges}, primes={PRIMES}, β_step={BETA_STEP}")
    print(f"  β range:  [{computation.beta_vals[0]:.4f}, {computation.beta_vals[-1]:.4f}]  ({len(computation.beta_vals)} values)")
    print(f"  trees:    {df.index.get_level_values('tree_id').nunique()}")
    print(f"  df shape: {df.shape}")
    print(df)


def main() -> int:
    for label, charges in CASES:
        run_case(label, charges)
    return 0


if __name__ == "__main__":
    sys.exit(main())
