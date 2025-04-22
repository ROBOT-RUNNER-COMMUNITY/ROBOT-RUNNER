import os
import xml.etree.ElementTree as ET
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

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
            
        self.is_loading = True
        stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'execution_times': [],
            'recent_test_runs': [],
            'test_details': []
        }
        
        try:
            print(f"Looking for XML files in: {os.path.abspath(self.results_dir)}")
            
            for root, _, files in os.walk(self.results_dir):
                if 'output.xml' in files:
                    xml_path = os.path.join(root, 'output.xml')
                    print(f"Processing XML file: {xml_path}")
                    
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        
                        # First try to get stats from statistics section
                        stat_node = root.find('.//statistics/total/stat[@name="All Tests"]')
                        if stat_node is not None:
                            stats['total_tests'] = int(stat_node.find('total').text)
                            stats['passed'] = int(stat_node.find('pass').text)
                            stats['failed'] = int(stat_node.find('fail').text)
                            print(f"Found statistics: Total={stats['total_tests']}, Passed={stats['passed']}, Failed={stats['failed']}")
                        
                        # Parse all test cases for detailed info
                        for test in root.findall('.//test'):
                            test_name = test.get('name', 'Unnamed Test')
                            test_status = test.find('status')
                            
                            if test_status is not None:
                                status = test_status.get('status', 'UNKNOWN')
                                
                                # Count individual tests if statistics weren't found
                                if stat_node is None:
                                    stats['total_tests'] += 1
                                    if status == 'PASS':
                                        stats['passed'] += 1
                                    else:
                                        stats['failed'] += 1
                                
                                # Record test execution details
                                try:
                                    start = datetime.strptime(
                                        test_status.get('starttime'), 
                                        "%Y%m%d %H:%M:%S.%f"
                                    )
                                    end = datetime.strptime(
                                        test_status.get('endtime'), 
                                        "%Y%m%d %H:%M:%S.%f"
                                    )
                                    duration = (end - start).total_seconds()
                                    
                                    stats['recent_test_runs'].append({
                                        'name': test_name,
                                        'timestamp': start,
                                        'status': status,
                                        'duration': duration
                                    })
                                    stats['execution_times'].append(duration)
                                    
                                    stats['test_details'].append({
                                        'name': test_name,
                                        'status': status,
                                        'start': test_status.get('starttime'),
                                        'end': test_status.get('endtime'),
                                        'duration': duration,
                                        'message': test_status.text.strip() if test_status.text else ""
                                    })
                                    
                                except ValueError as e:
                                    print(f"Error parsing timestamps for test {test_name}: {e}")
                                    continue
                                
                    except ET.ParseError as e:
                        print(f"Error parsing XML {xml_path}: {e}")
                        continue
            
            # Sort recent tests by timestamp (newest first)
            stats['recent_test_runs'].sort(key=lambda x: x['timestamp'], reverse=True)
            
            print(f"Final stats - Tests: {stats['total_tests']}, Passed: {stats['passed']}, Failed: {stats['failed']}")
            print(f"Recent test runs: {len(stats['recent_test_runs'])}")
            
            self.data_loaded.emit(stats)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.data_loaded.emit({})
        finally:
            self.is_loading = False