"""Per-tree alteration bar chart at a fixed β."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox

from app.plots.per_tree_base import PerTreePlot


class AlterationPerTreePlot(PerTreePlot):
    _value_column = "alteration"
    _y_label = "Alteration"
    _title_prefix = "Alteration per Tree"
    _default_auto_scale = True

    def _extra_controls(self, row: QHBoxLayout) -> None:
        row.addSpacing(16)
        row.addWidget(QLabel("Next charge:"))
        self._next_charge_spin = QSpinBox()
        self._next_charge_spin.setRange(-9999, 9999)
        self._next_charge_spin.setValue(1)
        row.addWidget(self._next_charge_spin)
