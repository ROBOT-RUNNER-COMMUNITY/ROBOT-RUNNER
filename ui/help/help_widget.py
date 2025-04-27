# ui/help/help_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QIcon, QPainter, QColor, QBrush, QPen, QPaintEvent
from utils.resource_utils import resource_path

class PerfectCircleButton(QPushButton):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)  # Taille augmentée pour accommoder l'icône de 70px
        
        # Configuration visuelle
        self.icon = QIcon(resource_path(f"images/{icon_path}"))
        self.hover_radius = 35  # Rayon du cercle de survol augmenté proportionnellement
        self.icon_size = 70     # Taille de l'icône
        
        # Style minimal pour éviter les interférences
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        
        # Dessiner le cercle de fond au survol
        if self.underMouse():
            painter.setBrush(QBrush(QColor(69, 71, 90, 120)))
            painter.setPen(QPen(QColor("#22d053"), 1.5))
            painter.drawEllipse(center, self.hover_radius, self.hover_radius)
        
        # Dessiner l'icône parfaitement centrée
        icon_rect = QRect(
            center.x() - self.icon_size//2,
            center.y() - self.icon_size//2,
            self.icon_size,
            self.icon_size
        )
        self.icon.paint(painter, icon_rect)

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Titre centré
        title = QLabel("Quick Links")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #22d053;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Layout horizontal centré
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.setSpacing(20)
        
        # Configuration des boutons
        buttons = [
            ("Report Issue", "bug.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER/issues"),
            ("GitHub Repo", "github.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER"),
            ("Documentation", "docs.png", "https://robot-runner-doc.readthedocs.io/en/latest/"),
            ("Donate", "donate.png", "https://buymeacoffee.com/khabarachre")
        ]
        
        for text, icon, url in buttons:
            btn = PerfectCircleButton(icon)
            btn.setToolTip(text)
            btn.clicked.connect(lambda _    , u=url: self.open_url(u))
            buttons_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def open_url(self, url):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))