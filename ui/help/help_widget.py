# ui/help/help_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Quick Links")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #89b4fa;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Icon buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add icon buttons
        self.add_icon_button(buttons_layout, "Report Issue", "bug.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER/issues")
        self.add_icon_button(buttons_layout, "GitHub Repo", "github.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER")
        self.add_icon_button(buttons_layout, "Documentation", "docs.png", "https://robot-runner-doc.readthedocs.io/en/latest/")
        self.add_icon_button(buttons_layout, "Donate", "donate.png", "https://paypal.me/yourusername")
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def add_icon_button(self, layout, tooltip, icon_path, url):
        """Add a compact icon button"""
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setIcon(QIcon(f"images/{icon_path}"))
        btn.setIconSize(QSize(32, 32))  # Smaller icon size
        btn.setFixedSize(50, 50)  # Smaller button size
        btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                border-radius: 8px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QToolTip {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 5px;
            }
        """)
        btn.url = url
        layout.addWidget(btn)