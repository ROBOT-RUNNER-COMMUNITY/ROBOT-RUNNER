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
                self.data_loaded.emit(stats)
                return
                
            output_xml = os.path.join(self.results_dir, "output.xml")
            if not os.path.exists(output_xml):
                self.data_loaded.emit(stats)
                return
                
            if os.path.getsize(output_xml) == 0:
                self.data_loaded.emit(stats)
                return
                
            tree = ET.parse(output_xml)
            root = tree.getroot()
            
            # METHOD 1: Get statistics from statistics section
            stat_node = root.find('.//statistics/total/stat[@name="All Tests"]')
            if stat_node is not None:
                stats['total_tests'] = int(stat_node.find('total').text)
                stats['passed'] = int(stat_node.find('pass').text)
                stats['failed'] = int(stat_node.find('fail').text)
            
            # METHOD 2: Count individual tests if statistics not found
            if stats['total_tests'] == 0:
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
            test_runs = {}
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
                        
                        # Store only the most recent run for each test
                        if test_name not in test_runs or start > test_runs[test_name]['timestamp']:
                            test_runs[test_name] = {
                                'name': test_name,
                                'timestamp': start,
                                'status': test_status.get('status', 'UNKNOWN'),
                                'duration': duration
                            }
                            
                        stats['execution_times'].append(duration)
                        stats['test_details'].append({
                            'name': test_name,
                            'status': test_status.get('status', 'UNKNOWN'),
                            'duration': duration,
                            'message': test_status.text.strip() if test_status.text else ""
                        })
                        
                    except ValueError as e:
                        continue
            
            # Convert to list and sort by most recent
            stats['recent_test_runs'] = sorted(
                test_runs.values(),
                key=lambda x: x['timestamp'],
                reverse=True
            )[:10]  # Limit to 10 most recent
            
            self.data_loaded.emit(stats)
            
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            self.data_loaded.emit(stats)
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.data_loaded.emit(stats)
        finally:
            self.is_loading = False