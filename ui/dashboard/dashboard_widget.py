from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_layout = QVBoxLayout()
        self.setLayout(self.dashboard_layout)
        self._init_ui()
        
    def _init_ui(self):
        # Refresh and Export buttons
        button_layout = QHBoxLayout()
        
        # Refresh Button with icon
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon(":/icons/refresh.svg"))  # Use your refresh icon
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setText(" Refresh Dashboard")
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
        
        # Export Button with Excel icon
        self.export_button = QPushButton()
        self.export_button.setIcon(QIcon(":/icons/excel.svg"))  # Use your Excel icon
        self.export_button.setIconSize(QSize(16, 16))
        self.export_button.setText(" Export Full Report")
        self.export_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 150px;
                color: white;
                background-color: #17a2b8;
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
        self.dashboard_layout.addLayout(button_layout)
        
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
        
        # All Test Runs Table
        self.recent_runs_table = QTableWidget()
        self.recent_runs_table.setColumnCount(4)
        self.recent_runs_table.setHorizontalHeaderLabels(["Test Name", "Timestamp", "Status", "Duration"])
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_runs_table.setMaximumHeight(400)
        self.dashboard_layout.addWidget(QLabel("All Test Runs:"))
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