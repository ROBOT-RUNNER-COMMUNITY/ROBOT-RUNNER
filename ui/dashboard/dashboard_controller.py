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
        self._connect_signals()
        self._init_charts()  # Initialize charts once
        self._show_empty_state()
        
    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(self._refresh_data)
        self.data_loader.data_loaded.connect(self.update_dashboard)
        
    def _init_charts(self):
        """Initialize chart objects once for better performance"""
        # Pie Chart
        self.pie_chart = QChart()
        self.pie_chart.setTitle("Test Results Distribution")
        self.pie_chart.legend().setVisible(True)
        self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.widget.pie_chart_view.setChart(self.pie_chart)
        
        # Bar Chart
        self.bar_chart = QChart()
        self.bar_chart.setTitle("Recent Execution Times")
        self.bar_series = QBarSeries()
        self.bar_chart.addSeries(self.bar_series)
        
        # Configure axes
        self.bar_axis_x = QBarCategoryAxis()
        self.bar_chart.addAxis(self.bar_axis_x, Qt.AlignmentFlag.AlignBottom)
        
        self.bar_axis_y = QValueAxis()
        self.bar_axis_y.setMin(0)
        self.bar_chart.addAxis(self.bar_axis_y, Qt.AlignmentFlag.AlignLeft)
        
        self.widget.bar_chart_view.setChart(self.bar_chart)

    def _refresh_data(self):
        """Trigger data refresh with loading indicator"""
        self.widget.refresh_button.setEnabled(False)
        self.widget.refresh_button.setText("Loading...")
        QTimer.singleShot(100, lambda: self.data_loader.load_data(force=True))

    def update_dashboard(self, data):
        try:
            if not data or not isinstance(data, dict):
                self._show_empty_state()
                return

            # Process data in background
            QTimer.singleShot(0, lambda: self._update_ui(data))
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
            self._show_empty_state()
        finally:
            self.widget.refresh_button.setEnabled(True)
            self.widget.refresh_button.setText("↻ Refresh Dashboard")

    def _update_ui(self, data):
        """Update UI elements with new data"""
        # Update stats cards
        total = data.get('total_tests', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        recent_runs = data.get('recent_test_runs', [])
        
        self.widget.total_tests_card.layout().itemAt(1).widget().setText(str(total))
        self.widget.passed_tests_card.layout().itemAt(1).widget().setText(str(passed))
        self.widget.failed_tests_card.layout().itemAt(1).widget().setText(str(failed))
        
        # Calculate average time
        exec_times = data.get('execution_times', [])
        avg_time = np.mean(exec_times) if exec_times else 0
        self.widget.avg_time_card.layout().itemAt(1).widget().setText(f"{avg_time:.2f}s")
        
        # Update pie chart
        self._update_pie_chart(passed, failed)
        
        # Update bar chart
        self._update_bar_chart(recent_runs)
        
        # Update table
        self._update_recent_runs_table(recent_runs)

    def _update_pie_chart(self, passed, failed):
        """Optimized pie chart update"""
        self.pie_chart.removeAllSeries()
        
        if passed > 0 or failed > 0:
            pie_series = QPieSeries()
            pie_series.append("Passed", passed)
            pie_series.append("Failed", failed)
            
            slices = pie_series.slices()
            if len(slices) > 0:
                slices[0].setColor(QColor("#2ecc71"))
                slices[0].setLabelVisible(True)
            if len(slices) > 1:
                slices[1].setColor(QColor("#e74c3c"))
                slices[1].setLabelVisible(True)
            
            self.pie_chart.addSeries(pie_series)

    def _update_bar_chart(self, recent_runs):
        """Optimized bar chart update"""
        self.bar_series.clear()
        self.bar_axis_x.clear()
        
        if recent_runs:
            bar_set = QBarSet("Execution Time (s)")
            categories = []
            
            # Get last 5 unique runs by timestamp
            unique_runs = {}
            for run in sorted(recent_runs, key=lambda x: x['timestamp'], reverse=True):
                if run['name'] not in unique_runs:
                    unique_runs[run['name']] = run
                    if len(unique_runs) >= 5:
                        break
            
            for run in unique_runs.values():
                bar_set.append(run['duration'])
                short_name = run['name'][:15] + ("..." if len(run['name']) > 15 else "")
                categories.append(short_name)
            
            self.bar_series.append(bar_set)
            self.bar_axis_x.append(categories)
            
            # Auto-scale y-axis
            max_duration = max(run['duration'] for run in unique_runs.values())
            self.bar_axis_y.setMax(max(1, max_duration * 1.2))  # Ensure min range of 1

    def _update_recent_runs_table(self, runs):
        """Optimized table update"""
        self.widget.recent_runs_table.setRowCount(0)
        
        if not runs:
            return
            
        # Get last 10 unique runs
        unique_runs = {}
        for run in sorted(runs, key=lambda x: x['timestamp'], reverse=True):
            if run['name'] not in unique_runs:
                unique_runs[run['name']] = run
                if len(unique_runs) >= 10:
                    break
        
        self.widget.recent_runs_table.setRowCount(len(unique_runs))
        for row, run in enumerate(unique_runs.values()):
            # Test Name
            name_item = QTableWidgetItem(run['name'])
            self.widget.recent_runs_table.setItem(row, 0, name_item)
            
            # Timestamp
            time_item = QTableWidgetItem(run['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
            self.widget.recent_runs_table.setItem(row, 1, time_item)
            
            # Status
            status_item = QTableWidgetItem(run['status'])
            status_item.setBackground(QColor("#2ecc71" if run['status'] == 'PASS' else "#e74c3c"))
            self.widget.recent_runs_table.setItem(row, 2, status_item)
            
            # Duration
            duration_item = QTableWidgetItem(f"{run['duration']:.2f}s")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.widget.recent_runs_table.setItem(row, 3, duration_item)

    def _show_empty_state(self):
        """Reset to empty state"""
        self.widget.total_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.passed_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.failed_tests_card.layout().itemAt(1).widget().setText("0")
        self.widget.avg_time_card.layout().itemAt(1).widget().setText("0s")
        
        self.pie_chart.removeAllSeries()
        self.bar_series.clear()
        self.bar_axis_x.clear()
        self.widget.recent_runs_table.setRowCount(0)