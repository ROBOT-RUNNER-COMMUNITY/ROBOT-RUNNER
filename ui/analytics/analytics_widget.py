from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QSizePolicy
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
        self.refresh_button.setStyleSheet("font-size: 12px; padding: 5px;")
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        self.analytics_layout.addLayout(refresh_layout)
        
        # Container for charts with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setContentsMargins(10, 10, 10, 10)
        
        # Time Series Chart - Compact size
        self.time_series_fig = Figure(figsize=(8, 3), tight_layout=True)
        self.time_series_ax = self.time_series_fig.add_subplot(111)
        self.time_series_canvas = FigureCanvas(self.time_series_fig)
        self.time_series_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        self.time_series_canvas.setMinimumHeight(300)
        charts_layout.addWidget(QLabel("<b>Test Execution Trends</b>"))
        charts_layout.addWidget(self.time_series_canvas)
        
        # Failure Analysis Chart - Compact size
        self.failure_fig = Figure(figsize=(8, 3), tight_layout=True)
        self.failure_ax = self.failure_fig.add_subplot(111)
        self.failure_canvas = FigureCanvas(self.failure_fig)
        self.failure_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        self.failure_canvas.setMinimumHeight(300)
        charts_layout.addWidget(QLabel("<b>Top Failing Tests</b>"))
        charts_layout.addWidget(self.failure_canvas)
        
        scroll.setWidget(charts_container)
        self.analytics_layout.addWidget(scroll)