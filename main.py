import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # This forces the entire layout to be Right-to-Left for Hebrew support
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # Create the window and show it on screen
    window = MainWindow()
    window.show()
    
    # Keep the app running in a loop until you click the red X
    sys.exit(app.exec())

if __name__ == "__main__":
    main()