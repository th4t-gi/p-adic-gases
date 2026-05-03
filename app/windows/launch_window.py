from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import APP_NAME, APP_TITLE
from app.windows.run_window import RunWindow


class LaunchWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(360, 480)

        self._open_runs: list[RunWindow] = []

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel(APP_TITLE)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        run_btn = QPushButton("Run")
        cancel_btn = QPushButton("Cancel")
        run_btn.clicked.connect(self._open_run_window)
        cancel_btn.clicked.connect(self.close)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(run_btn)

        body = QVBoxLayout()
        body.addStretch(1)
        body.addWidget(title)
        body.addWidget(subtitle)
        body.addStretch(1)
        body.addLayout(button_row)

        central = QWidget()
        central.setLayout(body)
        self.setCentralWidget(central)

    def _open_run_window(self) -> None:
        run_window = RunWindow()
        run_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        run_window.destroyed.connect(lambda: self._open_runs.remove(run_window))
        self._open_runs.append(run_window)
        run_window.show()
