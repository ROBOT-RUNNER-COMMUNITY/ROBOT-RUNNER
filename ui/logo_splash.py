from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from utils.resource_utils import resource_path

class LogoSplash:
    def __init__(self, parent):
        self.parent = parent
        self.logo_label = QLabel(parent)
        
        logo_path = resource_path("images/Logo.png")
        self.logo_pixmap = QPixmap(logo_path)
        
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setGeometry(parent.rect())
        self.show()

        QTimer.singleShot(2500, self.hide)

    def show(self):
        """Make the splash screen visible"""
        self.logo_label.show()

    def hide(self):
        """Hide the splash screen"""
        self.logo_label.hide()