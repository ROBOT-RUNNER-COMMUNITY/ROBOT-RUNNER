from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.analytics_layout = QVBoxLayout()
        self.setLayout(self.analytics_layout)
        self._init_ui()
        
    def _init_ui(self):
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("↻ Refresh Analytics")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                font-size: 12px; 
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 150px;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
            QPushButton:pressed {
                background: #dee2e6;
            }
        """)
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        self.analytics_layout.addLayout(refresh_layout)
        
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