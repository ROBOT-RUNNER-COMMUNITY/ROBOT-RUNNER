# ui/dashboard/dashboard_loader.py
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
            if not os.path.exists(self.results_dir):
                print(f"Results directory not found: {self.results_dir}")
                self.data_loaded.emit(stats)
                return
                
            xml_found = False
            for root, _, files in os.walk(self.results_dir):
                if 'output.xml' in files:
                    xml_path = os.path.join(root, 'output.xml')
                    print(f"Processing XML file: {xml_path}")
                    
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        xml_found = True
                        
                        # METHOD 1: Get statistics from statistics section
                        stat_node = root.find('.//statistics/total/stat[@name="All Tests"]')
                        if stat_node is not None:
                            stats['total_tests'] = int(stat_node.find('total').text)
                            stats['passed'] = int(stat_node.find('pass').text)
                            stats['failed'] = int(stat_node.find('fail').text)
                            print(f"Found statistics node: Total={stats['total_tests']}, Passed={stats['passed']}, Failed={stats['failed']}")
                        
                        # METHOD 2: Count individual tests if statistics not found
                        if stats['total_tests'] == 0:
                            print("Falling back to counting individual tests")
                            pass_count = 0
                            fail_count = 0
                            for test in root.findall('.//test'):
                                status = test.find('status').get('status', 'UNKNOWN')
                                if status == 'PASS':
                                    pass_count += 1
                                elif status == 'FAIL':
                                    fail_count += 1
                            stats['total_tests'] = pass_count + fail_count
                            stats['passed'] = pass_count
                            stats['failed'] = fail_count
                        
                        # Get individual test details
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
                                    
                                    stats['recent_test_runs'].append({
                                        'name': test_name,
                                        'timestamp': start,
                                        'status': test_status.get('status', 'UNKNOWN'),
                                        'duration': duration
                                    })
                                    stats['execution_times'].append(duration)
                                    
                                    stats['test_details'].append({
                                        'name': test_name,
                                        'status': test_status.get('status', 'UNKNOWN'),
                                        'duration': duration,
                                        'message': test_status.text.strip() if test_status.text else ""
                                    })
                                    
                                except ValueError as e:
                                    print(f"Error parsing test timestamps: {e}")
                                    continue
                                    
                    except ET.ParseError as e:
                        print(f"Error parsing XML {xml_path}: {e}")
                        continue
            
            if not xml_found:
                print("No output.xml file found in results directory")
            
            # Sort by most recent first and ensure we have unique test names
            unique_runs = {}
            for run in sorted(stats['recent_test_runs'], key=lambda x: x['timestamp'], reverse=True):
                if run['name'] not in unique_runs:
                    unique_runs[run['name']] = run
            
            stats['recent_test_runs'] = list(unique_runs.values())[:10]  # Get top 10 unique runs
            
            print(f"Final stats - Tests: {stats['total_tests']}, Passed: {stats['passed']}, Failed: {stats['failed']}")
            print(f"Recent test runs: {len(stats['recent_test_runs'])}")
            
            self.data_loaded.emit(stats)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.data_loaded.emit(stats)
        finally:
            self.is_loading = False