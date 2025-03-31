from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from utils.resource_utils import resource_path

def show_cross(window):
    cross_icon_path = resource_path("images/cross.png")
    cross_pixmap = QPixmap(cross_icon_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio)
    window.loadingLabel.setPixmap(cross_pixmap)
    window.loadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)