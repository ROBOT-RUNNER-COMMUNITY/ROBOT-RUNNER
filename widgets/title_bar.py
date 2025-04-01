from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TitleBar(QHBoxLayout):
    def __init__(self, title, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        
        # Title bar widget
        self.titleBarWidget = QFrame()
        self.titleBarWidget.setObjectName("titleBar")
        self.titleBarLayout = QHBoxLayout(self.titleBarWidget)
        self.titleBarLayout.setContentsMargins(5, 0, 5, 0)
        self.titleBarLayout.setSpacing(5)
        
        # Title label
        self.titleLabel = QLabel(title)
        self.titleLabel.setStyleSheet("""
            font-weight: bold;
            padding-left: 5px;
            color: white;
        """)
        self.titleBarLayout.addWidget(self.titleLabel)
        
        # Spacer
        self.titleBarLayout.addStretch()
        
        # Window control buttons
        self.minimizeButton = QPushButton("_")
        self.maximizeButton = QPushButton("🗖")  # Maximize symbol
        self.closeButton = QPushButton("X")
        
        # Configure buttons
        for btn in [self.minimizeButton, self.maximizeButton, self.closeButton]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton#closeButton:hover {
                    background-color: #e81123;
                }
            """)
        
        # Connect buttons if parent window exists
        if parent_window:
            self.minimizeButton.clicked.connect(parent_window.showMinimized)
            self.closeButton.clicked.connect(parent_window.close)
            self.maximizeButton.clicked.connect(self.toggle_maximize_restore)
            
            # Initial button state
            self.update_maximize_button()
            
            # Connect to window state changes
            parent_window.windowStateChanged.connect(self.update_maximize_button)
        
        # Add buttons to layout (standard order)
        self.titleBarLayout.addWidget(self.minimizeButton)
        self.titleBarLayout.addWidget(self.maximizeButton)
        self.titleBarLayout.addWidget(self.closeButton)
        
        self.addWidget(self.titleBarWidget)
    
    def toggle_maximize_restore(self):
        """Toggle between maximized and normal window state"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
            # Force immediate update
            self.update_maximize_button()
    
    def update_maximize_button(self):
        """Update maximize button appearance based on window state"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.maximizeButton.setText("🗗")  # Restore symbol
            else:
                self.maximizeButton.setText("🗖")  # Maximize symbol