"""Per-tree physical probability bar chart at a fixed β.

The widget exposes a β slider, a tree-count limit, and a sort dropdown so the
chart can be swept from β=0 to β_c. Replaces the matplotlib Slider from
data-analysis/tree_prob.py::TreePlt with native Qt controls.
"""

from __future__ import annotations

import matplotlib.image as mpimg
import numpy as np
from pathlib import Path
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.computations.utils import tree_image_path
from app.plots.base import BasePlot

_DEFAULT_SORT = "Tree ID"
_AVERAGE_SORT = "Average over selected primes"
_PRIME_PREFIX = "p = "


class ProbabilityPerTreePlot(BasePlot):
    supports_video = True

    def export_video(self, path: Path, fps: float = 10.0) -> None:
        from matplotlib.animation import FFMpegWriter, FuncAnimation

        beta_vals = self.computation.beta_vals
        saved_idx = self._beta_idx

        def update(frame_idx: int) -> list:
            self._beta_idx = frame_idx
            self._ax.clear()
            self._draw_for_state()
            return []

        anim = FuncAnimation(self.fig, update, frames=len(beta_vals), blit=False)
        anim.save(str(path), writer=FFMpegWriter(fps=fps))

        self._beta_idx = saved_idx
        self._ax.clear()
        self._draw_for_state()
        if hasattr(self, "_canvas"):
            self._canvas.draw_idle()

    def render(self) -> None:
        beta_vals = self.computation.beta_vals
        if len(beta_vals) == 0:
            self._stub("No β values to plot")
            return

        # Initial control state. widget() will create the actual Qt widgets.
        self._beta_idx = 0
        self._limit_enabled = False
        self._auto_scale = False
        self._sort_key = _DEFAULT_SORT
        n_total = len(self._all_tree_ids())
        self._n_limit = min(20, n_total)

        self._ax = self.fig.add_subplot(111)
        self._draw_for_state()

    def widget(self) -> QWidget:
        beta_vals = self.computation.beta_vals
        if len(beta_vals) == 0:
            return super().widget()

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addLayout(self._build_controls_row())
        layout.addLayout(self._build_slider_row())

        self._canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self._canvas, stretch=1)


        self._set_limit_controls_enabled(self._limit_enabled)
        return root

    # ---- widget construction ---------------------------------------------

    def _build_controls_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._limit_check = QCheckBox("Limit trees:")
        self._limit_check.setChecked(self._limit_enabled)
        self._limit_check.toggled.connect(self._on_limit_toggled)
        row.addWidget(self._limit_check)

        n_total = len(self._all_tree_ids())
        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, max(n_total, 1))
        self._limit_spin.setValue(self._n_limit)
        self._limit_spin.valueChanged.connect(self._on_n_changed)
        row.addWidget(self._limit_spin)

        row.addSpacing(16)

        self._sort_label = QLabel("Sort by:")
        row.addWidget(self._sort_label)

        self._sort_combo = QComboBox()
        self._sort_combo.addItem(_DEFAULT_SORT)
        for p in self.config.primes:
            self._sort_combo.addItem(f"{_PRIME_PREFIX}{p}")
        if len(self.config.primes) > 1:
            self._sort_combo.addItem(_AVERAGE_SORT)
        idx = self._sort_combo.findText(self._sort_key)
        if idx >= 0:
            self._sort_combo.setCurrentIndex(idx)
        self._sort_combo.currentTextChanged.connect(self._on_sort_changed)
        row.addWidget(self._sort_combo)

        row.addSpacing(16)

        self._auto_scale_check = QCheckBox("Auto-scale")
        self._auto_scale_check.setChecked(self._auto_scale)
        self._auto_scale_check.toggled.connect(self._on_auto_scale_toggled)
        row.addWidget(self._auto_scale_check)

        row.addStretch(1)
        return row

    def _build_slider_row(self) -> QHBoxLayout:
        beta_vals = self.computation.beta_vals
        row = QHBoxLayout()
        row.addWidget(QLabel("β"))

        self._beta_slider = QSlider(Qt.Orientation.Horizontal)
        self._beta_slider.setRange(0, len(beta_vals) - 1)
        self._beta_slider.setValue(self._beta_idx)
        self._beta_slider.valueChanged.connect(self._on_beta_changed)
        row.addWidget(self._beta_slider, stretch=1)

        self._beta_value_label = QLabel(self._format_beta(beta_vals[self._beta_idx]))
        self._beta_value_label.setMinimumWidth(70)
        row.addWidget(self._beta_value_label)
        return row

    # ---- signal handlers -------------------------------------------------

    def _on_limit_toggled(self, checked: bool) -> None:
        self._limit_enabled = checked
        self._set_limit_controls_enabled(checked)
        self._redraw()

    def _on_n_changed(self, value: int) -> None:
        self._n_limit = value
        if self._limit_enabled:
            self._redraw()

    def _on_sort_changed(self, text: str) -> None:
        self._sort_key = text
        self._redraw()

    def _on_auto_scale_toggled(self, checked: bool) -> None:
        self._auto_scale = checked
        self._redraw()

    def _on_beta_changed(self, idx: int) -> None:
        self._beta_idx = idx
        beta = float(self.computation.beta_vals[idx])
        self._beta_value_label.setText(self._format_beta(beta))
        self._redraw()

    def _set_limit_controls_enabled(self, enabled: bool) -> None:
        self._limit_spin.setEnabled(enabled)

    @staticmethod
    def _format_beta(beta: float) -> str:
        return f"{beta:.4f}"

    # ---- drawing ---------------------------------------------------------

    def _redraw(self) -> None:
        self._ax.clear()
        self._draw_for_state()
        if hasattr(self, "_canvas"):
            self._canvas.draw_idle()

    def _draw_for_state(self) -> None:
        beta = float(self.computation.beta_vals[self._beta_idx])
        df_beta = self.df.xs(beta, level="beta")
        pivot = df_beta["phys_prob"].unstack(level="prime")[self.config.primes]

        sort_col = self._sort_column(pivot, self._sort_key)
        if sort_col is not None:
            pivot = (
                pivot.assign(_sort=sort_col)
                .sort_values("_sort", ascending=False)
                .drop(columns="_sort")
            )
        if self._limit_enabled:
            pivot = pivot.head(self._n_limit)

        ax = self._ax
        pivot.plot(kind="bar", ax=ax, width=0.8, legend=True, rot=0)
        if not self._auto_scale:
            ax.set_ylim(0, 1)
        ax.set_ylabel("Probability")
        ax.set_title(
            f"Physical Probability per Tree (β={beta:.4f}, "
            f"q={self.config.charges})"
        )
        ax.legend(title="Prime p")

        tree_ids = list(pivot.index)
        max_image_ticks = 30
        if len(tree_ids) <= max_image_ticks:
            kept = list(range(len(tree_ids)))
        else:
            stride = int(np.ceil(len(tree_ids) / max_image_ticks))
            kept = list(range(0, len(tree_ids), stride))
        self._draw_tree_image_ticks(ax, tree_ids, kept)

    def _sort_column(self, pivot: pd.DataFrame, key: str) -> pd.Series | None:
        if key == _DEFAULT_SORT:
            return None
        if key == _AVERAGE_SORT:
            return pivot.mean(axis=1)
        if key.startswith(_PRIME_PREFIX):
            try:
                p = int(key[len(_PRIME_PREFIX):])
            except ValueError:
                return None
            if p in pivot.columns:
                return pivot[p]
        return None

    def _all_tree_ids(self) -> list[int]:
        return list(self.df.index.get_level_values("tree_id").unique())

    def _draw_tree_image_ticks(self, ax: Axes, tree_ids: list[int], kept: list[int]) -> None:
        """Replace x-tick labels with the per-tree thumbnails from `out/treesN/`.

        Falls back to numeric labels for any tree whose image is missing.
        """
        n = self.computation.n
        zoom = self._tick_image_zoom(len(kept))

        text_labels: dict[int, str] = {}
        ax.set_xticks(kept)
        ax.set_xticklabels(["" for _ in kept])
        # ax.tick_params(axis="x", which="both", length=0, pad=2)

        for x in kept:
            tid = tree_ids[x]
            path = tree_image_path(n, tid)
            if not path.exists():
                text_labels[x] = str(tid)
                continue
            img = mpimg.imread(str(path))
            ab = AnnotationBbox(
                OffsetImage(img, zoom=zoom),
                (x, 0),
                xybox=(0, -8),
                xycoords=("data", "axes fraction"),
                boxcoords="offset points",
                box_alignment=(0.5, 1.0),
                frameon=False,
                pad=0,
            )
            ax.add_artist(ab)

        if text_labels:
            ax.set_xticklabels(
                [text_labels.get(x, "") for x in kept]
            )

        # Reserve space below for the thumbnails (matches _IMAGE_MARGIN_FRAC).
        self.fig.subplots_adjust(bottom=self._IMAGE_MARGIN_FRAC + 0.04)
        ax.set_xlabel("")

    # Each thumbnail width = this fraction of figure width / n_kept.
    _IMAGE_WIDTH_FRAC = 0.70
    # Hard cap: thumbnails never taller than this fraction of figure height.
    _IMAGE_MAX_HEIGHT_FRAC = 0.05
    # Bottom margin accommodates the capped image height plus a small gap.
    _IMAGE_MARGIN_FRAC = _IMAGE_MAX_HEIGHT_FRAC + 0.02
    # Native image dimensions in pixels (output of data-analysis/tree_viz.py).
    _NATIVE_IMAGE_WIDTH_PX = 400
    _NATIVE_IMAGE_HEIGHT_PX = 370

    def _tick_image_zoom(self, n_kept: int) -> float:
        n_kept = max(n_kept, 1)
        fig_w_px, fig_h_px = [s * self.fig.dpi for s in self.fig.get_size_inches()]
        zoom_by_width = (fig_w_px * self._IMAGE_WIDTH_FRAC / n_kept) / self._NATIVE_IMAGE_WIDTH_PX
        zoom_by_height = (fig_h_px * self._IMAGE_MAX_HEIGHT_FRAC) / self._NATIVE_IMAGE_HEIGHT_PX
        print("w:", zoom_by_width, "h:", zoom_by_height)
        print("n:", n_kept, "w_px", fig_w_px, "h_px", fig_h_px)
        return min(zoom_by_width, zoom_by_height)
