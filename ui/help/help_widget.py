import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, QSize, QRect, QPropertyAnimation, QEasingCurve, 
                         QPointF, QPoint)
from PyQt6.QtGui import (QIcon, QPainter, QColor, QBrush, QPen, QPaintEvent, 
                        QLinearGradient, QFont)
from utils.resource_utils import resource_path
import webbrowser
import sys
import xml.etree.ElementTree as ET


class AnimatedCircleButton(QPushButton):
    def __init__(self, icon_path, text="", parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.font = QFont("Segoe UI", 9, QFont.Weight.Medium)
        self.text = text
        self.icon = QIcon(resource_path(f"images/{icon_path}"))
        self.icon_size = 60
        self._radius = 45  
        self.hover_radius = 50
        self.base_radius = 45 
        
        # Colors
        self.base_color = QColor(69, 71, 90, 80)
        self.hover_color = QColor(34, 208, 83, 150)
        self.text_color = QColor(200, 200, 200)
        self.highlight_color = QColor(34, 208, 83)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"radius")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
            QToolTip {
                background-color: #2a2b3a;
                color: #ffffff;
                border: 1px solid #22d053;
                padding: 5px;
                border-radius: 3px;
                font: 10pt "Segoe UI";
            }
        """)

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        self.update()

    radius = property(get_radius, set_radius)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self._radius)
        self.animation.setEndValue(self.hover_radius)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self._radius)
        self.animation.setEndValue(self.base_radius)
        self.animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        
        # Draw glow effect when hovered
        if self.underMouse():
            gradient = QLinearGradient(
                QPointF(center.x() - 30, center.y() - 30),
                QPointF(center.x() + 30, center.y() + 30)
            )
            gradient.setColorAt(0, QColor(34, 208, 83, 50))
            gradient.setColorAt(1, QColor(34, 208, 83, 20))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(center, self.hover_radius + 10, self.hover_radius + 10)
        
        # Draw the background circle
        painter.setPen(QPen(self.highlight_color if self.underMouse() else Qt.GlobalColor.transparent, 1.5))
        painter.setBrush(QBrush(self.hover_color if self.underMouse() else self.base_color))
        painter.drawEllipse(center, self._radius, self._radius)
        
        # Draw the icon
        icon_rect = QRect(
            center.x() - self.icon_size//2,
            center.y() - self.icon_size//2,
            self.icon_size,
            self.icon_size
        )
        self.icon.paint(painter, icon_rect)
        
        # Draw the text below the circle if provided
        if self.text:
            painter.setFont(self.font)
            painter.setPen(QPen(self.text_color))
            text_rect = QRect(
                center.x() - 50,
                center.y() + self._radius + 5,
                100,
                20
            )
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1f2c, stop:1 #2a2b3a
                );
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(25)
        
        # Title with decorative elements
        title_container = QHBoxLayout()
        title_container.setContentsMargins(0, 0, 0, 10)
        
        left_decoration = QFrame()
        left_decoration.setFrameShape(QFrame.Shape.HLine)
        left_decoration.setStyleSheet("border: 1px solid #22d053;")
        left_decoration.setFixedWidth(30)
        
        right_decoration = QFrame()
        right_decoration.setFrameShape(QFrame.Shape.HLine)
        right_decoration.setStyleSheet("border: 1px solid #22d053;")
        right_decoration.setFixedWidth(30)
        
        title = QLabel("Quick Links")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font: 20pt "Segoe UI SemiBold";
                color: #ffffff;
                padding: 0 15px;
            }
        """)
        
        title_container.addWidget(left_decoration, 0, Qt.AlignmentFlag.AlignVCenter)
        title_container.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(right_decoration, 0, Qt.AlignmentFlag.AlignVCenter)
        
        layout.addLayout(title_container)
        
        description = QLabel(
            "Access important resources and support channels with one click. "
            "Get help, report issues, or contribute to the project."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("""
            QLabel {
                font: 10pt "Segoe UI";
                color: #a0a0a0;
                padding: 0 20px;
            }
        """)
        layout.addWidget(description)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 0, 20, 0)
        buttons_layout.setSpacing(30)
        
        buttons = [
            ("Report Issue", "bug.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER/issues"),
            ("GitHub", "github.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER"),
            ("Docs", "docs.png", "https://robot-runner-doc.readthedocs.io/en/latest/"),
            ("Support", "donate.png", "https://buymeacoffee.com/khabarachre")
        ]
        
        for text, icon, url in buttons:
            btn = AnimatedCircleButton(icon, text)
            btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
            buttons_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(buttons_layout)

        config_paths = [
                'config.xml',
                os.path.join(os.path.dirname(sys.executable), 'config.xml'),
            ]
                
        config_loaded = False
        for path in config_paths:
            if os.path.exists(path):
                tree = ET.parse(path)
                root = tree.getroot()
                self.version_label = f"{root[0].text}"
                config_loaded = True
                break
                
        if not config_loaded:
            self.version_label = "(Unknown version)"

        footer = QLabel(f"© ROBOT RUNNER {self.version_label} | "
                        "Developed by Achraf KHABAR | ")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                font: 8pt "Segoe UI";
                color: #606060;
                padding-top: 15px;
                border-top: 1px solid #404040;
            }
        """)
        layout.addWidget(footer)
        
        self.setLayout(layout)
            

    def setup_animations(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(500)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutQuad)

    def showEvent(self, event):
        self.fade_in.start()
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Shadow effect
        shadow = QLinearGradient(0, 0, 0, self.height())
        shadow.setColorAt(0, QColor(0, 0, 0, 30))
        shadow.setColorAt(1, QColor(0, 0, 0, 60))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow))
        painter.drawRoundedRect(self.rect().adjusted(0, 3, 0, 3), 12, 12)
        
        # Main background
        painter.setBrush(QBrush(QColor(30, 31, 46)))
        painter.setPen(QPen(QColor(60, 62, 82), 1))
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        super().paintEvent(event)