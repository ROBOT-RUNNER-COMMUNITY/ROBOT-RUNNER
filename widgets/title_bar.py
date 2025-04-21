from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class TitleBar(QWidget):
    def __init__(self, title, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)


        layout.addStretch()

        # Buttons
        self.minimize_button = QPushButton("_")
        self.maximize_button = QPushButton("🗖")
        self.close_button = QPushButton("X")

        # Button font and size
        button_font = QFont()
        button_font.setPointSize(14)
        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFont(button_font)
            btn.setFixedSize(QSize(32, 32))  # Slightly larger buttons
            layout.addWidget(btn)

        # Connect signals
        if self.parent_window:
            self.minimize_button.clicked.connect(parent_window.showMinimized)
            self.close_button.clicked.connect(parent_window.close)
            self.maximize_button.clicked.connect(self.toggle_maximize_restore)
            self.update_maximize_button()
            self.parent_window.windowStateChanged.connect(self.update_maximize_button)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #34495e;
                border-bottom: 1px solid #2c3e50;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QPushButton {
                border: none;
                background: transparent;
                color: white;
            }
            QPushButton:hover {
                background: #2c3e50;
                border-radius: 3px;
            }
        """)

    def toggle_maximize_restore(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
            self.update_maximize_button()

    def update_maximize_button(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.maximize_button.setText("🗗")  # Restore
            else:
                self.maximize_button.setText("🗖")  # Maximize
