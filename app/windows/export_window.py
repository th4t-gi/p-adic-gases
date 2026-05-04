from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.plots import PlotSpec
from app.plots.base import BasePlot

_FORMAT_IMAGE = "Image (PNG)"
_FORMAT_VIDEO = "Video (MP4)"
_DEFAULT_DURATION_S = 10.0


class ExportWindow(QDialog):
    def __init__(self, plots: list[tuple[PlotSpec, BasePlot]], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Plots")
        self.setMinimumWidth(340)

        self._rows: list[tuple[QCheckBox, QComboBox | None, QDoubleSpinBox | None, PlotSpec, BasePlot]] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        for spec, plot in plots:
            row = QHBoxLayout()
            cb = QCheckBox(spec.label)
            cb.setChecked(True)
            row.addWidget(cb, stretch=1)

            combo: QComboBox | None = None
            dur_spin: QDoubleSpinBox | None = None

            if getattr(plot, "supports_video", False):
                combo = QComboBox()
                combo.addItem(_FORMAT_IMAGE)
                combo.addItem(_FORMAT_VIDEO)
                row.addWidget(combo)

                dur_widget = QWidget()
                dur_layout = QHBoxLayout(dur_widget)
                dur_layout.setContentsMargins(20, 0, 0, 0)
                dur_layout.addWidget(QLabel("Duration (seconds):"))
                dur_spin = QDoubleSpinBox()
                dur_spin.setRange(1.0, 600.0)
                dur_spin.setValue(_DEFAULT_DURATION_S)
                dur_spin.setSingleStep(1.0)
                dur_spin.setDecimals(1)
                dur_layout.addWidget(dur_spin)
                dur_layout.addStretch(1)
                dur_widget.setVisible(False)

                combo.currentTextChanged.connect(
                    lambda text, w=dur_widget: w.setVisible(text == _FORMAT_VIDEO)
                )

                layout.addLayout(row)
                layout.addWidget(dur_widget)
            else:
                layout.addLayout(row)

            self._rows.append((cb, combo, dur_spin, spec, plot))

        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Output folder:"))
        self._dir_edit = QLineEdit(str(Path(__file__).resolve().parents[2] / "out"))
        dir_row.addWidget(self._dir_edit, stretch=1)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse)
        dir_row.addWidget(browse_btn)
        layout.addLayout(dir_row)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        self._export_btn = QPushButton("Export")
        self._export_btn.setDefault(True)
        self._export_btn.clicked.connect(self._do_export)
        btn_row.addWidget(self._export_btn)
        layout.addLayout(btn_row)

        self.adjustSize()

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select output folder", self._dir_edit.text())
        if path:
            self._dir_edit.setText(path)

    def _do_export(self) -> None:
        selected = [r for r in self._rows if r[0].isChecked()]
        if not selected:
            return

        out_dir = Path(self._dir_edit.text())
        out_dir.mkdir(parents=True, exist_ok=True)

        self._progress.setMaximum(len(selected))
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._export_btn.setEnabled(False)

        try:
            for i, (_, combo, dur_spin, spec, plot) in enumerate(selected):
                as_video = combo is not None and combo.currentText() == _FORMAT_VIDEO
                ext = "mp4" if as_video else "png"
                out_path = out_dir / f"{spec.key}.{ext}"
                if as_video:
                    duration = dur_spin.value() if dur_spin is not None else _DEFAULT_DURATION_S
                    n_frames = len(plot.computation.beta_vals)
                    fps = n_frames / duration
                    plot.export_video(out_path, fps=fps)
                else:
                    plot.fig.savefig(str(out_path), dpi=150, bbox_inches="tight")
                self._progress.setValue(i + 1)
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
        finally:
            self._export_btn.setEnabled(True)
            self._progress.setVisible(False)

        self.accept()
