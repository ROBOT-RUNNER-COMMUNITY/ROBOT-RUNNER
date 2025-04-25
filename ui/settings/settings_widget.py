from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QCheckBox, QSpinBox, QLineEdit, 
                            QPushButton, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal

class SettingsWidget(QWidget):
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        
        # Appearance Section
        appearance_label = QLabel("Appearance")
        appearance_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(appearance_label)
        
        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Test Execution Section
        tests_label = QLabel("Test Execution")
        tests_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(tests_label)
        
        # Default Processes
        process_layout = QHBoxLayout()
        process_label = QLabel("Default processes:")
        self.process_spin = QSpinBox()
        self.process_spin.setRange(1, 16)
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_spin)
        layout.addLayout(process_layout)
        
        # Auto-refresh
        self.auto_refresh_check = QCheckBox("Auto-refresh after test execution")
        layout.addWidget(self.auto_refresh_check)
        
        # Paths Section
        paths_label = QLabel("Paths")
        paths_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(paths_label)
        
        # Test Directory
        test_dir_layout = QHBoxLayout()
        test_dir_label = QLabel("Test directory:")
        self.test_dir_input = QLineEdit()
        self.test_dir_input.setPlaceholderText("Select default test directory")
        test_dir_button = QPushButton("Browse...")
        test_dir_button.clicked.connect(lambda: self.browse_directory(self.test_dir_input))
        test_dir_layout.addWidget(test_dir_label)
        test_dir_layout.addWidget(self.test_dir_input)
        test_dir_layout.addWidget(test_dir_button)
        layout.addLayout(test_dir_layout)
        
        # Output Directory
        output_dir_layout = QHBoxLayout()
        output_dir_label = QLabel("Output directory:")
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Select default output directory")
        output_dir_button = QPushButton("Browse...")
        output_dir_button.clicked.connect(lambda: self.browse_directory(self.output_dir_input))
        output_dir_layout.addWidget(output_dir_label)
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(output_dir_button)
        layout.addLayout(output_dir_layout)
        
        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.emit_settings)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
    
    def browse_directory(self, line_edit):
        """Open directory dialog and set path to line edit"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            line_edit.setText(dir_path)
    
    def get_settings(self):
        """Return current settings as dict"""
        return {
            "theme": self.theme_combo.currentText(),
            "default_processes": self.process_spin.value(),
            "auto_refresh": self.auto_refresh_check.isChecked(),
            "default_test_dir": self.test_dir_input.text(),
            "default_output_dir": self.output_dir_input.text()
        }
        
    def set_settings(self, settings):
        """Set widget values from settings dict"""
        self.theme_combo.setCurrentText(settings.get("theme", "Light"))
        self.process_spin.setValue(settings.get("default_processes", 2))
        self.auto_refresh_check.setChecked(settings.get("auto_refresh", True))
        self.test_dir_input.setText(settings.get("default_test_dir", ""))
        self.output_dir_input.setText(settings.get("default_output_dir", ""))
    
    def emit_settings(self):
        """Emit current settings"""
        self.settings_changed.emit(self.get_settings())