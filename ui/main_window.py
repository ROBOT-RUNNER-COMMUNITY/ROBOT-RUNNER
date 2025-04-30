# ui/main_window.py
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QCheckBox, QSpinBox, QScrollArea, 
    QStackedWidget, QMessageBox, QLineEdit, QGroupBox, 
    QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer, QSettings
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont

from ui.logo_splash import LogoSplash
from ui.styles import apply_styles
from utils.file_utils import clear_results_directory, select_directory, select_output_directory
from utils.test_utils import export_results, load_tests, open_log, open_report, run_tests
from widgets.sidebar import SideBar
from widgets.title_bar import TitleBar
from ui.dashboard.dashboard_loader import DashboardDataLoader
from ui.dashboard.dashboard_widget import DashboardWidget
from ui.dashboard.dashboard_controller import DashboardController
from ui.analytics.analytics_widget import AnalyticsWidget
from ui.analytics.analytics_controller import AnalyticsController
from ui.help.help_widget import HelpWidget
from ui.help.help_controller import HelpController


matplotlib.use('Qt5Agg')

class RobotTestRunner(QWidget):
    windowStateChanged = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.version_label = ""
        self.test_directory = ""
        self.output_directory = ""
        self.drag_position = QPoint()
        self.settings = QSettings("RobotTestRunner", "RobotTestRunner")
        self._load_config()
        self.init_ui()
        self.show_splash()

    def _load_config(self):
        try:
            # Try multiple paths to locate the config file
            config_paths = [
                'config.xml',  # Development path
                os.path.join(os.path.dirname(sys.executable), 'config.xml'),  # EXE location
                os.path.join(sys._MEIPASS, 'config.xml')  # PyInstaller temp directory
            ]
            
            config_loaded = False
            for path in config_paths:
                if os.path.exists(path):
                    tree = ET.parse(path)
                    root = tree.getroot()
                    self.version_label = f"© Robot Runner {root[0].text}"
                    config_loaded = True
                    break
                    
            if not config_loaded:
                raise FileNotFoundError("Config file not found in any standard location")
                
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
        self.title_bar = TitleBar("Robot Test Runner", self)
        self.right_layout.addWidget(self.title_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.right_layout.addWidget(self.stacked_widget)
        
        # Main content area
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_scroll.setWidget(self.content_widget)
        self.stacked_widget.addWidget(self.content_scroll)
        
        self.main_h_layout.addWidget(self.right_container)
        
        # Initialize components
        self._init_components()
        self._init_dashboard_page()
        self._init_analytics_page()
        self._init_settings_page()
        self._init_help_page()
        self._connect_signals()
        
        apply_styles(self)
        self.show_main_content()

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
        self.processInput.setValue(self.settings.value("subprocess_count", 2, type=int))
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

    def _init_dashboard_page(self):
        """Initialize the dashboard page"""
        self.dashboard_loader = DashboardDataLoader(self.output_directory)
        self.dashboard_page = DashboardWidget()
        self.dashboard_controller = DashboardController(self.dashboard_page, self.dashboard_loader)
        self.stacked_widget.addWidget(self.dashboard_page)

    def _init_analytics_page(self):
        """Initialize the analytics page"""
        self.analytics_page = AnalyticsWidget()
        self.analytics_controller = AnalyticsController(self.analytics_page, self.dashboard_loader)
        self.stacked_widget.addWidget(self.analytics_page)

    def _init_settings_page(self):
        """Initialize settings page with working options"""
        self.settings_page = QWidget()
        self.settings_layout = QVBoxLayout()
        self.settings_page.setLayout(self.settings_layout)
        
        # Execution Settings Group
        execution_group = QGroupBox("Execution Settings")
        execution_layout = QFormLayout()
        
        # Default Process Count
        self.default_process_count = QSpinBox()
        self.default_process_count.setValue(self.settings.value("subprocess_count", 2, type=int))
        self.default_process_count.setRange(1, 50)
        execution_layout.addRow("Default Process Count:", self.default_process_count)
        
        # Default Timeout
        self.default_timeout = QSpinBox()
        self.default_timeout.setValue(self.settings.value("default_timeout", 300, type=int))
        self.default_timeout.setRange(30, 3600)
        self.default_timeout.setSuffix(" seconds")
        execution_layout.addRow("Default Test Timeout:", self.default_timeout)
        
        # Retry Failed Tests
        self.retry_failed = QCheckBox("Automatically retry failed tests")
        self.retry_failed.setChecked(self.settings.value("retry_failed", False, type=bool))
        execution_layout.addRow(self.retry_failed)
        
        execution_group.setLayout(execution_layout)
        self.settings_layout.addWidget(execution_group)
        
        # UI Settings Group
        ui_group = QGroupBox("Interface Settings")
        ui_layout = QFormLayout()
        
        # Font Size
        self.font_size = QSpinBox()
        self.font_size.setValue(self.settings.value("font_size", 10, type=int))
        self.font_size.setRange(8, 16)
        ui_layout.addRow("Font Size:", self.font_size)
        
        # Show Tooltips
        self.show_tooltips = QCheckBox("Show tooltips")
        self.show_tooltips.setChecked(self.settings.value("show_tooltips", True, type=bool))
        ui_layout.addRow(self.show_tooltips)
        
        ui_group.setLayout(ui_layout)
        self.settings_layout.addWidget(ui_group)
        
        # Results Settings Group
        results_group = QGroupBox("Results Settings")
        results_layout = QFormLayout()
        
        # Auto-open Report
        self.auto_open_report = QCheckBox("Open report after test completion")
        self.auto_open_report.setChecked(self.settings.value("auto_open_report", False, type=bool))
        results_layout.addRow(self.auto_open_report)
        
        # Keep History
        self.keep_history = QSpinBox()
        self.keep_history.setValue(self.settings.value("keep_history", 5, type=int))
        self.keep_history.setRange(1, 30)
        self.keep_history.setSuffix(" days")
        results_layout.addRow("Keep results history:", self.keep_history)
        
        results_group.setLayout(results_layout)
        self.settings_layout.addWidget(results_group)
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        # Save Button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_button)
        
        # Reset Button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._reset_settings)
        buttons_layout.addWidget(reset_button)
        
        self.settings_layout.addLayout(buttons_layout)
        self.settings_layout.addStretch()
        self.stacked_widget.addWidget(self.settings_page)

    def _init_help_page(self):
        """Initialize the simplified help page"""
        self.help_page = HelpWidget()
        self.help_controller = HelpController(self.help_page)
        self.stacked_widget.addWidget(self.help_page)

    def _handle_help_link(self, url):
        """Handle help link clicks"""
        print(f"Help link clicked: {url}")

    def _save_settings(self):
        """Save settings to persistent storage"""
        # Execution Settings
        self.settings.setValue("subprocess_count", self.default_process_count.value())
        self.settings.setValue("default_timeout", self.default_timeout.value())
        self.settings.setValue("retry_failed", self.retry_failed.isChecked())
        
        # UI Settings
        self.settings.setValue("font_size", self.font_size.value())
        self.settings.setValue("show_tooltips", self.show_tooltips.isChecked())
        
        # Results Settings
        self.settings.setValue("auto_open_report", self.auto_open_report.isChecked())
        self.settings.setValue("keep_history", self.keep_history.value())
        
        # Update current values in the main interface
        self.processInput.setValue(self.default_process_count.value())
        
        # Apply font size changes
        font = QFont()
        font.setPointSize(self.font_size.value())
        self.setFont(font)
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

    def _reset_settings(self):
        """Reset settings to default values"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            
            # Execution Settings
            self.default_process_count.setValue(2)
            self.default_timeout.setValue(300)
            self.retry_failed.setChecked(False)
            
            # UI Settings
            self.font_size.setValue(10)
            self.show_tooltips.setChecked(True)
            
            # Results Settings
            self.auto_open_report.setChecked(False)
            self.keep_history.setValue(5)
            
            # Update main interface
            self.processInput.setValue(2)
            
            # Reset font size
            font = QFont()
            font.setPointSize(10)
            self.setFont(font)
            
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to default values.")

    def run_tests_with_update(self):
        """Run tests and then update dashboard"""
        try:
            # Save process count to settings
            self.settings.setValue("subprocess_count", self.processInput.value())
            
            # Clear old results first
            clear_results_directory(self)
            # Run new tests
            run_tests(self)
            
            # Auto-open report if enabled
            if self.settings.value("auto_open_report", False, type=bool):
                QTimer.singleShot(1000, lambda: open_report(self))
            
            # Only refresh if we're on dashboard or analytics page
            if not self.content_scroll.isVisible():
                QTimer.singleShot(2000, self.force_refresh_current_page)
        except Exception as e:
            QMessageBox.warning(self, "Test Execution Error", f"Failed to run tests: {str(e)}")

    def force_refresh_current_page(self):
        """Force refresh of the current page"""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget == self.dashboard_page:
            self.dashboard_loader.load_data(force=True)
        elif current_widget == self.analytics_page:
            self.dashboard_loader.load_data(force=True)

    def clear_results_with_update(self):
        """Clear results and update dashboard"""
        clear_results_directory(self)
        # Only refresh if we're on dashboard or analytics page
        if not self.content_scroll.isVisible():
            self.force_refresh_current_page()
        
    def _connect_signals(self):
        """Connect all signals"""
        self.sidebar.testSelectionClicked.connect(self.show_main_content)
        self.sidebar.dashboardClicked.connect(self.show_dashboard)
        self.sidebar.analyticsClicked.connect(self.show_analytics)
        self.sidebar.settingsClicked.connect(lambda: self.show_page(self.settings_page))
        self.sidebar.helpClicked.connect(lambda: self.show_page(self.help_page))

    def show_dashboard(self):
        """Show dashboard"""
        self.show_page(self.dashboard_page)

    def show_analytics(self):
        """Show analytics"""
        self.show_page(self.analytics_page)

    def show_main_content(self):
        """Show the main test selection content"""
        self.stacked_widget.setCurrentWidget(self.content_scroll)

    def show_page(self, page):
        """Show a specific page"""
        self.stacked_widget.setCurrentWidget(page)

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