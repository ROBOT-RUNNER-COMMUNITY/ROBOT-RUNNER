from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QSizePolicy, QSpacerItem, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class SideBar(QWidget):
    testSelectionClicked = pyqtSignal()
    dashboardClicked = pyqtSignal()
    analyticsClicked = pyqtSignal()
    settingsClicked = pyqtSignal()
    helpClicked = pyqtSignal()

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
        layout.addWidget(self.logo)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #34495e;")
        layout.addWidget(separator)
        
        # Main Navigation Section
        self.btn_dashboard = QPushButton(QIcon("images/dashboard.png"), " Dashboard")
        self.btn_tests = QPushButton(QIcon("images/Logo.png"), " Test Selection")
        
        # Analytics Section
        separator_analytics = QFrame()
        separator_analytics.setFrameShape(QFrame.Shape.HLine)
        separator_analytics.setStyleSheet("color: #34495e;")
        
        self.btn_analytics = QPushButton(QIcon("images/analytics.png"), " Analytics")
        
        # Settings Section
        separator_settings = QFrame()
        separator_settings.setFrameShape(QFrame.Shape.HLine)
        separator_settings.setStyleSheet("color: #34495e;")
        
        self.btn_settings = QPushButton(QIcon("images/settings.png"), " Settings")
        self.btn_help = QPushButton(QIcon("images/help.png"), " Help")

        # Add all buttons to layout
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_tests)
        
        layout.addWidget(separator_analytics)
        layout.addWidget(self.btn_analytics)
        
        layout.addWidget(separator_settings)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_help)

        layout.addSpacerItem(QSpacerItem(20, 40, 
                              QSizePolicy.Policy.Minimum, 
                              QSizePolicy.Policy.Expanding))

        # Connect signals
        self.btn_dashboard.clicked.connect(self.dashboardClicked.emit)
        self.btn_tests.clicked.connect(self.testSelectionClicked.emit)
        self.btn_analytics.clicked.connect(self.analyticsClicked.emit)
        self.btn_settings.clicked.connect(self.settingsClicked.emit)
        self.btn_help.clicked.connect(self.helpClicked.emit)

        # Style all buttons consistently
        for btn in [self.btn_dashboard, self.btn_tests, 
                   self.btn_analytics, self.btn_settings, 
                   self.btn_help]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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
            QLabel {
                margin-bottom: 15px;
            }
        """)