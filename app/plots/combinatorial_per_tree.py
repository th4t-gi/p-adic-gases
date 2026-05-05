"""Per-tree combinatorial term bar chart at a fixed β."""

from __future__ import annotations

from app.plots.per_tree_base import PerTreePlot


class CombinatorialPerTreePlot(PerTreePlot):
    _value_column = "comb_term"
    _y_label = r"$C_\pitchfork(p)$"
    _title_prefix = "Combinatorial Term per Tree"
    _default_auto_scale = True
    _supports_log_y = True
    _has_beta_slider = False
    supports_video = False
