"""Per-tree quotient (phys_term) bar chart at a fixed β."""

from __future__ import annotations

from app.plots.per_tree_base import PerTreePlot


class QuotientPerTreePlot(PerTreePlot):
    _value_column = "phys_term"
    _y_label = r"$Q_\pitchfork(\beta)$"
    _title_prefix = "Quotient per Tree"
    _default_auto_scale = True
    _supports_log_y = True
