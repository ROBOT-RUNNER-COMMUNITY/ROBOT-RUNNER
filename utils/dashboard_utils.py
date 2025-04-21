import os
import json
from datetime import datetime
from collections import defaultdict
from PyQt6.QtCore import QObject, pyqtSignal
import xml.etree.ElementTree as ET

class DashboardDataLoader(QObject):
    data_loaded = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.results_dir = "tests-for-validation/Results"
        self.history_file = "history.json"
        
    def load_dashboard_data(self):
        """Load all data needed for dashboard"""
        try:
            data = {
                'recent_runs': self._load_recent_runs(),
                'statistics': self._calculate_statistics(),
                'failure_analysis': self._analyze_failures()
            }
            self.data_loaded.emit(data)
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            # Return empty data on error
            self.data_loaded.emit({
                'recent_runs': [],
                'statistics': self._get_default_stats(),
                'failure_analysis': {}
            })
    
    def _load_recent_runs(self):
        """Load last 5 test runs from history"""
        if not os.path.exists(self.history_file):
            return []
            
        try:
            with open(self.history_file) as f:
                history = json.load(f)
                return history[-5:]  # Return last 5 runs
        except:
            return []
    
    def _get_default_stats(self):
        """Return default statistics when no data is available"""
        return {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'success_rate': 0
        }
    
    def _calculate_statistics(self):
        """Calculate test statistics from output.xml"""
        stats = self._get_default_stats()
        output_file = os.path.join(self.results_dir, "output.xml")
        
        if not os.path.exists(output_file):
            return stats
            
        try:
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            # Safely get attributes with defaults
            total = root.get('total', '0')
            passed = root.get('passed', '0')
            failed = root.get('failed', '0')
            
            stats['total'] = int(total) if total.isdigit() else 0
            stats['passed'] = int(passed) if passed.isdigit() else 0
            stats['failed'] = int(failed) if failed.isdigit() else 0
            
            if stats['total'] > 0:
                stats['success_rate'] = round((stats['passed'] / stats['total']) * 100, 2)
                
            return stats
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return self._get_default_stats()
    
    def _analyze_failures(self):
        """Analyze failure patterns from output.xml"""
        failures = defaultdict(int)
        output_file = os.path.join(self.results_dir, "output.xml")
        
        if not os.path.exists(output_file):
            return dict(failures)
            
        try:
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            for test in root.findall(".//test"):
                if test.get('status') == 'FAIL':
                    msg_element = test.find(".//msg")
                    if msg_element is not None and msg_element.text:
                        failure_msg = msg_element.text.split('\n')[0]
                        failures[failure_msg] += 1
                        
            return dict(failures)
        except Exception as e:
            print(f"Error analyzing failures: {e}")
            return {}