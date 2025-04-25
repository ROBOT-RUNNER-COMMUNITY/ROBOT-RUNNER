from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QSizePolicy, QSpacerItem, QLabel, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
 
from utils.resource_utils import resource_path
 
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
 
        # Logo/Header with icon
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
 
        logo_icon = QLabel()
        pixmap = QPixmap(resource_path("images/Logo.png")).scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_icon.setPixmap(pixmap)
        logo_icon.setStyleSheet("border: 2px solid transparent; background: transparent;")

        logo_text = QLabel("Robot Runner")
        logo_text.setStyleSheet("font-size: 18px; font-weight: bold; color: #50C878; background: transparent; border: 2px solid transparent;")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
 
        logo_layout.addWidget(logo_icon)
        logo_layout.addSpacing(6)
        logo_layout.addWidget(logo_text)
 
        layout.addLayout(logo_layout)
        # Main Navigation Section
        self.btn_dashboard = QPushButton(QIcon(resource_path("images/dashboard.png")), " Dashboard")
        self.btn_tests = QPushButton(QIcon(resource_path("images/Tests.png")), " Test Selection")
 
        self.btn_analytics = QPushButton(QIcon(resource_path("images/analytics.png")), " Analytics")
 
        self.btn_settings = QPushButton(QIcon(resource_path("images/settings.png")), " Settings")
        self.btn_help = QPushButton(QIcon(resource_path("images/help.png")), " Help")
 
        # Add all buttons to layout
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_tests)
 
        layout.addWidget(self.btn_analytics)
 
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
