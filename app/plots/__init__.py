"""Catalog of plots CANO.PY can produce.

The launch window reads PLOT_SPECS to render checkboxes; the run window reads
PLOT_REGISTRY to instantiate the right plot class for each selected key.
Add new plots as a module in this package and register them below.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import matplotlib as mpl

mpl.rcParams.update(
    {
        # "text.usetex": True,
        "text.latex.preamble": r"\usepackage{lmodern}\usepackage{amsfonts}\renewcommand{\familydefault}{\sfdefault}",
    }
)


class PlotKind(Enum):
    BETA = "β-valued plots"  # x-axis = β, one line per prime
    PER_TREE = "Per-tree plots"  # x-axis = tree id, bar chart at a chosen β


@dataclass(frozen=True)
class PlotSpec:
    key: str
    label: str
    kind: PlotKind


@dataclass
class RunConfig:
    charges: list[int]
    primes: list[int]
    beta_step: float
    plot_keys: list[str] = field(default_factory=list)


PLOT_SPECS: tuple[PlotSpec, ...] = (
    PlotSpec("partition", "Partition Function", PlotKind.BETA),
    PlotSpec("probability_per_tree", "Probability per Tree", PlotKind.PER_TREE),
    PlotSpec("expected_alteration", "Expected Alteration", PlotKind.BETA),
    PlotSpec("alteration_per_tree", "Alteration per Tree", PlotKind.PER_TREE),
    PlotSpec("max_quotient", "Max Quotient per Beta", PlotKind.BETA),
    PlotSpec("quotient_per_tree", "Quotient per tree", PlotKind.PER_TREE),
)


from app.plots.alteration_per_tree import AlterationPerTreePlot
from app.plots.base import BasePlot
from app.plots.expected_alteration import ExpectedAlterationPlot
from app.plots.max_quotient import MaxQuotientPlot
from app.plots.partition import PartitionPlot
from app.plots.probability_per_tree import ProbabilityPerTreePlot
from app.plots.quotient_per_tree import QuotientPerTreePlot

PLOT_REGISTRY: dict[str, type[BasePlot]] = {
    "partition": PartitionPlot,
    "probability_per_tree": ProbabilityPerTreePlot,
    "expected_alteration": ExpectedAlterationPlot,
    "alteration_per_tree": AlterationPerTreePlot,
    "max_quotient": MaxQuotientPlot,
    "quotient_per_tree": QuotientPerTreePlot,
}

SPEC_BY_KEY: dict[str, PlotSpec] = {s.key: s for s in PLOT_SPECS}

__all__ = [
    "PlotKind",
    "PlotSpec",
    "RunConfig",
    "PLOT_SPECS",
    "PLOT_REGISTRY",
    "SPEC_BY_KEY",
    "BasePlot",
]
