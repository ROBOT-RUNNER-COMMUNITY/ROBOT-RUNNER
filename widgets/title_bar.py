from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QEvent, QPoint
from PyQt6.QtGui import QFont

class TitleBar(QWidget):
    def __init__(self, title, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.drag_start_position = None

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        layout.addStretch()
        
        self.minimize_button = QPushButton("_")
        self.maximize_button = QPushButton("🗖")
        self.close_button = QPushButton("X")

        button_font = QFont()
        button_font.setPointSize(14)
        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFont(button_font)
            btn.setFixedSize(QSize(32, 32))
            layout.addWidget(btn)

        if self.parent_window:
            self.minimize_button.clicked.connect(parent_window.showMinimized)
            self.close_button.clicked.connect(parent_window.close)
            self.maximize_button.clicked.connect(self.toggle_maximize_restore)
            self.update_maximize_button()
            self.parent_window.installEventFilter(self)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #34495e;
                border-bottom: 1px solid #2c3e50;
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

    def eventFilter(self, obj, event):
        if obj == self.parent_window and event.type() == QEvent.Type.WindowStateChange:
            self.update_maximize_button()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if not self.drag_start_position:
            return
            
        if not self.parent_window.isMaximized():
            # Déplacement normal de la fenêtre
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.parent_window.move(self.parent_window.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()
        event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_start_position = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize_restore()
        event.accept()

    def toggle_maximize_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
        self.update_maximize_button()

    def update_maximize_button(self):
        if self.parent_window.isMaximized():
            self.maximize_button.setText("🗗")
        else:
            self.maximize_button.setText("🗖")