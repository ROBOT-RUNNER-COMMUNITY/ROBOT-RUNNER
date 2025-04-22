from PyQt6.QtCore import QObject, Qt
from PyQt6.QtCharts import QChart, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem
import numpy as np

class DashboardController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self._connect_signals()
        
    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(lambda: self.data_loader.load_data(force=True))
        self.data_loader.data_loaded.connect(self.update_dashboard)
        
    def update_dashboard(self, data):
        try:
            if not data:
                print("Empty data received")
                self._show_empty_state()
                return
                
            # Debug output
            print("\n=== Dashboard Update ===")
            print(f"Total Tests: {data.get('total_tests', 0)}")
            print(f"Passed: {data.get('passed', 0)}")
            print(f"Failed: {data.get('failed', 0)}")
            print(f"Recent Test Runs: {len(data.get('recent_test_runs', []))}")
            
            # Update stats cards
            total = data.get('total_tests', 0)
            passed = data.get('passed', 0)
            failed = data.get('failed', 0)
            exec_times = data.get('execution_times', [])
            
            # Get references to the card widgets
            total_label = self.widget.total_tests_card.layout().itemAt(1).widget()
            passed_label = self.widget.passed_tests_card.layout().itemAt(1).widget()
            failed_label = self.widget.failed_tests_card.layout().itemAt(1).widget()
            avg_label = self.widget.avg_time_card.layout().itemAt(1).widget()
            
            # Update card values
            total_label.setText(str(total))
            passed_label.setText(str(passed))
            failed_label.setText(str(failed))
            
            avg_time = np.mean(exec_times) if exec_times else 0
            avg_label.setText(f"{avg_time:.2f}s")
            
            # Update pie chart
            if total > 0:
                pie_series = QPieSeries()
                if passed > 0:
                    passed_slice = pie_series.append(f"Passed ({passed})", passed)
                    passed_slice.setColor(QColor("#2ecc71"))
                    passed_slice.setLabelVisible(True)
                if failed > 0:
                    failed_slice = pie_series.append(f"Failed ({failed})", failed)
                    failed_slice.setColor(QColor("#e74c3c"))
                    failed_slice.setLabelVisible(True)
                
                chart = QChart()
                chart.addSeries(pie_series)
                chart.setTitle("Test Results Distribution")
                chart.legend().setVisible(True)
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
                self.widget.pie_chart_view.setChart(chart)
            else:
                self._show_empty_chart(self.widget.pie_chart_view, "No test results")
            
            # Update bar chart with recent test executions
            recent_tests = data.get('recent_test_runs', [])
            if recent_tests:
                bar_set = QBarSet("Execution Time (s)")
                categories = []
                
                # Show last 5 test executions
                for test in recent_tests[:5]:
                    bar_set.append(test['duration'])
                    categories.append(f"{test['name'][:15]}...\n{test['timestamp'].strftime('%m-%d %H:%M')}")
                
                bar_series = QBarSeries()
                bar_series.append(bar_set)
                
                chart = QChart()
                chart.addSeries(bar_series)
                chart.setTitle("Recent Test Execution Times")
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
                
                axis_x = QBarCategoryAxis()
                axis_x.append(categories)
                chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
                bar_series.attachAxis(axis_x)
                
                axis_y = QValueAxis()
                chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
                bar_series.attachAxis(axis_y)
                
                self.widget.bar_chart_view.setChart(chart)
            else:
                self._show_empty_chart(self.widget.bar_chart_view, "No recent test runs")
            
            # Update recent test runs table
            self._update_recent_tests_table(recent_tests)
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            self._show_empty_state()

    def _update_recent_tests_table(self, tests):
        """Update table with individual test runs"""
        self.widget.recent_runs_table.setRowCount(0)
        
        if not tests:
            return
            
        # Show last 5 test executions
        for test in tests[:5]:
            row = self.widget.recent_runs_table.rowCount()
            self.widget.recent_runs_table.insertRow(row)
            
            # Test Name
            name_item = QTableWidgetItem(test['name'])
            self.widget.recent_runs_table.setItem(row, 0, name_item)
            
            # Timestamp
            time_item = QTableWidgetItem(test['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
            self.widget.recent_runs_table.setItem(row, 1, time_item)
            
            # Status with color coding
            status_item = QTableWidgetItem(test['status'])
            status_item.setBackground(
                QColor("#2ecc71") if test['status'] == 'PASS' else QColor("#e74c3c")
            )
            self.widget.recent_runs_table.setItem(row, 2, status_item)
            
            # Duration
            duration_item = QTableWidgetItem(f"{test['duration']:.2f}s")
            self.widget.recent_runs_table.setItem(row, 3, duration_item)

    def _show_empty_state(self):
        """Reset dashboard to empty state"""
        # Update stats cards
        total_label = self.widget.total_tests_card.layout().itemAt(1).widget()
        passed_label = self.widget.passed_tests_card.layout().itemAt(1).widget()
        failed_label = self.widget.failed_tests_card.layout().itemAt(1).widget()
        avg_label = self.widget.avg_time_card.layout().itemAt(1).widget()
        
        total_label.setText("0")
        passed_label.setText("0")
        failed_label.setText("0")
        avg_label.setText("0s")
        
        # Clear charts
        self._show_empty_chart(self.widget.pie_chart_view, "No test data")
        self._show_empty_chart(self.widget.bar_chart_view, "No recent runs")
        
        # Clear table
        self.widget.recent_runs_table.setRowCount(0)

    def _show_empty_chart(self, view, message):
        """Display empty chart with message"""
        chart = QChart()
        chart.setTitle(message)
        view.setChart(chart)