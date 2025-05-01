import os
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

class DashboardDataLoader(QObject):
    data_loaded = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.results_dir = "tests-for-validation/Results"
        
    def load_data(self):
        try:
            stats = {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'execution_times': [],
                'recent_runs': []
            }
            
            if os.path.exists(self.results_dir):
                for root, _, files in os.walk(self.results_dir):
                    if 'output.xml' in files:
                        xml_path = os.path.join(root, 'output.xml')
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        
                        for stat in root.findall('.//statistics/total/stat'):
                            if stat.get('name') == 'All Tests':
                                stats['total_tests'] += int(stat.find('total').text)
                                stats['passed'] += int(stat.find('pass').text)
                                stats['failed'] += int(stat.find('fail').text)
                                
                        for suite in root.findall('.//suite'):
                            status = suite.find('.//status')
                            if status is not None:

                                timestamp_str = status.get('starttime')
                                try:
                                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d %H:%M:%S.%f")
                                except ValueError:
                                
                                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d %H:%M:%S")
                                
                                stats['recent_runs'].append({
                                    'suite': suite.get('name'),
                                    'timestamp': timestamp,
                                    'status': 'PASS' if status.get('status') == 'PASS' else 'FAIL'
                                })
                                
                            
                                endtime_str = status.get('endtime')
                                try:
                                    endtime = datetime.strptime(endtime_str, "%Y%m%d %H:%M:%S.%f")
                                except ValueError:
                                    endtime = datetime.strptime(endtime_str, "%Y%m%d %H:%M:%S")
                                    
                                stats['execution_times'].append((endtime - timestamp).total_seconds())
                            
                        stats['execution_times'].append(float(root.find('.//suite/status').get('endtime')) - 
                                                      float(root.find('.//suite/status').get('starttime')))
            
            if stats['recent_runs']:
                stats['recent_runs'].sort(key=lambda x: x['timestamp'], reverse=True)
                
            self.data_loaded.emit(stats)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.data_loaded.emit({})