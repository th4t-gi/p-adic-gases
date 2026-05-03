from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RunWindow(QMainWindow):
    _next_run_number = 1

    def __init__(self) -> None:
        super().__init__()

        run_number = RunWindow._next_run_number
        RunWindow._next_run_number += 1
        self.setWindowTitle(f"Run #{run_number}")
        self.resize(720, 480)

        placeholder = QLabel(f"Run #{run_number}")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_font = placeholder.font()
        placeholder_font.setPointSize(20)
        placeholder.setFont(placeholder_font)

        exit_btn = QPushButton("Close")
        exit_btn.clicked.connect(self.close)

        button_row = QHBoxLayout()
        button_row.addWidget(exit_btn)
        button_row.addStretch(1)

        body = QVBoxLayout()
        body.addStretch(1)
        body.addWidget(placeholder)
        body.addStretch(1)
        body.addLayout(button_row)

        central = QWidget()
        central.setLayout(body)
        self.setCentralWidget(central)
