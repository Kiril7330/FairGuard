import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from PyQt6.QtGui import QIcon


def get_asset_path(relative_path):
    """Dynamically route paths for PyInstaller _MEIPASS or local dev"""
    if hasattr(sys, "_MEIPASS"):

        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)


def main():
    app = QApplication(sys.argv)

    # Hebrew layout support
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # Logo display
    logo_path = get_asset_path("assets/guard_logo.jpg")
    app.setWindowIcon(QIcon(logo_path))

    # Create the window and show it on screen
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
