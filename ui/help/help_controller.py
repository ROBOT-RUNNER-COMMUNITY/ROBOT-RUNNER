# ui/help/help_controller.py
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QPushButton

class HelpController(QObject):
    def __init__(self, help_widget):
        super().__init__()
        self.help_widget = help_widget
        self._connect_buttons()

    def _connect_buttons(self):
        """Connect all buttons to open their URLs"""
        for btn in self.help_widget.findChildren(QPushButton):
            if hasattr(btn, 'url'):
                btn.clicked.connect(lambda checked, url=btn.url: QDesktopServices.openUrl(QUrl(url)))