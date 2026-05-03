import sys

from PySide6.QtWidgets import QApplication

from app import APP_NAME
from app.windows.launch_window import LaunchWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    launcher = LaunchWindow()
    launcher.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
