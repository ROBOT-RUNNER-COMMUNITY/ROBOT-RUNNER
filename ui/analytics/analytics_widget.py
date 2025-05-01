from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.resource_utils import resource_path

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.analytics_layout = QVBoxLayout()
        self.setLayout(self.analytics_layout)
        self._init_ui()
        
    def _init_ui(self):
        # Refresh and Export buttons
        button_layout = QHBoxLayout()
        
        # Refresh Button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon(resource_path("images/refresh.png")))  # Use your refresh icon
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setText(" Refresh Analytics")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 150px;
                color: white;
                background-color: #6c757d;
            }
            QPushButton:hover {
                background-color: #5a6268;
                color: white;
            }
            QPushButton:pressed {
                background: #545b62;
                color: white;
            }
        """)
        
        # Export Button
        self.export_button = QPushButton()
        self.export_button.setIcon(QIcon(resource_path("images/excel.png")))
        self.export_button.setIconSize(QSize(16, 16))
        self.export_button.setText(" Export Analytics")
        self.export_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 150px;
                color: white;
                background-color: #2f8a39;
            }
            QPushButton:hover {
                background-color: #138496;
                color: white;
            }
            QPushButton:pressed {
                background: #117a8b;
                color: white;
            }
        """)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        self.analytics_layout.addLayout(button_layout)
        
        # Container for charts with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        charts_container = QWidget()
        self.charts_layout = QGridLayout(charts_container)
        self.charts_layout.setContentsMargins(15, 15, 15, 15)
        self.charts_layout.setSpacing(20)
        self.charts_layout.setColumnStretch(0, 2)  # Left column (trends) wider
        self.charts_layout.setColumnStretch(1, 1)  # Right column (status) narrower
        
        # Create all charts
        self._create_trends_chart()
        self._create_status_chart()
        self._create_failure_chart()
        self._create_time_chart()
        
        scroll.setWidget(charts_container)
        self.analytics_layout.addWidget(scroll)

    def _create_trends_chart(self):
        """Execution trends chart (top left)"""
        self.trends_fig = Figure(figsize=(10, 4), tight_layout=True, dpi=100)
        self.trends_ax = self.trends_fig.add_subplot(111)
        self.trends_canvas = FigureCanvas(self.trends_fig)
        self.trends_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.trends_canvas.setMinimumHeight(300)
        self.charts_layout.addWidget(QLabel("<b style='font-size: 12px;'>Test Execution Trends</b>"), 0, 0)
        self.charts_layout.addWidget(self.trends_canvas, 1, 0)

    def _create_status_chart(self):
        """Status distribution chart (top right)"""
        self.status_fig = Figure(figsize=(6, 4), tight_layout=True, dpi=100)
        self.status_ax = self.status_fig.add_subplot(111)
        self.status_canvas = FigureCanvas(self.status_fig)
        self.status_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.status_canvas.setMinimumHeight(300)
        self.charts_layout.addWidget(QLabel("<b style='font-size: 12px;'>Test Status Distribution</b>"), 0, 1)
        self.charts_layout.addWidget(self.status_canvas, 1, 1)

    def _create_failure_chart(self):
        """Failure analysis chart (bottom left)"""
        self.failure_fig = Figure(figsize=(10, 4), tight_layout=True, dpi=100)
        self.failure_ax = self.failure_fig.add_subplot(111)
        self.failure_canvas = FigureCanvas(self.failure_fig)
        self.failure_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.failure_canvas.setMinimumHeight(300)
        self.charts_layout.addWidget(QLabel("<b style='font-size: 12px;'>Top Failure Reasons</b>"), 2, 0)
        self.charts_layout.addWidget(self.failure_canvas, 3, 0)

    def _create_time_chart(self):
        """Execution time chart (bottom right)"""
        self.time_fig = Figure(figsize=(6, 4), tight_layout=True, dpi=100)
        self.time_ax = self.time_fig.add_subplot(111)
        self.time_canvas = FigureCanvas(self.time_fig)
        self.time_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.time_canvas.setMinimumHeight(300)
        self.charts_layout.addWidget(QLabel("<b style='font-size: 12px;'>Execution Time Distribution</b>"), 2, 1)
        self.charts_layout.addWidget(self.time_canvas, 3, 1)