from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                            QListWidget, QListWidgetItem, QHBoxLayout, 
                            QFrame, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from ui.logo_splash import LogoSplash
from ui.styles import apply_styles
from utils.file_utils import select_directory, select_output_directory, clear_results_directory
from utils.test_utils import export_results, load_tests, run_tests, open_report, open_log
from widgets.title_bar import TitleBar
import xml.etree.ElementTree as ET

class RobotTestRunner(QWidget):
    windowStateChanged = pyqtSignal(object)  # Add this line

    def __init__(self):
        super().__init__()
        # Get the version 
        tree = ET.parse('config.xml')
        root = tree.getroot()
        version = root[0].text
        

        self.version_label = f"© Robot Runner {version}"
        self.test_directory = ""
        self.output_directory = ""
        self.init_ui()
        self.show_splash()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(1100, 650)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Add title bar
        self.title_bar = TitleBar("Robot Framework Test Runner", self)
        self.main_layout.addLayout(self.title_bar)
        
        # Initialize UI components
        self.init_directory_controls()
        self.init_test_selection()
        self.init_parameters()
        self.init_results_controls()
        self.init_version_label()
        
        # Apply styles
        apply_styles(self)

    def show_splash(self):
        self.splash = LogoSplash(self)  # No need to call show() here as it's done in __init__

    def init_directory_controls(self):
        self.label = QLabel("Select a folder containing .robot files")
        self.main_layout.addWidget(self.label)
        
        self.selectButton = QPushButton("Select Folder")
        self.selectButton.clicked.connect(lambda: select_directory(self))
        self.main_layout.addWidget(self.selectButton)

    def init_test_selection(self):
        # Horizontal layout for select all and refresh
        self.layout_horizontal = QHBoxLayout()

        # Select all checkbox
        self.selectAllCheckBox = QCheckBox("Select all tests")
        self.selectAllCheckBox.stateChanged.connect(self.toggle_select_all_tests)
        self.layout_horizontal.addWidget(self.selectAllCheckBox)

        # Refresh button with loading indicator
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
        self.main_layout.addLayout(self.layout_horizontal)

        # Test list
        self.testList = QListWidget()
        self.main_layout.addWidget(self.testList)

    def init_parameters(self):
        paramLayout = QHBoxLayout()
        self.processLabel = QLabel("Number of subprocesses :")
        self.processInput = QSpinBox()
        self.processInput.setValue(2)
        self.processInput.setFixedWidth(50)
        self.processInput.setMinimum(1)
        self.processInput.setMaximum(50)
        paramLayout.addWidget(self.processLabel)
        paramLayout.addWidget(self.processInput)
        self.main_layout.addLayout(paramLayout)

    def init_results_controls(self):
        # File selection
        self.fileLabel = QLabel("Select result storage location :")
        self.main_layout.addWidget(self.fileLabel)
        
        fileLayout = QHBoxLayout()
        self.fileButton = QPushButton("Choose folder")
        self.fileButton.clicked.connect(lambda: select_output_directory(self))
        fileLayout.addWidget(self.fileButton)

        self.clearButton = QPushButton("Clear results")
        self.clearButton.clicked.connect(lambda: clear_results_directory(self))
        fileLayout.addWidget(self.clearButton)
        self.main_layout.addLayout(fileLayout)

        # Run button
        self.runButton = QPushButton("Run selected tests")
        self.runButton.clicked.connect(lambda: run_tests(self))
        self.main_layout.addWidget(self.runButton)
        
        # Results label
        self.resultLabel = QLabel("Test Results :")
        self.main_layout.addWidget(self.resultLabel)
        
        # Report and log buttons
        reportLogLayout = QHBoxLayout()
        self.reportButton = QPushButton("Open Report")
        self.reportButton.clicked.connect(lambda: open_report(self))
        reportLogLayout.addWidget(self.reportButton)

        self.logButton = QPushButton("Open Log")
        self.logButton.clicked.connect(lambda: open_log(self))
        reportLogLayout.addWidget(self.logButton)
        self.main_layout.addLayout(reportLogLayout)
        
        self.exportResults = QPushButton("Export Results")
        self.exportResults.clicked.connect(lambda: export_results(self))
        reportLogLayout.addWidget(self.exportResults)
        self.main_layout.addLayout(reportLogLayout)


    def init_version_label(self):
        self.version_layout = QVBoxLayout()
        self.version = QLabel(f"{self.version_label}")
        self.version_layout.addWidget(self.version)
        self.main_layout.addLayout(self.version_layout)

    def toggle_select_all_tests(self, state):
        check_state = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        for i in range(self.testList.count()):
            self.testList.item(i).setCheckState(check_state)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()