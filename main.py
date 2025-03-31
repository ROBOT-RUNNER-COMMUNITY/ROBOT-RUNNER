import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import RobotTestRunner

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotTestRunner()
    window.show()
    sys.exit(app.exec())