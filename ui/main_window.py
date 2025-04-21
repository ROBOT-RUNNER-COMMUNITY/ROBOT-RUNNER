from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                            QListWidget, QListWidgetItem, QHBoxLayout, 
                            QFrame, QCheckBox, QSpinBox, QScrollArea,
                            QStackedWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from ui.logo_splash import LogoSplash
from ui.styles import apply_styles
from utils.file_utils import select_directory, select_output_directory, clear_results_directory
from utils.test_utils import export_results, load_tests, run_tests, open_report, open_log
from widgets.sidebar import SideBar
from widgets.title_bar import TitleBar
import xml.etree.ElementTree as ET

class RobotTestRunner(QWidget):
    windowStateChanged = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        
        # Initialize attributes
        self.version_label = ""
        self.test_directory = ""
        self.output_directory = ""
        self.drag_position = QPoint()
        
        # Load configuration
        self._load_config()
        
        # Initialize UI
        self.init_ui()
        self.show_splash()

    def _load_config(self):
        """Load version from config file"""
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.version_label = f"© Robot Runner {root[0].text}"

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
        self.title_bar = TitleBar("Robot Framework Test Runner", self)
        self.right_layout.addWidget(self.title_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.right_layout.addWidget(self.stacked_widget)
        
        # Main content area (contains all functionality)
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
        self._init_empty_pages()
        self._connect_signals()
        
        apply_styles(self)
        
        # Show main content by default
        self.show_main_content()

    def _init_components(self):
        """Initialize all UI components"""
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
        self.processLabel = QLabel("Number of subprocesses :")
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
        self.runButton.clicked.connect(lambda: run_tests(self))
        self.content_layout.addWidget(self.runButton)

        # Results controls
        self.fileLabel = QLabel("Select result storage location :")
        self.content_layout.addWidget(self.fileLabel)
        
        fileLayout = QHBoxLayout()
        self.fileButton = QPushButton("Choose folder")
        self.fileButton.clicked.connect(lambda: select_output_directory(self))
        fileLayout.addWidget(self.fileButton)

        self.clearButton = QPushButton("Clear results")
        self.clearButton.clicked.connect(lambda: clear_results_directory(self))
        fileLayout.addWidget(self.clearButton)
        self.content_layout.addLayout(fileLayout)

        # Results label
        self.resultLabel = QLabel("Test Results :")
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
        self.version = QLabel(f"{self.version_label}")
        self.version_layout.addWidget(self.version)
        self.content_layout.addLayout(self.version_layout)

    def _init_empty_pages(self):
        """Initialize empty pages for other menu items"""
        # Dashboard Page
        self.dashboard_page = QWidget()
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_page.setLayout(self.dashboard_layout)
        label = QLabel("Dashboard Page\n\n- Recent test runs\n- Statistics\n- Quick actions")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dashboard_layout.addWidget(label)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Analytics Page
        self.analytics_page = QWidget()
        self.analytics_layout = QVBoxLayout()
        self.analytics_page.setLayout(self.analytics_layout)
        label = QLabel("Analytics Page\n\n- Test execution trends\n- Failure analysis\n- Performance metrics")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analytics_layout.addWidget(label)
        self.stacked_widget.addWidget(self.analytics_page)
        
        # Settings Page
        self.settings_page = QWidget()
        self.settings_layout = QVBoxLayout()
        self.settings_page.setLayout(self.settings_layout)
        label = QLabel("Settings Page\n\n- Application preferences\n- Test configurations\n- UI customization")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_layout.addWidget(label)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Help Page
        self.help_page = QWidget()
        self.help_layout = QVBoxLayout()
        self.help_page.setLayout(self.help_layout)
        label = QLabel("Help Page\n\n- User manual\n- Troubleshooting\n- Contact support")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.help_layout.addWidget(label)
        self.stacked_widget.addWidget(self.help_page)

    def _connect_signals(self):
        """Connect all signals"""
        # Test Selection shows main content
        self.sidebar.testSelectionClicked.connect(self.show_main_content)
        
        # Other buttons show their respective pages
        self.sidebar.dashboardClicked.connect(lambda: self.show_page(self.dashboard_page))
        self.sidebar.analyticsClicked.connect(lambda: self.show_page(self.analytics_page))
        self.sidebar.settingsClicked.connect(lambda: self.show_page(self.settings_page))
        self.sidebar.helpClicked.connect(lambda: self.show_page(self.help_page))
        
    def show_main_content(self):
        """Show the main content area"""
        self.content_scroll.show()
        self.stacked_widget.hide()

    def show_page(self, page):
        """Show a specific page from the stacked widget"""
        self.content_scroll.hide()
        self.stacked_widget.show()
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