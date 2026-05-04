from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import APP_NAME, APP_TITLE, APP_SUBTITLE
from app.computations.physics import beta_critical, beta_value_count
from app.computations.utils import parse_int_list, phylogenetic_tree_count
from app.plots import PLOT_SPECS, PlotKind, RunConfig
from app.windows.run_window import RunWindow


class LaunchWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumWidth(400)

        self._open_runs: list[RunWindow] = []
        self._plot_checkboxes: dict[str, QCheckBox] = {}

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self.charges_input = QLineEdit("1,-1,1")
        self.charges_input.setPlaceholderText("e.g. 2, -2, 1, -1, 1")

        self.primes_input = QLineEdit("2,3,5")
        self.primes_input.setPlaceholderText("e.g. 2, 3, 5, 7, 11")

        self.step_input = QDoubleSpinBox()
        self.step_input.setDecimals(5)
        self.step_input.setRange(1e-5, 1.0)
        self.step_input.setSingleStep(1e-5)
        self.step_input.setValue(0.001)

        self.beta_c_label = QLabel()
        self.beta_count_label = QLabel()
        self.computations_label = QLabel()
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #d33;")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)

        form = QFormLayout()
        form.addRow("Charges:", self.charges_input)
        form.addRow("Primes:", self.primes_input)
        form.addRow("β resolution:", self.step_input)
        form.addRow("β_c:", self.beta_c_label)
        form.addRow("# of β values:", self.beta_count_label)
        form.addRow("Total Computations:", self.computations_label)

        plots_group = QVBoxLayout()
        plots_group.setContentsMargins(16, 0, 16, 0)
        for kind in PlotKind:
            specs = [s for s in PLOT_SPECS if s.kind is kind]
            if not specs:
                continue
            group = QGroupBox(kind.value)
            group_layout = QVBoxLayout(group)
            for spec in specs:
                checkbox = QCheckBox(spec.label)
                if spec.key in ["partition", "probability_per_tree"]:
                    checkbox.setChecked(True)
                self._plot_checkboxes[spec.key] = checkbox
                group_layout.addWidget(checkbox)
            # group_layout.addStretch(1)
            plots_group.addWidget(group)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self._open_run_window)
        self.run_btn.setDefault(True)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(self.run_btn)

        body = QVBoxLayout()
        body.addWidget(title)
        body.addWidget(subtitle)
        body.addSpacing(16)
        body.addLayout(form)
        body.addLayout(plots_group)
        body.addWidget(self.error_label)
        body.addLayout(button_row)

        central = QWidget()
        central.setLayout(body)
        self.setCentralWidget(central)

        self.charges_input.textChanged.connect(self._update_feedback_labels)
        self.primes_input.textChanged.connect(self._update_feedback_labels)
        self.step_input.valueChanged.connect(self._update_feedback_labels)
        self._update_feedback_labels()

        self.adjustSize()

    def _update_feedback_labels(self) -> None:
        try:
            charges = parse_int_list(self.charges_input.text())
            primes = parse_int_list(self.primes_input.text())
            if not charges or not primes:
                self.beta_c_label.clear()
                self.beta_count_label.clear()
                self.computations_label.clear()
                return

            step = self.step_input.value()
            bc = beta_critical(charges)
            count = beta_value_count(charges, step)
            tree_count = phylogenetic_tree_count(len(charges))
            total = count * len(primes) * tree_count

            self.beta_c_label.setText(f"{bc:g}")
            self.beta_count_label.setText(f"{count}")
            self.computations_label.setText(f"{total:,}")
        except ValueError:
            self.beta_c_label.setText("—")
            self.beta_count_label.setText("—")
            self.computations_label.setText("—")

    def _is_prime(self, value: int) -> bool:
        if value < 2:
            return False
        if value == 2:
            return True
        if value % 2 == 0:
            return False
        for divisor in range(3, int(value**0.5) + 1, 2):
            if value % divisor == 0:
                return False
        return True

    def _validate_inputs(self) -> bool:
        errors: list[str] = []

        try:
            charges = parse_int_list(self.charges_input.text())
            if not charges:
                errors.append("Enter at least one charge.")
        except ValueError as e:
            errors.append(str(e))

        try:
            primes = parse_int_list(self.primes_input.text())
            if not primes:
                errors.append("Enter at least one prime.")
            else:
                non_primes = [p for p in primes if not self._is_prime(p)]
                if non_primes:
                    errors.append("Invalid list of primes.")
        except ValueError as e:
            errors.append(str(e))

        if not self.selected_plot_keys():
            errors.append("Select at least one plot.")

        if errors:
            self.error_label.setVisible(True)
            self.error_label.setText("\n".join(errors))
            return False

        self.error_label.setVisible(False)
        return True

    def selected_plot_keys(self) -> list[str]:
        return [key for key, cb in self._plot_checkboxes.items() if cb.isChecked()]

    def _open_run_window(self) -> None:
        if not self._validate_inputs():
            return

        config = RunConfig(
            charges=parse_int_list(self.charges_input.text()),
            primes=parse_int_list(self.primes_input.text()),
            beta_step=self.step_input.value(),
            plot_keys=self.selected_plot_keys(),
        )
        run_window = RunWindow(config)
        run_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        run_window.destroyed.connect(lambda: self._open_runs.remove(run_window))
        self._open_runs.append(run_window)
        run_window.show()
