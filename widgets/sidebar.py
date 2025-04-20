from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QSizePolicy, QSpacerItem, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class SideBar(QWidget):
    testSelectionClicked = pyqtSignal()
    runTestsClicked = pyqtSignal()
    resultsClicked = pyqtSignal()
    settingsClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self._setup_ui()
        self._setup_style()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Logo/Header
        self.logo = QLabel("Robot Runner")
        self.logo.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Navigation Buttons
        self.btn_tests = QPushButton(QIcon("images/Logo.png"), " Test Selection")
        self.btn_run = QPushButton(QIcon("images/check.png"), " Run Tests")
        self.btn_results = QPushButton(QIcon("images/report.png"), " Results")
        self.btn_settings = QPushButton(QIcon("images/settings.png"), " Settings")

        for btn in [self.btn_tests, self.btn_run, self.btn_results, self.btn_settings]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

        layout.addSpacerItem(QSpacerItem(20, 40, 
                              QSizePolicy.Policy.Minimum, 
                              QSizePolicy.Policy.Expanding))

        # Connect signals
        self.btn_tests.clicked.connect(self.testSelectionClicked.emit)
        self.btn_run.clicked.connect(self.runTestsClicked.emit)
        self.btn_results.clicked.connect(self.resultsClicked.emit)
        self.btn_settings.clicked.connect(self.settingsClicked.emit)

        self.setLayout(layout)

    def _setup_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #2c3e50;
                border-right: 1px solid #34495e;
            }
            QPushButton {
                color: white;
                text-align: left;
                padding: 8px 15px;
                border: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #34495e;
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)