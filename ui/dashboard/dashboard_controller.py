import os
import subprocess
import platform
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import numpy as np
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtCharts import QChart, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
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
        self.widget.export_button.clicked.connect(self.export_to_excel)
        self.data_loader.data_loaded.connect(self.update_dashboard)
        
    def update_dashboard(self, data):
        try:
            if not data or not data.get('test_details'):
                self._show_empty_state()
                return
                
            # Update stats cards
            self._update_stats_cards(data)
            
            # Update charts
            self._update_pie_chart(data)
            self._update_bar_chart(data)
            
            # Update table with all tests
            self._update_test_runs_table(data.get('test_details', []))
            
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
        """Improved bar chart for execution times"""
        test_details = data.get('test_details', [])
        self.bar_series.clear()
        self.bar_axis_x.clear()

        if not test_details:
            self.bar_chart.setTitle("No test runs")
            return

        # Sort by duration and take top 10
        top_tests = sorted(test_details, key=lambda x: x['duration'], reverse=True)[:10]
        
        bar_set = QBarSet("Execution Time")
        bar_set.setColor(QColor("#3498db"))
        bar_set.setBorderColor(QColor("#ffffff"))
        categories = []
        
        for test in top_tests:
            bar_set.append(test['duration'])
            # Smart name truncation with ellipsis
            name = test['name']
            if len(name) > 20:
                name = name[:8] + "..." + name[-8:]
            categories.append(name)

        self.bar_series.append(bar_set)
        self.bar_axis_x.append(categories)
        
        # Configure Y axis with dynamic padding
        max_duration = max(test['duration'] for test in top_tests)
        self.bar_axis_y.setRange(0, max(1, max_duration * 1.15))
        
        # Chart styling
        self.bar_chart.setTitle("Top 10 Longest Running Tests")
        self.bar_chart.setTitleFont(QFont("Arial", 10, QFont.Weight.Bold))

    def _update_test_runs_table(self, test_details):
        """Update the table to show all test runs"""
        self.widget.recent_runs_table.setRowCount(0)
        
        if not test_details:
            return
            
        # Sort by most recent first
        test_details_sorted = sorted(test_details, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        self.widget.recent_runs_table.setRowCount(len(test_details_sorted))
        
        for row, test in enumerate(test_details_sorted):
            # Test Name
            name_item = QTableWidgetItem(test.get('name', 'Unnamed Test'))
            self.widget.recent_runs_table.setItem(row, 0, name_item)
            
            # Timestamp
            timestamp = test.get('timestamp', datetime.min)
            if isinstance(timestamp, str):
                time_item = QTableWidgetItem(timestamp)
            else:
                time_item = QTableWidgetItem(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.widget.recent_runs_table.setItem(row, 1, time_item)
            
            # Status with color
            status = test.get('status', 'UNKNOWN')
            status_item = QTableWidgetItem(status)
            if status == 'PASS':
                status_item.setBackground(QColor("#2ecc71"))
            elif status == 'FAIL':
                status_item.setBackground(QColor("#e74c3c"))
            else:
                status_item.setBackground(QColor("#f39c12"))
            status_item.setForeground(QColor("#ffffff"))
            self.widget.recent_runs_table.setItem(row, 2, status_item)
            
            # Duration
            duration = test.get('duration', 0)
            duration_item = QTableWidgetItem(f"{duration:.2f}s")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.widget.recent_runs_table.setItem(row, 3, duration_item)

    def export_to_excel(self):
        """Export all test data to Excel and open it"""
        try:
            if not self.data_loader.results_dir:
                QMessageBox.warning(self.widget, "Export Error", "No results directory configured")
                return
                
            # Check if output directory exists
            if not os.path.exists(self.data_loader.results_dir):
                QMessageBox.warning(self.widget, "Export Error", 
                                   f"Results directory doesn't exist:\n{self.data_loader.results_dir}")
                return
                
            output_xml = os.path.join(self.data_loader.results_dir, "output.xml")
            if not os.path.exists(output_xml):
                QMessageBox.warning(self.widget, "Export Error", "output.xml not found in results directory")
                return
                
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(self.data_loader.results_dir, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"RobotTestReport_{timestamp}.xlsx"
            export_path = os.path.join(reports_dir, export_filename)
            
            # Check if file is already open
            if self._is_file_open(export_path):
                QMessageBox.warning(self.widget, "Export Error", 
                                  "Please close the previous report before exporting a new one")
                return
            
            # Parse XML data
            tree = ET.parse(output_xml)
            root = tree.getroot()
            
            # Prepare data for export
            test_data = []
            for test in root.findall('.//test'):
                test_name = test.get('name', 'Unnamed Test')
                test_status = test.find('status')
                
                if test_status is not None:
                    try:
                        start = datetime.strptime(
                            test_status.get('starttime', '19700101 00:00:00.000'), 
                            "%Y%m%d %H:%M:%S.%f"
                        )
                        end = datetime.strptime(
                            test_status.get('endtime', '19700101 00:00:00.000'), 
                            "%Y%m%d %H:%M:%S.%f"
                        )
                        duration = (end - start).total_seconds()
                        
                        test_data.append({
                            'Test Name': test_name,
                            'Timestamp': start,
                            'Status': test_status.get('status', 'UNKNOWN'),
                            'Duration (s)': duration,
                            'Message': test_status.text.strip() if test_status.text else ""
                        })
                        
                    except ValueError as e:
                        continue
            
            if not test_data:
                QMessageBox.warning(self.widget, "Export Error", "No test data found to export")
                return
                
            # Create DataFrame
            df = pd.DataFrame(test_data)
            
            # Create Excel writer
            with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
                # Write test data
                df.to_excel(writer, sheet_name='Test Results', index=False)
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Test Results']
                
                # Add conditional formatting for status
                format_pass = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
                format_fail = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                format_unknown = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'})
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'PASS',
                    'format': format_pass
                })
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'FAIL',
                    'format': format_fail
                })
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'UNKNOWN',
                    'format': format_unknown
                })
                
                # Add charts sheet
                chart_sheet = workbook.add_worksheet('Charts')
                
                # Create pie chart
                pie_chart = workbook.add_chart({'type': 'pie'})
                
                # Count statuses
                status_counts = df['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                # Write status counts to a new sheet
                status_counts.to_excel(writer, sheet_name='Status Counts', index=False)
                
                pie_chart.add_series({
                    'name': 'Test Results',
                    'categories': ['Status Counts', 1, 0, len(status_counts), 0],
                    'values': ['Status Counts', 1, 1, len(status_counts), 1],
                    'data_labels': {'percentage': True, 'category': True}
                })
                
                pie_chart.set_title({'name': 'Test Results Distribution'})
                pie_chart.set_style(10)
                chart_sheet.insert_chart('B2', pie_chart)
                
                # Create bar chart of top 20 longest tests
                bar_chart = workbook.add_chart({'type': 'column'})
                
                # Get top 20 tests by duration
                top_tests = df.nlargest(20, 'Duration (s)')
                
                bar_chart.add_series({
                    'name': 'Duration (s)',
                    'categories': ['Test Results', 1, 0, min(20, len(df)), 0],
                    'values': ['Test Results', 1, 3, min(20, len(df)), 3],
                    'fill': {'color': '#3498db'},
                })
                
                bar_chart.set_title({'name': 'Top 20 Longest Running Tests'})
                bar_chart.set_x_axis({'name': 'Test Name'})
                bar_chart.set_y_axis({'name': 'Duration (seconds)'})
                bar_chart.set_style(11)
                chart_sheet.insert_chart('B20', bar_chart)
                
                # Auto-adjust columns width
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
            
            # Open the Excel file
            self._open_file(export_path)
            
            QMessageBox.information(self.widget, "Export Successful", 
                                  f"Report exported to:\n{export_path}")
            
        except PermissionError:
            QMessageBox.warning(self.widget, "Export Error", 
                              "Please close the previous report before exporting a new one")
        except Exception as e:
            QMessageBox.critical(self.widget, "Export Error", 
                              f"Failed to export report:\n{str(e)}")

    def _is_file_open(self, filepath):
        """Check if a file is currently open (Windows-specific)"""
        if not os.path.exists(filepath):
            return False
            
        if platform.system() == 'Windows':
            try:
                # Try to open the file in exclusive mode
                fd = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.close(fd)
                os.unlink(filepath)
                return False
            except OSError:
                return True
        else:
            # For non-Windows systems, we can't reliably check
            return False

    def _open_file(self, filepath):
        """Open the file with the default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath], check=True)
            else:  # Linux and others
                subprocess.run(['xdg-open', filepath], check=True)
        except Exception as e:
            print(f"Error opening file: {e}")
            QMessageBox.information(self.widget, "Report Ready", 
                                  f"Report saved to:\n{filepath}\n\nPlease open it manually.")

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
        
        self.bar_chart.setTitle("No test runs")
        self.bar_series.clear()
        self.bar_axis_x.clear()
        
        # Table
        self.widget.recent_runs_table.setRowCount(0)