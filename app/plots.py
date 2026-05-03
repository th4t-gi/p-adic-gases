"""Catalog of plots CANO.PY can produce.

Shared between the launch window (presents checkboxes) and the run window
(consumes the selection to decide which columns to compute / which figures to
draw). Add new plots here rather than wiring them in two places.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlotKind(Enum):
    BETA = "β-valued plots"  # x-axis = β, one line per prime
    PER_TREE = "Per-tree plots"  # x-axis = tree id, bar chart at a chosen β


@dataclass(frozen=True)
class PlotSpec:
    key: str
    label: str
    kind: PlotKind


PLOT_SPECS: tuple[PlotSpec, ...] = (
    PlotSpec("partition", "Z_N(β)", PlotKind.BETA),
    PlotSpec("probability_per_tree", "Probability per Tree", PlotKind.PER_TREE),
    PlotSpec("expected_alteration", "Expected Alteration", PlotKind.BETA),
    PlotSpec("alteration_per_tree", "Alteration per Tree", PlotKind.PER_TREE),
    PlotSpec("quotient_per_tree", "Quotient per tree", PlotKind.PER_TREE),
)
