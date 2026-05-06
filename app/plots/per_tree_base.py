"""Shared base for per-tree bar-chart plots with a β slider.

Subclasses configure behaviour via class attributes:

    _value_column         — DataFrame column to plot (e.g. "phys_prob")
    _y_label              — y-axis label string
    _title_prefix         — prefix for the plot title
    _fixed_ylim           — (lo, hi) applied when auto-scale is off; None = skip
    _default_auto_scale   — initial state of the auto-scale checkbox
    _default_log_y        — initial state of the log-y checkbox
    _default_p_trees_only — initial state of the p-trees-only checkbox
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
import mplcursors
import numpy as np
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
_FILTER_ALL = "All"


class PerTreePlot(BasePlot):
    # ---- subclass configuration ------------------------------------------
    _value_column: str = "phys_prob"
    _y_label: str = "Value"
    _title_prefix: str = "Value per Tree"
    _fixed_ylim: tuple[float, float] | None = None
    _default_auto_scale: bool = True
    _default_log_y: bool = False
    _default_p_trees_only: bool = False
    _has_beta_slider: bool = True

    supports_video = True

    # ---- lifecycle -------------------------------------------------------

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

        self.fig.set_layout_engine(None)
        self._beta_idx = 0
        self._auto_scale = self._default_auto_scale
        self._log_y = self._default_log_y
        self._p_trees_only = self._default_p_trees_only
        self._show_tree_images = False
        self._sort_key = _DEFAULT_SORT
        self._filter_p = _FILTER_ALL
        n_total = len(self._all_tree_ids())
        if self.computation.n >= 5:
            self._limit_enabled = True
            self._n_limit = min(200, n_total)
        else:
            self._limit_enabled = False
            self._n_limit = min(20, n_total)

        self._ax = self.fig.add_subplot(111)
        self._draw_for_state()

    def widget(self) -> QWidget:
        if len(self.computation.beta_vals) == 0:
            return super().widget()

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addLayout(self._build_controls_row())
        if self._has_beta_slider:
            layout.addLayout(self._build_slider_row())

        self._canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self._canvas, stretch=1)

        self._set_limit_controls_enabled(self._limit_enabled)
        return root

    # ---- widget construction ---------------------------------------------

    def _build_controls_row(self) -> QVBoxLayout:
        outer = QVBoxLayout()
        outer.setSpacing(4)

        # ---- row 1: data controls ----------------------------------------
        top = QHBoxLayout()
        top.addStretch(1)

        self._limit_check = QCheckBox("Limit trees:")
        self._limit_check.setChecked(self._limit_enabled)
        self._limit_check.toggled.connect(self._on_limit_toggled)
        top.addWidget(self._limit_check)

        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, max(len(self._all_tree_ids()), 1))
        self._limit_spin.setValue(self._n_limit)
        self._limit_spin.valueChanged.connect(self._on_n_changed)
        top.addWidget(self._limit_spin)

        top.addSpacing(16)
        top.addWidget(QLabel("Sort by:"))

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
        top.addWidget(self._sort_combo)

        if len(self.config.primes) > 1:
            top.addSpacing(16)
            top.addWidget(QLabel("Filter by p:"))
            self._filter_p_combo = QComboBox()
            self._filter_p_combo.addItem(_FILTER_ALL)
            for p in self.config.primes:
                self._filter_p_combo.addItem(f"{_PRIME_PREFIX}{p}")
            idx = self._filter_p_combo.findText(self._filter_p)
            if idx >= 0:
                self._filter_p_combo.setCurrentIndex(idx)
            self._filter_p_combo.currentTextChanged.connect(self._on_filter_p_changed)
            top.addWidget(self._filter_p_combo)

        top.addStretch(1)
        outer.addLayout(top)

        # ---- row 2: view toggles -----------------------------------------
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self._auto_scale_check = QCheckBox("Auto-scale")
        self._auto_scale_check.setChecked(self._auto_scale)
        self._auto_scale_check.toggled.connect(self._on_auto_scale_toggled)
        bottom.addWidget(self._auto_scale_check)

        bottom.addSpacing(16)
        self._log_check = QCheckBox("Log y")
        self._log_check.setChecked(self._log_y)
        self._log_check.toggled.connect(self._on_log_toggled)
        bottom.addWidget(self._log_check)

        bottom.addSpacing(16)
        self._p_trees_check = QCheckBox("p-trees only")
        self._p_trees_check.setChecked(self._p_trees_only)
        self._p_trees_check.toggled.connect(self._on_p_trees_toggled)
        bottom.addWidget(self._p_trees_check)

        bottom.addSpacing(16)
        self._show_images_check = QCheckBox("Tree images")
        self._show_images_check.setChecked(self._show_tree_images)
        self._show_images_check.toggled.connect(self._on_show_images_toggled)
        bottom.addWidget(self._show_images_check)

        self._extra_controls(bottom)
        bottom.addStretch(1)
        outer.addLayout(bottom)

        return outer

    def _extra_controls(self, row: QHBoxLayout) -> None:
        """Hook for subclasses to append controls before the trailing stretch."""

    def _filter_pivot(self, pivot):
        if not self._p_trees_only:
            return pivot
        trees_df = self.computation._trees_df
        if self._filter_p != _FILTER_ALL and self._filter_p.startswith(_PRIME_PREFIX):
            try:
                p = int(self._filter_p[len(_PRIME_PREFIX):])
            except ValueError:
                p = max(self.config.primes)
        else:
            p = max(self.config.primes)
        is_p_tree = trees_df[f"is_{p}_tree"].reindex(pivot.index).fillna(False)
        return pivot[is_p_tree]

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

    def _on_filter_p_changed(self, text: str) -> None:
        self._filter_p = text
        self._update_sort_combo()
        self._redraw()

    def _update_sort_combo(self) -> None:
        if not hasattr(self, "_sort_combo"):
            return
        current = self._sort_combo.currentText()
        self._sort_combo.blockSignals(True)
        self._sort_combo.clear()
        self._sort_combo.addItem(_DEFAULT_SORT)
        if self._filter_p == _FILTER_ALL:
            for p in self.config.primes:
                self._sort_combo.addItem(f"{_PRIME_PREFIX}{p}")
            if len(self.config.primes) > 1:
                self._sort_combo.addItem(_AVERAGE_SORT)
        else:
            self._sort_combo.addItem(self._filter_p)
        idx = self._sort_combo.findText(current)
        if idx >= 0:
            self._sort_combo.setCurrentIndex(idx)
        else:
            self._sort_combo.setCurrentIndex(0)
            self._sort_key = _DEFAULT_SORT
        self._sort_combo.blockSignals(False)

    def _on_auto_scale_toggled(self, checked: bool) -> None:
        self._auto_scale = checked
        self._redraw()

    def _on_log_toggled(self, checked: bool) -> None:
        self._log_y = checked
        self._redraw()

    def _on_p_trees_toggled(self, checked: bool) -> None:
        self._p_trees_only = checked
        self._redraw()

    def _on_show_images_toggled(self, checked: bool) -> None:
        self._show_tree_images = checked
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
        if hasattr(self, "_hover_cursor"):
            self._hover_cursor.remove()
            del self._hover_cursor
        self._ax.clear()
        self._draw_for_state()
        if hasattr(self, "_canvas"):
            self._canvas.draw_idle()

    def _draw_for_state(self) -> None:
        beta = float(self.computation.beta_vals[self._beta_idx if self._has_beta_slider else 0])
        df_beta = self.df.xs(beta, level="beta")
        pivot = df_beta[self._value_column].unstack(level="prime")[self.config.primes]
        if self._filter_p != _FILTER_ALL and self._filter_p.startswith(_PRIME_PREFIX):
            try:
                p = int(self._filter_p[len(_PRIME_PREFIX):])
            except ValueError:
                p = None
            if p in pivot.columns:
                pivot = pivot[[p]]
        pivot = self._filter_pivot(pivot)

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

        if self._log_y:
            ax.set_yscale("log")
        elif not self._auto_scale and self._fixed_ylim is not None:
            ax.set_ylim(*self._fixed_ylim)

        ax.set_ylabel(self._y_label)
        ax.set_title(f"{self._title_prefix} (β={beta:.4f}, q={self.config.charges})")
        ax.legend(title="Prime p")

        tree_ids = list(pivot.index)
        max_image_ticks = 30
        if len(tree_ids) <= max_image_ticks:
            kept = list(range(len(tree_ids)))
        else:
            stride = int(np.ceil(len(tree_ids) / max_image_ticks))
            kept = list(range(0, len(tree_ids), stride))
        self._draw_tree_image_ticks(ax, tree_ids, kept)
        self._attach_hover_tooltip(ax, tree_ids)

    def _attach_hover_tooltip(self, ax: Axes, tree_ids: list[int]) -> None:
        bar_containers = [c for c in ax.containers if hasattr(c, "patches")]
        if not bar_containers:
            return

        self._hover_cursor = mplcursors.cursor(bar_containers, hover=mplcursors.HoverMode.Transient)
        n = self.computation.n

        @self._hover_cursor.connect("add")
        def _on_add(sel) -> None:
            bar_idx = sel.index
            if not (0 <= bar_idx < len(tree_ids)):
                return
            tid = tree_ids[bar_idx]
            sel.annotation.set_text(f"")
            sel.annotation.arrow_patch.set_visible(False)
            path = tree_image_path(n, tid)
            if not path.exists():
                sel.annotation.set_text(f"Tree {tid}")
                sel.annotation.arrow_patch.set_visible(True)
                return
            img = mpimg.imread(str(path))
            ab = AnnotationBbox(
                OffsetImage(img, zoom=0.15),
                sel.target,
                xybox=(0, 30),
                xycoords="data",
                boxcoords="offset points",
                frameon=True,
                pad=0.1,
            )
            ax.add_artist(ab)
            sel.extras.append(ab)

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
        ax.set_xticks(kept)
        ax.set_xlabel("")

        if not self._show_tree_images:
            ax.set_xticklabels([str(tree_ids[x]) for x in kept])
            self.fig.subplots_adjust(left=self._LEFT_MARGIN, right=self._RIGHT_MARGIN, top=self._TOP_MARGIN, bottom=0.12)
            return

        n = self.computation.n
        zoom = self._tick_image_zoom()

        text_labels: dict[int, str] = {}
        ax.set_xticklabels(["" for _ in kept])

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
            ax.set_xticklabels([text_labels.get(x, "") for x in kept])

        self.fig.subplots_adjust(
            left=self._LEFT_MARGIN,
            right=self._RIGHT_MARGIN,
            top=self._TOP_MARGIN,
            bottom=self._IMAGE_MARGIN_FRAC + 0.04,
        )

    _IMAGE_WIDTH_FRAC = 0.03
    _IMAGE_MARGIN_FRAC = 0.05
    _NATIVE_IMAGE_WIDTH_PX = 400
    # Fixed plot-area margins so toggling auto-scale (y-tick label width changes)
    # doesn't reshape the bar area horizontally.
    _LEFT_MARGIN = 0.12
    _RIGHT_MARGIN = 0.95
    _TOP_MARGIN = 0.92

    def _tick_image_zoom(self) -> float:
        fig_w_px = self.fig.get_size_inches()[0] * self.fig.dpi
        return (fig_w_px * self._IMAGE_WIDTH_FRAC) / self._NATIVE_IMAGE_WIDTH_PX
