from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_layout = QVBoxLayout()
        self.setLayout(self.dashboard_layout)
        self._init_ui()
        
    def _init_ui(self):
        # Refresh button for dashboard
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Dashboard")
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        self.dashboard_layout.addLayout(refresh_layout)
        
        # Stats Cards
        self.stats_layout = QHBoxLayout()
        self.total_tests_card = self._create_stat_card("Total Tests", "0")
        self.passed_tests_card = self._create_stat_card("Passed", "0", "#2ecc71")
        self.failed_tests_card = self._create_stat_card("Failed", "0", "#e74c3c")
        self.avg_time_card = self._create_stat_card("Avg Time", "0s", "#3498db")
        
        self.stats_layout.addWidget(self.total_tests_card)
        self.stats_layout.addWidget(self.passed_tests_card)
        self.stats_layout.addWidget(self.failed_tests_card)
        self.stats_layout.addWidget(self.avg_time_card)
        self.dashboard_layout.addLayout(self.stats_layout)
        
        # Charts
        self.charts_layout = QHBoxLayout()
        
        # Pie Chart
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setMinimumSize(400, 300)
        
        # Bar Chart
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setMinimumSize(400, 300)
        
        self.charts_layout.addWidget(self.pie_chart_view)
        self.charts_layout.addWidget(self.bar_chart_view)
        self.dashboard_layout.addLayout(self.charts_layout)
        
        # Recent Runs Table
        self.recent_runs_table = QTableWidget()
        self.recent_runs_table.setColumnCount(4)
        self.recent_runs_table.setHorizontalHeaderLabels(["Test Suite", "Timestamp", "Status", "Duration"])
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_runs_table.setMaximumHeight(200)
        self.dashboard_layout.addWidget(QLabel("Recent Test Runs:"))
        self.dashboard_layout.addWidget(self.recent_runs_table)
    
    def _create_stat_card(self, title, value, color="#34495e"):
        """Create a statistic card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            background: {color};
            border-radius: 5px;
            padding: 15px;
            min-width: 150px;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card