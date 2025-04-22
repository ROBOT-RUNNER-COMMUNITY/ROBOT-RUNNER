from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_layout = QVBoxLayout()
        self.setLayout(self.dashboard_layout)
        self._init_ui()
        
    def _init_ui(self):
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("↻ Refresh Dashboard")
        self.refresh_button.setStyleSheet("font-size: 12px; padding: 5px;")
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        self.dashboard_layout.addLayout(refresh_layout)
        
        # Stats Cards - Compact layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        self.total_tests_card = self._create_stat_card("Total Tests", "0", "#3498db")
        self.passed_tests_card = self._create_stat_card("Passed", "0", "#2ecc71")
        self.failed_tests_card = self._create_stat_card("Failed", "0", "#e74c3c")
        self.avg_time_card = self._create_stat_card("Avg Time", "0s", "#9b59b6")
        
        stats_layout.addWidget(self.total_tests_card)
        stats_layout.addWidget(self.passed_tests_card)
        stats_layout.addWidget(self.failed_tests_card)
        stats_layout.addWidget(self.avg_time_card)
        self.dashboard_layout.addLayout(stats_layout)
        
        # Charts - Smaller and compact
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)
        
        # Pie Chart - Smaller size
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setMinimumSize(300, 220)
        self.pie_chart_view.setMaximumHeight(250)
        
        # Bar Chart - Smaller size
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setMinimumSize(300, 220)
        self.bar_chart_view.setMaximumHeight(250)
        
        charts_layout.addWidget(self.pie_chart_view)
        charts_layout.addWidget(self.bar_chart_view)
        self.dashboard_layout.addLayout(charts_layout)
        
        # Recent Test Runs Table
        self.recent_runs_table = QTableWidget()
        self.recent_runs_table.setColumnCount(4)
        self.recent_runs_table.setHorizontalHeaderLabels(["Test Name", "Timestamp", "Status", "Duration"])
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_runs_table.setMaximumHeight(200)
        self.dashboard_layout.addWidget(QLabel("Recent Test Runs:"))
        self.dashboard_layout.addWidget(self.recent_runs_table)
    
    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            background: {color};
            border-radius: 5px;
            padding: 10px;
            min-width: 120px;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card