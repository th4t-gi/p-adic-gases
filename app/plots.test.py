"""Render the probability_per_tree plot for N=3, 4, and 5 charges.

Run from the repo root:

    .venv/bin/python -m app.plots.test       # name has a dot, so use the path:
    .venv/bin/python app/plots.test.py

Requires a QApplication, but works headlessly via QT_QPA_PLATFORM=offscreen.
Each rendered figure is written to out/test_plots/.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running as a script from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from app.computations.computation import RunComputation  # noqa: E402
from app.plots import PLOT_REGISTRY, RunConfig  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "out" / "test_plots"

CASES = [
    ("n3", [1, -1, 1]),
    ("n4", [1, 1, -1, -1]),
    ("n5", [2, -2, 1, -1, 1]),
]
PRIMES = [2, 3, 5]
BETA_STEP = 0.05


def render_case(label: str, charges: list[int]) -> Path:
    config = RunConfig(
        charges=charges,
        primes=PRIMES,
        beta_step=BETA_STEP,
        plot_keys=["probability_per_tree"],
    )
    computation = RunComputation(config)
    df = computation.run()

    plot_cls = PLOT_REGISTRY["probability_per_tree"]
    plot = plot_cls(df, computation)
    plot.render()
    plot.fig.canvas.draw()

    out_path = OUTPUT_DIR / f"probability_per_tree_{label}.png"
    plot.fig.savefig(out_path, dpi=120)
    return out_path


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    QApplication(sys.argv)

    for label, charges in CASES:
        out = render_case(label, charges)
        print(f"{label}: charges={charges} -> {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
