from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.computations.computation import RunComputation
from app.plots import PLOT_REGISTRY, SPEC_BY_KEY, RunConfig


class RunWindow(QMainWindow):
    _next_run_number = 1

    def __init__(self, config: RunConfig) -> None:
        super().__init__()

        run_number = RunWindow._next_run_number
        RunWindow._next_run_number += 1
        self.setWindowTitle(f"Run #{run_number}")
        self.resize(900, 600)

        self._config = config
        self._computation = RunComputation(config)
        df = self._computation.run()

        tabs = QTabWidget()
        self._plots = []
        for key in config.plot_keys:
            spec = SPEC_BY_KEY.get(key)
            cls = PLOT_REGISTRY.get(key)
            if spec is None or cls is None:
                continue
            plot = cls(df, self._computation)
            plot.render()
            self._plots.append(plot)
            tabs.addTab(plot.widget(), spec.label)

        if tabs.count() == 0:
            empty = QLabel("No plots selected.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tabs.addTab(empty, "—")

        exit_btn = QPushButton("Close")
        exit_btn.clicked.connect(self.close)
        exit_btn.setDefault(True)
        export_btn = QPushButton("Export to")

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(export_btn)
        button_row.addWidget(exit_btn)

        body = QVBoxLayout()
        body.addWidget(tabs)
        body.addLayout(button_row)

        central = QWidget()
        central.setLayout(body)
        self.setCentralWidget(central)
