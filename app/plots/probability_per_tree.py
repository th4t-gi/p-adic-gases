"""Per-tree physical probability bar chart at a fixed β."""

from __future__ import annotations

from app.plots.per_tree_base import PerTreePlot


class ProbabilityPerTreePlot(PerTreePlot):
    _value_column = "phys_prob"
    _y_label = "Probability"
    _title_prefix = "Physical Probability per Tree"
    _fixed_ylim = (0.0, 1.0)
    _default_auto_scale = False
