import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib

from ui.logo_splash import LogoSplash
from ui.styles import apply_styles
from utils.file_utils import clear_results_directory, select_directory, select_output_directory
from utils.test_utils import export_results, load_tests, open_log, open_report, run_tests
from widgets.sidebar import SideBar
from widgets.title_bar import TitleBar
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QFrame, QCheckBox, QSpinBox,
    QScrollArea, QStackedWidget, QSizePolicy, QTableWidget,
    QHeaderView, QTableWidgetItem, QApplication
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

# Suppress Qt network errors
os.environ["QT_LOGGING_RULES"] = "qt.network.ssl.warning=false"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging"

class DashboardDataLoader(QObject):
    data_loaded = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.results_dir = os.path.join("tests-for-validation", "Results")
        self.is_loading = False
        self.last_modified = 0
        
    def load_data(self, force=False):
        if self.is_loading:
            return
            
        # Check if results directory has changed
        current_modified = 0
        if os.path.exists(self.results_dir):
            for root, _, files in os.walk(self.results_dir):
                if 'output.xml' in files:
                    file_path = os.path.join(root, 'output.xml')
                    current_modified = max(current_modified, os.path.getmtime(file_path))
        
        if not force and current_modified <= self.last_modified:
            return
            
        self.last_modified = current_modified
        self.is_loading = True
        stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'execution_times': [],
            'recent_runs': [],
            'test_details': []
        }
        
        try:
            if os.path.exists(self.results_dir):
                for root, _, files in os.walk(self.results_dir):
                    if 'output.xml' in files:
                        try:
                            xml_path = os.path.join(root, 'output.xml')
                            tree = ET.parse(xml_path)
                            xml_root = tree.getroot()
                            
                            # Get statistics
                            for stat in xml_root.findall('.//statistics/total/stat'):
                                if stat.get('name') == 'All Tests':
                                    stats['total_tests'] += int(stat.find('total').text)
                                    stats['passed'] += int(stat.find('pass').text)
                                    stats['failed'] += int(stat.find('fail').text)
                            
                            # Get suite and test details
                            for suite in xml_root.findall('.//suite'):
                                suite_name = suite.get('name')
                                status = suite.find('.//status')
                                
                                if status is not None:
                                    try:
                                        start = datetime.strptime(
                                            status.get('starttime'), 
                                            "%Y%m%d %H:%M:%S.%f"
                                        )
                                        end = datetime.strptime(
                                            status.get('endtime'), 
                                            "%Y%m%d %H:%M:%S.%f"
                                        )
                                        duration = (end - start).total_seconds()
                                        
                                        stats['recent_runs'].append({
                                            'suite': suite_name,
                                            'timestamp': start,
                                            'status': status.get('status'),
                                            'duration': duration
                                        })
                                        stats['execution_times'].append(duration)
                                        
                                        # Get individual test details
                                        for test in suite.findall('.//test'):
                                            test_status = test.find('.//status')
                                            if test_status is not None:
                                                stats['test_details'].append({
                                                    'suite': suite_name,
                                                    'test': test.get('name'),
                                                    'status': test_status.get('status'),
                                                    'start': test_status.get('starttime'),
                                                    'end': test_status.get('endtime'),
                                                    'message': test_status.text.strip() if test_status.text else ""
                                                })
                                    except ValueError as e:
                                        print(f"Error parsing timestamps: {e}")
                                        continue
                                    
                        except ET.ParseError as e:
                            print(f"Error parsing XML {xml_path}: {e}")
                            continue
            
            if stats['recent_runs']:
                stats['recent_runs'].sort(key=lambda x: x['timestamp'], reverse=True)
                
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
        finally:
            self.is_loading = False
            self.data_loaded.emit(stats)

class RobotTestRunner(QWidget):
    windowStateChanged = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.version_label = ""
        self.test_directory = ""
        self.output_directory = ""
        self.drag_position = QPoint()
        self._load_config()
        self.init_ui()
        self.show_splash()

    def _load_config(self):
        try:
            tree = ET.parse('config.xml')
            root = tree.getroot()
            self.version_label = f"© Robot Runner {root[0].text}"
        except Exception as e:
            print(f"Error loading config: {e}")
            self.version_label = "© Robot Runner"

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(1300, 700)
        
        # Main layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)
        self.setLayout(self.main_h_layout)
        
        # Sidebar
        self.sidebar = SideBar()
        self.main_h_layout.addWidget(self.sidebar)
        
        # Right side container
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_container.setLayout(self.right_layout)
        
        # Title bar
        self.title_bar = TitleBar("", self)
        self.right_layout.addWidget(self.title_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.right_layout.addWidget(self.stacked_widget)
        
        # Main content area
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_scroll.setWidget(self.content_widget)
        self.right_layout.addWidget(self.content_scroll)
        
        self.main_h_layout.addWidget(self.right_container)
        
        # Initialize components
        self._init_components()
        self._init_dashboard_page()
        self._init_analytics_page()
        self._init_settings_page()
        self._init_help_page()
        self._connect_signals()
        
        # Add update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(5000)  # Check every 5 seconds

        apply_styles(self)
        self.show_main_content()

    def check_for_updates(self):
        """Check for new test results and update UI if found"""
        if hasattr(self, 'dashboard_loader'):
            self.dashboard_loader.load_data()

    def _init_components(self):
        """Initialize test selection components"""
        # Directory controls
        self.label = QLabel("Select a folder containing .robot files")
        self.content_layout.addWidget(self.label)
        
        self.selectButton = QPushButton("Select Folder")
        self.selectButton.clicked.connect(lambda: select_directory(self))
        self.content_layout.addWidget(self.selectButton)

        # Test selection controls
        self.layout_horizontal = QHBoxLayout()
        self.selectAllCheckBox = QCheckBox("Select all tests")
        self.selectAllCheckBox.stateChanged.connect(self.toggle_select_all_tests)
        self.layout_horizontal.addWidget(self.selectAllCheckBox)

        self.refreshLayout = QHBoxLayout()
        self.refreshButton = QPushButton("Refresh tests")
        self.refreshButton.setFixedSize(100, 40)
        self.refreshButton.clicked.connect(lambda: load_tests(self))
        self.refreshLayout.addWidget(self.refreshButton)

        self.loadingLabel = QLabel()
        self.loadingLabel.setFixedSize(30, 30)
        self.loadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.refreshLayout.addWidget(self.loadingLabel)
        self.layout_horizontal.addLayout(self.refreshLayout)
        self.content_layout.addLayout(self.layout_horizontal)

        # Test list
        self.testList = QListWidget()
        self.content_layout.addWidget(self.testList)

        # Parameters
        paramLayout = QHBoxLayout()
        self.processLabel = QLabel("Number of subprocesses:")
        self.processInput = QSpinBox()
        self.processInput.setValue(2)
        self.processInput.setFixedWidth(50)
        self.processInput.setMinimum(1)
        self.processInput.setMaximum(50)
        paramLayout.addWidget(self.processLabel)
        paramLayout.addWidget(self.processInput)
        self.content_layout.addLayout(paramLayout)

        # Run button
        self.runButton = QPushButton("Run selected tests")
        self.runButton.clicked.connect(self.run_tests_with_update)
        self.content_layout.addWidget(self.runButton)

        # Results controls
        self.fileLabel = QLabel("Select result storage location:")
        self.content_layout.addWidget(self.fileLabel)
        
        fileLayout = QHBoxLayout()
        self.fileButton = QPushButton("Choose folder")
        self.fileButton.clicked.connect(lambda: select_output_directory(self))
        fileLayout.addWidget(self.fileButton)

        self.clearButton = QPushButton("Clear results")
        self.clearButton.clicked.connect(self.clear_results_with_update)
        fileLayout.addWidget(self.clearButton)
        self.content_layout.addLayout(fileLayout)

        # Results label
        self.resultLabel = QLabel("Test Results:")
        self.content_layout.addWidget(self.resultLabel)
        
        # Report and log buttons
        reportLogLayout = QHBoxLayout()
        self.reportButton = QPushButton("Open Report")
        self.reportButton.clicked.connect(lambda: open_report(self))
        reportLogLayout.addWidget(self.reportButton)

        self.logButton = QPushButton("Open Log")
        self.logButton.clicked.connect(lambda: open_log(self))
        reportLogLayout.addWidget(self.logButton)

        self.exportResults = QPushButton("Export Results")
        self.exportResults.clicked.connect(lambda: export_results(self))
        reportLogLayout.addWidget(self.exportResults)
        self.content_layout.addLayout(reportLogLayout)

        # Version label
        self.version_layout = QVBoxLayout()
        self.version = QLabel(self.version_label)
        self.version_layout.addWidget(self.version)
        self.content_layout.addLayout(self.version_layout)

    def run_tests_with_update(self):
        """Run tests and then update dashboard"""
        run_tests(self)
        if hasattr(self, 'dashboard_loader'):
            QTimer.singleShot(1000, lambda: self.dashboard_loader.load_data(force=True))

    def clear_results_with_update(self):
        """Clear results and update dashboard"""
        clear_results_directory(self)
        if hasattr(self, 'dashboard_loader'):
            QTimer.singleShot(1000, lambda: self.dashboard_loader.load_data(force=True))

    def _init_dashboard_page(self):
        """Initialize the dashboard page"""
        self.dashboard_page = QWidget()
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_page.setLayout(self.dashboard_layout)
        
        # Refresh button for dashboard
        refresh_layout = QHBoxLayout()
        self.dashboard_refresh = QPushButton("Refresh Dashboard")
        self.dashboard_refresh.clicked.connect(lambda: self.dashboard_loader.load_data(force=True))
        refresh_layout.addWidget(self.dashboard_refresh)
        refresh_layout.addStretch()
        self.dashboard_layout.addLayout(refresh_layout)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        self.total_tests_card = self._create_stat_card("Total Tests", "0")
        self.passed_tests_card = self._create_stat_card("Passed", "0", "#2ecc71")
        self.failed_tests_card = self._create_stat_card("Failed", "0", "#e74c3c")
        self.avg_time_card = self._create_stat_card("Avg Time", "0s", "#3498db")
        
        stats_layout.addWidget(self.total_tests_card)
        stats_layout.addWidget(self.passed_tests_card)
        stats_layout.addWidget(self.failed_tests_card)
        stats_layout.addWidget(self.avg_time_card)
        self.dashboard_layout.addLayout(stats_layout)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Pie Chart
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setMinimumSize(400, 300)
        
        # Bar Chart
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setMinimumSize(400, 300)
        
        charts_layout.addWidget(self.pie_chart_view)
        charts_layout.addWidget(self.bar_chart_view)
        self.dashboard_layout.addLayout(charts_layout)
        
        # Recent Runs Table
        self.recent_runs_table = QTableWidget()
        self.recent_runs_table.setColumnCount(4)
        self.recent_runs_table.setHorizontalHeaderLabels(["Test Suite", "Timestamp", "Status", "Duration"])
        self.recent_runs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_runs_table.setMaximumHeight(200)
        self.dashboard_layout.addWidget(QLabel("Recent Test Runs:"))
        self.dashboard_layout.addWidget(self.recent_runs_table)
        
        # Data loader
        self.dashboard_loader = DashboardDataLoader()
        self.dashboard_loader.data_loaded.connect(self.update_dashboard)
        QTimer.singleShot(100, lambda: self.dashboard_loader.load_data(force=True))
        
        self.stacked_widget.addWidget(self.dashboard_page)

    def _init_analytics_page(self):
        """Initialize the analytics page"""
        self.analytics_page = QWidget()
        self.analytics_layout = QVBoxLayout()
        self.analytics_page.setLayout(self.analytics_layout)
        
        # Refresh button for analytics
        refresh_layout = QHBoxLayout()
        self.analytics_refresh = QPushButton("Refresh Analytics")
        self.analytics_refresh.clicked.connect(lambda: self.dashboard_loader.load_data(force=True))
        refresh_layout.addWidget(self.analytics_refresh)
        refresh_layout.addStretch()
        self.analytics_layout.addLayout(refresh_layout)
        
        # Time Series Chart
        self.time_series_fig, self.time_series_ax = plt.subplots(figsize=(6, 4))
        self.time_series_canvas = FigureCanvas(self.time_series_fig)
        self.time_series_canvas.setMinimumSize(600, 400)
        
        # Failure Analysis Chart
        self.failure_fig, self.failure_ax = plt.subplots(figsize=(6, 4))
        self.failure_canvas = FigureCanvas(self.failure_fig)
        self.failure_canvas.setMinimumSize(600, 400)
        
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.time_series_canvas)
        charts_layout.addWidget(self.failure_canvas)
        self.analytics_layout.addLayout(charts_layout)
        
        self.dashboard_loader.data_loaded.connect(self.update_analytics)
        self.stacked_widget.addWidget(self.analytics_page)

    def _init_settings_page(self):
        """Initialize settings page"""
        self.settings_page = QWidget()
        self.settings_layout = QVBoxLayout()
        self.settings_page.setLayout(self.settings_layout)
        label = QLabel("Settings Page\n\n- Application preferences\n- Test configurations\n- UI customization")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_layout.addWidget(label)
        self.stacked_widget.addWidget(self.settings_page)

    def _init_help_page(self):
        """Initialize help page"""
        self.help_page = QWidget()
        self.help_layout = QVBoxLayout()
        self.help_page.setLayout(self.help_layout)
        label = QLabel("Help Page\n\n- User manual\n- Troubleshooting\n- Contact support")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.help_layout.addWidget(label)
        self.stacked_widget.addWidget(self.help_page)

    def _connect_signals(self):
        """Connect all signals"""
        self.sidebar.testSelectionClicked.connect(self.show_main_content)
        self.sidebar.dashboardClicked.connect(self.show_dashboard)
        self.sidebar.analyticsClicked.connect(self.show_analytics)
        self.sidebar.settingsClicked.connect(lambda: self.show_page(self.settings_page))
        self.sidebar.helpClicked.connect(lambda: self.show_page(self.help_page))

    def show_dashboard(self):
        """Show dashboard and refresh data"""
        self.show_page(self.dashboard_page)
        self.dashboard_loader.load_data(force=True)

    def show_analytics(self):
        """Show analytics and refresh data"""
        self.show_page(self.analytics_page)
        self.dashboard_loader.load_data(force=True)

    def show_main_content(self):
        """Show the main test selection content"""
        self.content_scroll.show()
        self.stacked_widget.hide()

    def show_page(self, page):
        """Show a specific page"""
        self.content_scroll.hide()
        self.stacked_widget.show()
        self.stacked_widget.setCurrentWidget(page)

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

    def update_dashboard(self, data):
        try:
            if not data:
                return
                
            # Update stats cards
            self.total_tests_card.layout().itemAt(1).widget().setText(str(data['total_tests']))
            self.passed_tests_card.layout().itemAt(1).widget().setText(str(data['passed']))
            self.failed_tests_card.layout().itemAt(1).widget().setText(str(data['failed']))
            
            avg_time = np.mean(data['execution_times']) if data['execution_times'] else 0
            self.avg_time_card.layout().itemAt(1).widget().setText(f"{avg_time:.2f}s")
            
            # Update pie chart
            pie_series = QPieSeries()
            if data['passed'] > 0:
                passed_slice = pie_series.append("Passed", data['passed'])
                passed_slice.setColor(QColor("#2ecc71"))
            if data['failed'] > 0:
                failed_slice = pie_series.append("Failed", data['failed'])
                failed_slice.setColor(QColor("#e74c3c"))
            
            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setTitle("Test Results Distribution")
            pie_chart.legend().setVisible(True)
            pie_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            self.pie_chart_view.setChart(pie_chart)
            
            # Update bar chart with execution times
            bar_set = QBarSet("Execution Time (s)")
            if data['recent_runs']:
                recent_runs = sorted(data['recent_runs'], key=lambda x: x['timestamp'])
                categories = []
                for run in recent_runs[-5:]:  # Show last 5 runs
                    bar_set.append(run['duration'])
                    categories.append(run['suite'][:15] + "\n" + 
                                    run['timestamp'].strftime("%m-%d %H:%M"))
            else:
                bar_set.append(0)
                categories = ["No data"]
            
            bar_series = QBarSeries()
            bar_series.append(bar_set)
            
            bar_chart = QChart()
            bar_chart.addSeries(bar_series)
            bar_chart.setTitle("Test Execution Times")
            bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            bar_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            bar_series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            bar_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            bar_series.attachAxis(axis_y)
            
            self.bar_chart_view.setChart(bar_chart)
            
            # Update recent runs table with more details
            self.recent_runs_table.setRowCount(0)
            for run in data['recent_runs'][:5]:  # Show only 5 most recent
                row = self.recent_runs_table.rowCount()
                self.recent_runs_table.insertRow(row)
                
                self.recent_runs_table.setItem(row, 0, QTableWidgetItem(run['suite']))
                self.recent_runs_table.setItem(row, 1, QTableWidgetItem(run['timestamp'].strftime("%Y-%m-%d %H:%M:%S")))
                
                status_item = QTableWidgetItem(run['status'])
                if run['status'] == 'PASS':
                    status_item.setBackground(QColor("#2ecc71"))
                else:
                    status_item.setBackground(QColor("#e74c3c"))
                self.recent_runs_table.setItem(row, 2, status_item)
                
                duration_item = QTableWidgetItem(f"{run['duration']:.2f}s")
                self.recent_runs_table.setItem(row, 3, duration_item)
                
        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def update_analytics(self, data):
        """Update analytics charts with data from test results"""
        try:
            if not data:
                return
                
            # Prepare data for analytics
            dates = []
            execution_times = []
            failure_counts = []
            test_details = []
            
            if data.get('recent_runs'):
                # Group by date for time series
                date_groups = {}
                for run in data['recent_runs']:
                    date = run['timestamp'].date()
                    if date not in date_groups:
                        date_groups[date] = {
                            'execution_time': 0,
                            'failures': 0,
                            'tests': 0
                        }
                    date_groups[date]['execution_time'] += run.get('duration', 0)
                    date_groups[date]['failures'] += 1 if run['status'] == 'FAIL' else 0
                    date_groups[date]['tests'] += 1
                
                dates = sorted(date_groups.keys())
                execution_times = [date_groups[d]['execution_time'] for d in dates]
                failure_counts = [date_groups[d]['failures'] for d in dates]
            
            if not dates:  # No data found
                dates = [datetime.now().date()]
                execution_times = [0]
                failure_counts = [0]
            
            # Time Series Chart
            self.time_series_ax.clear()
            if len(dates) > 1:
                self.time_series_ax.plot(dates, execution_times, marker='o', color='#3498db', label='Total Time')
                self.time_series_ax.set_ylabel('Execution Time (s)', color='#3498db')
                self.time_series_ax.tick_params(axis='y', labelcolor='#3498db')
                
                # Add failure rate as second y-axis
                ax2 = self.time_series_ax.twinx()
                failure_rates = [f/t if t > 0 else 0 for f, t in zip(failure_counts, [date_groups[d]['tests'] for d in dates])]
                ax2.plot(dates, failure_rates, marker='x', color='#e74c3c', linestyle='--', label='Failure Rate')
                ax2.set_ylabel('Failure Rate', color='#e74c3c')
                ax2.tick_params(axis='y', labelcolor='#e74c3c')
                
                self.time_series_ax.legend(loc='upper left')
                ax2.legend(loc='upper right')
            else:
                self.time_series_ax.text(0.5, 0.5, 'Not enough data for time series', 
                                       ha='center', va='center', transform=self.time_series_ax.transAxes)
            
            self.time_series_ax.set_title('Test Execution Trends', pad=20)
            self.time_series_ax.set_xlabel('Date')
            self.time_series_ax.grid(True, linestyle='--', alpha=0.6)
            self.time_series_fig.tight_layout()
            self.time_series_canvas.draw()
            
            # Failure Analysis Chart
            self.failure_ax.clear()
            if any(failure_counts):
                # Group failures by test name if available
                if data.get('test_details'):
                    failure_reasons = {}
                    for test in data['test_details']:
                        if test['status'] == 'FAIL':
                            key = f"{test['suite']}.{test['test']}"
                            failure_reasons[key] = failure_reasons.get(key, 0) + 1
                    
                    if failure_reasons:
                        reasons = sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:10]
                        labels = [r[0] for r in reasons]
                        counts = [r[1] for r in reasons]
                        
                        self.failure_ax.barh(labels, counts, color='#e74c3c')
                        self.failure_ax.set_title('Top 10 Failing Tests', pad=20)
                        self.failure_ax.set_xlabel('Failure Count')
                    else:
                        self.failure_ax.text(0.5, 0.5, 'No failure data available', 
                                          ha='center', va='center', transform=self.failure_ax.transAxes)
                else:
                    self.failure_ax.bar([d.strftime("%m-%d") for d in dates], failure_counts, color='#e74c3c')
                    self.failure_ax.set_title('Daily Failures', pad=20)
                    self.failure_ax.set_xlabel('Date')
                    self.failure_ax.set_ylabel('Failure Count')
            else:
                self.failure_ax.text(0.5, 0.5, 'No failures recorded', 
                                    ha='center', va='center', transform=self.failure_ax.transAxes)
            
            self.failure_ax.grid(True, linestyle='--', alpha=0.6)
            self.failure_fig.tight_layout()
            self.failure_canvas.draw()
            
        except Exception as e:
            print(f"Error updating analytics: {e}")

    def toggle_select_all_tests(self, state):
        check_state = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        for i in range(self.testList.count()):
            self.testList.item(i).setCheckState(check_state)

    def show_splash(self):
        self.splash = LogoSplash(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotTestRunner()
    window.show()
    sys.exit(app.exec())