import os
import subprocess
import platform
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import numpy as np
from collections import defaultdict
import logging
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.dates as mdates

class AnalyticsController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self._setup_chart_styles()
        self._connect_signals()
        logging.basicConfig(level=logging.DEBUG)
        
    def _setup_chart_styles(self):
        """Configure consistent styling for all charts"""
        rcParams.update({
            'figure.facecolor': '#ffffff',
            'axes.facecolor': '#f8f9fa',
            'axes.edgecolor': '#dddddd',
            'axes.labelcolor': '#555555',
            'text.color': '#333333',
            'xtick.color': '#777777',
            'ytick.color': '#777777',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.linestyle': '--',
            'font.size': 9,
            'axes.titlesize': 11,
            'axes.labelsize': 10
        })

    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(lambda: self.data_loader.load_data(force=True))
        self.widget.export_button.clicked.connect(self.export_to_excel)
        self.data_loader.data_loaded.connect(self.update_analytics)
        
    def update_analytics(self, data):
        try:
            logging.debug(f"Data received - keys: {data.keys()}")
            if not data or not isinstance(data, dict):
                logging.warning("Empty or invalid data received")
                self._show_empty_state()
                return
                
            self._update_execution_trends(data)
            self._update_test_status_distribution(data)
            self._update_failure_analysis(data)
            self._update_execution_time_analysis(data)
            
        except Exception as e:
            logging.error(f"Error updating analytics: {str(e)}", exc_info=True)
            self._show_empty_state()

    def _update_execution_trends(self, data):
        ax = self.widget.trends_ax
        ax.clear()
        
        recent_runs = data.get('recent_test_runs', [])
        if not recent_runs:
            self._show_empty_chart(ax, "No execution data available")
            self.widget.trends_canvas.draw()
            return
        
        date_data = defaultdict(lambda: {'passed': 0, 'failed': 0})
        
        for run in recent_runs:
            try:
                if isinstance(run['timestamp'], str):
                    date = datetime.strptime(run['timestamp'], "%Y%m%d %H:%M:%S.%f").date()
                else:
                    date = run['timestamp'].date()
                
                status = run.get('status', '').upper()
                
                if status == 'PASS':
                    date_data[date]['passed'] += 1
                elif status == 'FAIL':
                    date_data[date]['failed'] += 1
                    
            except Exception as e:
                logging.warning(f"Error processing run data: {str(e)}")
                continue
        
        if not date_data:
            self._show_empty_chart(ax, "Insufficient valid data")
            self.widget.trends_canvas.draw()
            return
        
        dates = sorted(date_data.keys())
        passed = [date_data[d]['passed'] for d in dates]
        failed = [date_data[d]['failed'] for d in dates]
        
        try:
            ax.stackplot(mdates.date2num(dates), passed, failed,
                        colors=['#4CAF50', '#F44336'],
                        alpha=0.7,
                        labels=['Passed', 'Failed'])
            
            ax.set_title('Test Execution Trends', pad=15, fontweight='bold')
            ax.set_ylabel('Number of Tests')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//5)))
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(loc='upper left')
            ax.grid(True, linestyle='--', alpha=0.3)
            
        except Exception as e:
            logging.error(f"Error drawing trends: {str(e)}")
            self._show_empty_chart(ax, "Error displaying trends")
        
        self.widget.trends_fig.tight_layout()
        self.widget.trends_canvas.draw()

    def _update_test_status_distribution(self, data):
        ax = self.widget.status_ax
        ax.clear()
        
        total = data.get('total_tests', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        other = max(0, total - passed - failed)
        
        if total == 0:
            self._show_empty_chart(ax, "No test data available")
            self.widget.status_canvas.draw()
            return
            
        try:
            sizes = [passed, failed, other]
            labels = [f'Passed ({passed})', f'Failed ({failed})', f'Other ({other})']
            colors = ['#2ecc71', '#e74c3c', '#f39c12']
            explode = (0.05, 0.05, 0)
            
            wedges, _, _ = ax.pie(
                sizes, explode=explode, labels=labels, colors=colors,
                autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                startangle=90, pctdistance=0.85,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1},
                textprops={'fontsize': 8}
            )
            
            ax.set_title('Test Status Distribution', pad=15, fontweight='bold')
            ax.axis('equal')
            
        except Exception as e:
            logging.error(f"Error drawing status chart: {str(e)}")
            self._show_empty_chart(ax, "Error displaying status")
        
        self.widget.status_fig.tight_layout()
        self.widget.status_canvas.draw()

    def _update_failure_analysis(self, data):
        ax = self.widget.failure_ax
        ax.clear()
        
        test_details = data.get('test_details', [])
        if not test_details:
            self._show_empty_chart(ax, "No test details available")
            self.widget.failure_canvas.draw()
            return
            
        failure_messages = defaultdict(int)
        for test in test_details:
            if not isinstance(test, dict):
                continue
                
            if test.get('status', '').upper() == 'FAIL' and test.get('message'):
                message = str(test['message']).split('\n')[0].strip()
                if message:
                    failure_messages[message] += 1
        
        if not failure_messages:
            self._show_empty_chart(ax, "No failures with messages")
            self.widget.failure_canvas.draw()
            return
            
        sorted_failures = sorted(failure_messages.items(), key=lambda x: x[1], reverse=True)[:5]
        reasons = [x[0][:50] + ('...' if len(x[0]) > 50 else '') for x in sorted_failures]
        counts = [x[1] for x in sorted_failures]
        
        try:
            y_pos = np.arange(len(reasons))
            bars = ax.barh(y_pos, counts, color='#e74c3c', height=0.6, alpha=0.7)
            
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}', ha='left', va='center', color='#333333', fontsize=8)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(reasons, fontsize=8)
            ax.set_xlabel('Occurrences', labelpad=5)
            ax.set_title('Top Failure Reasons', pad=15, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logging.error(f"Error drawing failure analysis: {str(e)}")
            self._show_empty_chart(ax, "Error displaying failures")
        
        self.widget.failure_fig.tight_layout()
        self.widget.failure_canvas.draw()

    def _update_execution_time_analysis(self, data):
        ax = self.widget.time_ax
        ax.clear()
        
        execution_times = data.get('execution_times', [])
        if not execution_times:
            self._show_empty_chart(ax, "No execution time data")
            self.widget.time_canvas.draw()
            return
            
        try:
            times = [float(t) for t in execution_times if isinstance(t, (int, float)) or str(t).replace('.', '').isdigit()]
            if not times:
                self._show_empty_chart(ax, "No valid time data")
                self.widget.time_canvas.draw()
                return
                
            times = np.array(times)
            q75, q25 = np.percentile(times, [75, 25])
            iqr = q75 - q25
            upper_bound = q75 + (1.5 * iqr)
            filtered_times = times[times <= upper_bound]
            
            bin_count = min(15, len(filtered_times))
            if bin_count < 1:
                self._show_empty_chart(ax, "Not enough data points")
                self.widget.time_canvas.draw()
                return
                
            ax.hist(
                filtered_times, 
                bins=bin_count,
                color='#3498db', 
                alpha=0.7,
                edgecolor='white'
            )
            
            ax.set_title('Test Execution Time Distribution', pad=15, fontweight='bold')
            ax.set_xlabel('Execution Time (seconds)')
            ax.set_ylabel('Number of Tests')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logging.error(f"Error drawing time distribution: {str(e)}")
            self._show_empty_chart(ax, "Error displaying times")
        
        self.widget.time_fig.tight_layout()
        self.widget.time_canvas.draw()

    def export_to_excel(self):
        """Export analytics data to Excel with proper charts and formatting"""
        try:
            # Vérification des prérequis
            if not self.data_loader.results_dir:
                QMessageBox.warning(self.widget, "Export Error", "No results directory configured")
                return

            # Préparation du chemin d'export
            reports_dir = os.path.join(self.data_loader.results_dir, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(reports_dir, f"RobotAnalyticsReport_{timestamp}.xlsx")

            # Vérification du fichier source
            output_xml = os.path.join(self.data_loader.results_dir, "output.xml")
            if not os.path.exists(output_xml):
                QMessageBox.warning(self.widget, "Export Error", "output.xml not found")
                return

            # Extraction des données
            test_data = []
            tree = ET.parse(output_xml)
            root = tree.getroot()

            for test in root.findall('.//test'):
                # ... (code d'extraction existant) ...
                pass

            if not test_data:
                QMessageBox.warning(self.widget, "Export Error", "No test data to export")
                return

            # Création du DataFrame
            df = pd.DataFrame(test_data)

            # Création du fichier Excel avec mise en forme
            with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
                # 1. Feuille des résultats bruts
                df.to_excel(writer, sheet_name='Test Results', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Test Results']
                
                # Formatage conditionnel pour les statuts
                format_pass = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
                format_fail = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                format_other = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'})
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'PASS',
                    'format': format_pass
                })
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'FAIL',
                    'format': format_fail
                })
                
                worksheet.conditional_format(1, 2, len(df), 2, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'UNKNOWN',
                    'format': format_other
                })

                # 2. Feuille des graphiques analytiques
                charts_sheet = workbook.add_worksheet('Analytics Charts')
                charts_sheet.set_tab_color('#4F81BD')  # Bleu pour identification
                
                # Ajout des graphiques principaux
                self._add_excel_charts(workbook, df, charts_sheet)
                
                # Ajustement des colonnes
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, max(len(col), *df[col].astype(str).map(len).max()) + 2)

            # Ouverture du fichier
            self._open_file(export_path)
            QMessageBox.information(self.widget, "Export Successful", 
                                f"Report exported to:\n{export_path}")

        except Exception as e:
            QMessageBox.critical(self.widget, "Export Error", 
                            f"Failed to export report:\n{str(e)}")

    def _add_excel_charts(self, workbook, df, sheet):
        """Add all analytics charts to Excel sheet"""
        try:
            # 1. Graphique des tendances d'exécution
            dates = pd.to_datetime(df['Timestamp']).dt.date
            status_counts = df.groupby([dates, 'Status']).size().unstack(fill_value=0)
            
            line_chart = workbook.add_chart({'type': 'line'})
            for i, status in enumerate(['PASS', 'FAIL']):
                if status in status_counts.columns:
                    line_chart.add_series({
                        'name': status,
                        'categories': ['Test Results', 1, 0, len(df), 0],
                        'values': ['Test Results', 1, 2+i, len(df), 2+i],
                        'line': {'color': '#4CAF50' if status == 'PASS' else '#F44336'}
                    })
            line_chart.set_title({'name': 'Test Execution Trends'})
            line_chart.set_x_axis({'name': 'Date'})
            line_chart.set_y_axis({'name': 'Count'})
            sheet.insert_chart('B2', line_chart)

            # 2. Camembert des statuts
            pie_chart = workbook.add_chart({'type': 'pie'})
            status_summary = df['Status'].value_counts()
            pie_chart.add_series({
                'name': 'Status Distribution',
                'categories': ['Test Results', 1, 2, len(status_summary), 2],
                'values': ['Test Results', 1, 2, len(status_summary), 2],
                'data_labels': {'percentage': True, 'category': True}
            })
            pie_chart.set_title({'name': 'Test Status Distribution'})
            sheet.insert_chart('B20', pie_chart)

            # 3. Histogramme des temps d'exécution
            hist_chart = workbook.add_chart({'type': 'column'})
            hist_chart.add_series({
                'name': 'Execution Time',
                'values': ['Test Results', 1, 3, len(df), 3],
                'categories': ['Test Results', 1, 0, len(df), 0],
                'fill': {'color': '#3498db'}
            })
            hist_chart.set_title({'name': 'Execution Time Distribution'})
            sheet.insert_chart('B38', hist_chart)

        except Exception as e:
            logging.error(f"Error adding Excel charts: {str(e)}")

    def _parse_test_data(self, xml_path):
        """Robust XML parser with comprehensive error handling"""
        test_data = []
        
        try:
            for event, elem in ET.iterparse(xml_path, events=('end',)):
                if elem.tag == 'test':
                    try:
                        test_name = elem.get('name', 'Unnamed Test')
                        status = elem.find('status')
                        
                        if status is None:
                            logging.warning(f"Test '{test_name}' has no status element")
                            continue
                            
                        start_str = status.get('starttime', '')
                        end_str = status.get('endtime', '')
                        
                        if not start_str or not end_str:
                            logging.warning(f"Test '{test_name}' has incomplete timing data")
                            continue
                            
                        try:
                            start = datetime.strptime(start_str, "%Y%m%d %H:%M:%S.%f")
                            end = datetime.strptime(end_str, "%Y%m%d %H:%M:%S.%f")
                            duration = (end - start).total_seconds()
                            
                            test_data.append({
                                'Test Name': test_name,
                                'Timestamp': start,
                                'Status': status.get('status', 'UNKNOWN').upper(),
                                'Duration (s)': duration,
                                'Message': status.text.strip() if status.text else ""
                            })
                            
                        except ValueError as e:
                            logging.warning(f"Invalid timestamp format in test '{test_name}': {str(e)}")
                            continue
                            
                    except Exception as e:
                        logging.error(f"Error parsing test case: {str(e)}")
                    finally:
                        elem.clear()
                        
        except ET.ParseError as e:
            logging.error(f"XML parsing error: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error reading XML file: {str(e)}")
            return None
            
        return test_data if test_data else None

    def _add_analytics_sheets(self, workbook, df):
        """Add analytics summary sheets to Excel"""
        try:
            # Status Summary
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            status_counts.to_excel(workbook, sheet_name='Status Summary', index=False)
            
            # Failure Analysis
            if 'FAIL' in df['Status'].values:
                failures = df[df['Status'] == 'FAIL']
                failure_counts = failures['Message'].value_counts().head(5).reset_index()
                failure_counts.columns = ['Failure Reason', 'Count']
                failure_counts.to_excel(workbook, sheet_name='Failure Analysis', index=False)
            
            # Time Analysis
            time_stats = df['Duration (s)'].describe().reset_index()
            time_stats.columns = ['Metric', 'Value']
            time_stats.to_excel(workbook, sheet_name='Time Stats', index=False)
            
            # Add charts
            self._add_excel_charts(workbook, df)
            
        except Exception as e:
            logging.error(f"Error adding analytics sheets: {str(e)}")

    def _add_excel_charts(self, workbook, df):
        """Add charts to Excel workbook"""
        try:
            # Status Pie Chart
            status_sheet = workbook.sheets['Status Summary']
            pie_chart = workbook.add_chart({'type': 'pie'})
            pie_chart.add_series({
                'name': 'Status Distribution',
                'categories': ['Status Summary', 1, 0, len(df['Status'].unique()), 0],
                'values': ['Status Summary', 1, 1, len(df['Status'].unique()), 1],
                'data_labels': {'percentage': True, 'category': True}
            })
            pie_chart.set_title({'name': 'Test Status Distribution'})
            status_sheet.insert_chart('D2', pie_chart)
            
            # Failure Bar Chart (if failures exist)
            if 'FAIL' in df['Status'].values:
                failure_sheet = workbook.sheets['Failure Analysis']
                bar_chart = workbook.add_chart({'type': 'bar'})
                bar_chart.add_series({
                    'name': 'Failures',
                    'categories': ['Failure Analysis', 1, 0, min(5, len(df[df['Status'] == 'FAIL'])), 0],
                    'values': ['Failure Analysis', 1, 1, min(5, len(df[df['Status'] == 'FAIL'])), 1],
                    'fill': {'color': '#FF0000'}
                })
                bar_chart.set_title({'name': 'Top Failure Reasons'})
                failure_sheet.insert_chart('D2', bar_chart)
            
            # Time Histogram
            time_sheet = workbook.sheets['Time Stats']
            hist_chart = workbook.add_chart({'type': 'column'})
            hist_chart.add_series({
                'name': 'Execution Times',
                'categories': ['Test Results', 1, 0, len(df), 0],
                'values': ['Test Results', 1, 3, len(df), 3],
                'fill': {'color': '#3498db'}
            })
            hist_chart.set_title({'name': 'Test Execution Times'})
            time_sheet.insert_chart('D10', hist_chart)
            
        except Exception as e:
            logging.error(f"Error adding Excel charts: {str(e)}")

    def _is_file_open(self, filepath):
        """Check if file is already open (Windows only)"""
        if platform.system() != 'Windows':
            return False
            
        try:
            fd = os.open(filepath, os.O_WRONLY|os.O_CREAT|os.O_EXCL)
            os.close(fd)
            os.unlink(filepath)
            return False
        except OSError:
            return True

    def _open_file(self, filepath):
        """Open file with default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath], check=True)
            else:
                subprocess.run(['xdg-open', filepath], check=True)
        except Exception as e:
            logging.error(f"Error opening file: {str(e)}")
            QMessageBox.information(self.widget, "Report Ready",
                                  f"Report saved to:\n{filepath}\n\nPlease open it manually.")

    def _show_empty_state(self):
        """Show empty state for all charts"""
        for ax in [self.widget.trends_ax, self.widget.status_ax, 
                  self.widget.failure_ax, self.widget.time_ax]:
            self._show_empty_chart(ax, "No data available")
        
        self.widget.trends_canvas.draw()
        self.widget.status_canvas.draw()
        self.widget.failure_canvas.draw()
        self.widget.time_canvas.draw()

    def _show_empty_chart(self, ax, message):
        """Display empty chart message"""
        ax.clear()
        ax.text(0.5, 0.5, message, 
               ha='center', va='center', 
               transform=ax.transAxes,
               color='#777777', fontsize=10)
        ax.set_title('')
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)