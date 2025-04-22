from PyQt6.QtCore import QObject, Qt
from PyQt6.QtCharts import QChart, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QTableWidgetItem
import numpy as np
from PyQt6 import QtCore

class DashboardController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self._init_charts()
        self._connect_signals()
        
    def _init_charts(self):
        """Initialize chart objects with consistent styling"""
        # Pie Chart
        self.pie_chart = QChart()
        self.pie_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.pie_chart.setBackgroundBrush(QColor("#ffffff"))
        self.pie_chart.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.widget.pie_chart_view.setChart(self.pie_chart)
        self.widget.pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Bar Chart
        self.bar_chart = QChart()
        self.bar_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.bar_chart.setBackgroundBrush(QColor("#ffffff"))
        self.bar_chart.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.bar_series = QBarSeries()
        self.bar_chart.addSeries(self.bar_series)
        
        # Configure axes
        self.bar_axis_x = QBarCategoryAxis()
        self.bar_axis_x.setTitleText("Test Cases")
        self.bar_axis_x.setLabelsFont(QFont("Arial", 8))
        self.bar_axis_x.setLabelsAngle(-45)
        
        self.bar_axis_y = QValueAxis()
        self.bar_axis_y.setTitleText("Duration (s)")
        self.bar_axis_y.setLabelsFont(QFont("Arial", 8))
        
        self.bar_chart.addAxis(self.bar_axis_x, Qt.AlignmentFlag.AlignBottom)
        self.bar_chart.addAxis(self.bar_axis_y, Qt.AlignmentFlag.AlignLeft)
        self.bar_series.attachAxis(self.bar_axis_x)
        self.bar_series.attachAxis(self.bar_axis_y)
        
        self.widget.bar_chart_view.setChart(self.bar_chart)
        self.widget.bar_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(lambda: self.data_loader.load_data(force=True))
        self.data_loader.data_loaded.connect(self.update_dashboard)
        
    def update_dashboard(self, data):
        try:
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
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            self._show_empty_state()

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
            pie_series.setLabelsVisible(True)
            pie_series.append(f"Passed ({passed})", passed)
            pie_series.append(f"Failed ({failed})", failed)

            # Set slice colors and style
            slices = pie_series.slices()
            slices[0].setColor(QColor("#2ecc71"))
            slices[0].setLabelColor(QColor("#333333"))
            slices[0].setBorderColor(QColor("#ffffff"))
            slices[0].setBorderWidth(1)
            
            if len(slices) > 1:
                slices[1].setColor(QColor("#e74c3c"))
                slices[1].setLabelColor(QColor("#333333"))
                slices[1].setBorderColor(QColor("#ffffff"))
                slices[1].setBorderWidth(1)

            self.pie_chart.addSeries(pie_series)
            self.pie_chart.setTitle("Test Results Distribution")
            self.pie_chart.legend().setVisible(True)
            self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self.pie_chart.legend().setFont(QFont("Arial", 8))

    def _update_bar_chart(self, data):
        """Improved bar chart for recent execution times"""
        recent_runs = data.get('recent_test_runs', [])
        self.bar_series.clear()
        self.bar_axis_x.clear()

        if not recent_runs:
            self.bar_chart.setTitle("No recent runs")
            return

        # Prepare data - get last 5 unique test runs
        bar_set = QBarSet("Execution Time")
        bar_set.setColor(QColor("#3498db"))  # Consistent blue color
        bar_set.setBorderColor(QColor("#ffffff"))
        categories = []
        
        # Sort by most recent and ensure unique test names
        unique_runs = {}
        for run in sorted(recent_runs, key=lambda x: x['timestamp'], reverse=True):
            if run['name'] not in unique_runs:
                unique_runs[run['name']] = run
        recent_runs_sorted = list(unique_runs.values())[:5]  # Get top 5 most recent

        for test in recent_runs_sorted:
            bar_set.append(test['duration'])
            # Smart name truncation with ellipsis
            name = test['name']
            if len(name) > 20:
                name = name[:8] + "..." + name[-8:]
            categories.append(name)

        self.bar_series.append(bar_set)
        self.bar_axis_x.append(categories)
        
        # Configure Y axis with dynamic padding
        max_duration = max(test['duration'] for test in recent_runs_sorted)
        self.bar_axis_y.setRange(0, max(1, max_duration * 1.15))  # 15% padding
        
        # Chart styling
        self.bar_chart.setTitle("Recent Execution Times")
        self.bar_chart.setTitleFont(QFont("Arial", 10, QFont.Weight.Bold))

    def _update_recent_runs_table(self, runs):
        """Update the recent runs table with improved styling"""
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
            status_item.setForeground(QColor("#ffffff"))
            self.widget.recent_runs_table.setItem(row, 2, status_item)
            
            # Duration
            duration_item = QTableWidgetItem(f"{run['duration']:.2f}s")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.widget.recent_runs_table.setItem(row, 3, duration_item)

    def _show_empty_state(self):
        """Reset all widgets to clean empty state"""
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