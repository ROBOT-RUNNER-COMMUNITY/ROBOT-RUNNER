# ui/dashboard/dashboard_controller.py
from PyQt6.QtCore import QObject, Qt, QTimer
from PyQt6.QtCharts import QChart, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem
import numpy as np
from datetime import datetime

class DashboardController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self.cached_data = None
        self._connect_signals()
        self._init_charts()
        self._show_empty_state()

    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(self._refresh_data)
        self.data_loader.data_loaded.connect(self._handle_new_data)

    def _init_charts(self):
        """Initialize chart objects for better performance"""
        # Pie Chart
        self.pie_chart = QChart()
        self.pie_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.widget.pie_chart_view.setChart(self.pie_chart)

        # Bar Chart
        self.bar_chart = QChart()
        self.bar_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.bar_series = QBarSeries()
        self.bar_chart.addSeries(self.bar_series)
        
        # Configure axes once
        self.bar_axis_x = QBarCategoryAxis()
        self.bar_axis_y = QValueAxis()
        self.bar_chart.addAxis(self.bar_axis_x, Qt.AlignmentFlag.AlignBottom)
        self.bar_chart.addAxis(self.bar_axis_y, Qt.AlignmentFlag.AlignLeft)
        self.bar_series.attachAxis(self.bar_axis_x)
        self.bar_series.attachAxis(self.bar_axis_y)
        
        self.widget.bar_chart_view.setChart(self.bar_chart)

    def _refresh_data(self):
        """Trigger data refresh with visual feedback"""
        self.widget.refresh_button.setEnabled(False)
        self.widget.refresh_button.setText("Loading...")
        QTimer.singleShot(100, lambda: self.data_loader.load_data(force=True))

    def _handle_new_data(self, data):
        """Process new data and update UI"""
        try:
            self.cached_data = data
            self._update_ui(data)
        finally:
            self.widget.refresh_button.setEnabled(True)
            self.widget.refresh_button.setText("↻ Refresh Dashboard")

    def _update_ui(self, data):
        """Update all UI elements with new data"""
        if not data or not data.get('recent_test_runs'):
            self._show_empty_state()
            return

        # Update stats cards
        self._update_stats_cards(data)
        
        # Update charts
        self._update_pie_chart(data)
        self._update_bar_chart(data)
        
        # Update table
        self._update_recent_runs_table(data.get('recent_test_runs', []))

    def _update_stats_cards(self, data):
        """Update the statistic cards"""
        total = data.get('total_tests', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        exec_times = data.get('execution_times', [])

        # Get references to the card widgets
        total_label = self.widget.total_tests_card.layout().itemAt(1).widget()
        passed_label = self.widget.passed_tests_card.layout().itemAt(1).widget()
        failed_label = self.widget.failed_tests_card.layout().itemAt(1).widget()
        avg_label = self.widget.avg_time_card.layout().itemAt(1).widget()

        # Update the labels
        total_label.setText(str(total))
        passed_label.setText(str(passed))
        failed_label.setText(str(failed))
        
        # Calculate average time
        avg_time = np.mean(exec_times) if exec_times else 0
        avg_label.setText(f"{avg_time:.2f}s")

    def _update_pie_chart(self, data):
        """Update the pie chart with new data"""
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)

        self.pie_chart.removeAllSeries()
        
        if passed > 0 or failed > 0:
            pie_series = QPieSeries()
            pie_series.append(f"Passed ({passed})", passed)
            pie_series.append(f"Failed ({failed})", failed)

            # Set slice colors
            slices = pie_series.slices()
            slices[0].setColor(QColor("#2ecc71"))
            slices[0].setLabelVisible(True)
            if len(slices) > 1:
                slices[1].setColor(QColor("#e74c3c"))
                slices[1].setLabelVisible(True)

            self.pie_chart.addSeries(pie_series)
            self.pie_chart.setTitle("Test Results Distribution")

    def _update_bar_chart(self, data):
        """Update the bar chart with recent execution times"""
        recent_runs = data.get('recent_test_runs', [])
        self.bar_series.clear()
        self.bar_axis_x.clear()

        if not recent_runs:
            self.bar_chart.setTitle("No recent runs")
            return

        # Prepare data for the last 5 runs
        bar_set = QBarSet("Execution Time (s)")
        categories = []
        
        # Sort by most recent first and take top 5
        recent_runs_sorted = sorted(recent_runs, key=lambda x: x['timestamp'], reverse=True)[:5]
        
        for test in recent_runs_sorted:
            bar_set.append(test['duration'])
            short_name = test['name'][:15] + ("..." if len(test['name']) > 15 else "")
            categories.append(short_name)

        self.bar_series.append(bar_set)
        self.bar_axis_x.append(categories)
        
        # Configure Y axis
        max_duration = max(test['duration'] for test in recent_runs_sorted)
        self.bar_axis_y.setRange(0, max_duration * 1.2)  # 20% padding
        
        self.bar_chart.setTitle("Recent Execution Times")

    def _update_recent_runs_table(self, runs):
        """Update the recent runs table"""
        self.widget.recent_runs_table.setRowCount(0)
        
        if not runs:
            return
            
        # Sort by most recent first
        runs_sorted = sorted(runs, key=lambda x: x['timestamp'], reverse=True)
        self.widget.recent_runs_table.setRowCount(len(runs_sorted))
        
        for row, run in enumerate(runs_sorted):
            # Test Name
            name_item = QTableWidgetItem(run['name'])
            self.widget.recent_runs_table.setItem(row, 0, name_item)
            
            # Timestamp
            time_item = QTableWidgetItem(run['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
            self.widget.recent_runs_table.setItem(row, 1, time_item)
            
            # Status with color
            status_item = QTableWidgetItem(run['status'])
            status_item.setBackground(
                QColor("#2ecc71") if run['status'] == 'PASS' else QColor("#e74c3c")
            )
            self.widget.recent_runs_table.setItem(row, 2, status_item)
            
            # Duration
            duration_item = QTableWidgetItem(f"{run['duration']:.2f}s")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.widget.recent_runs_table.setItem(row, 3, duration_item)

    def _show_empty_state(self):
        """Reset all widgets to empty state"""
        # Stats cards
        self.widget.total_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.passed_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.failed_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.avg_time_card.layout().itemAt(1).widget().setText("0s")
        
        # Charts
        self.pie_chart.setTitle("No test data")
        self.pie_chart.removeAllSeries()
        
        self.bar_chart.setTitle("No recent runs")
        self.bar_series.clear()
        self.bar_axis_x.clear()
        
        # Table
        self.widget.recent_runs_table.setRowCount(0)