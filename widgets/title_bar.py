from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TitleBar(QHBoxLayout):
    def __init__(self, title, parent_window=None):
        super().__init__()
        self.parent_window = parent_window  # Store reference to parent window
        self.titleBarWidget = QFrame()
        self.titleBarWidget.setObjectName("titleBar")
        self.titleBarLayout = QHBoxLayout(self.titleBarWidget)
        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        
        self.titleLabel = QLabel(title)
        self.titleLabel.setStyleSheet("font-weight: bold; padding-left: 5px;")

        self.titleBarLayout.addWidget(self.titleLabel)
        self.titleBarLayout.addStretch()
        
        self.minimizeButton = QPushButton("_")
        self.closeButton = QPushButton("X")
        
        self.minimizeButton.setFixedSize(30, 30)
        self.closeButton.setFixedSize(30, 30)
        
        # Connect buttons directly if parent_window is provided
        if parent_window:
            self.minimizeButton.clicked.connect(parent_window.showMinimized)
            self.closeButton.clicked.connect(parent_window.close)
        
        self.titleBarLayout.addWidget(self.minimizeButton)
        self.titleBarLayout.addWidget(self.closeButton)
        
        self.addWidget(self.titleBarWidget)