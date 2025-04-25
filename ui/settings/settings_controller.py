import json
import os
from PyQt6.QtCore import QObject

class SettingsController(QObject):
    def __init__(self, settings_widget):
        super().__init__()
        self.settings_widget = settings_widget
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        
        # Connect signals
        self.settings_widget.settings_changed.connect(self.save_settings)
        
        # Initialize widget with loaded settings
        self.settings_widget.set_settings(self.settings)
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.default_settings()
        return self.default_settings()
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def default_settings(self):
        """Return default settings"""
        return {
            "theme": "Light",
            "default_processes": 2,
            "auto_refresh": True,
            "default_test_dir": "",
            "default_output_dir": ""
        }
    
    def get_setting(self, key):
        """Get specific setting value"""
        return self.settings.get(key, self.default_settings().get(key))
    
    def get_settings(self):
        """Get all settings"""
        return self.settings