from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from collections import defaultdict
import logging

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
        
        # Debug: Vérifier les données reçues
        print("Données reçues pour les tendances:", data.get('recent_test_runs', [])[:2])
        
        recent_runs = data.get('recent_test_runs', [])
        if not recent_runs:
            print("Aucune exécution récente trouvée")
            self._show_empty_chart(ax, "Aucune donnée d'exécution disponible")
            self.widget.trends_canvas.draw()
            return
        
        # Préparer les données
        date_data = {}
        for run in recent_runs:
            try:
                # Vérifier que le run contient bien les données nécessaires
                if not all(key in run for key in ['timestamp', 'status']):
                    print("Données de run incomplètes:", run)
                    continue
                    
                # Convertir le timestamp si nécessaire
                if isinstance(run['timestamp'], str):
                    date = datetime.strptime(run['timestamp'], "%Y%m%d %H:%M:%S.%f").date()
                else:
                    date = run['timestamp'].date()
                
                status = run['status'].upper()
                
                # Initialiser les compteurs pour cette date si nécessaire
                if date not in date_data:
                    date_data[date] = {'passed': 0, 'failed': 0, 'total': 0}
                
                # Mettre à jour les compteurs
                date_data[date]['total'] += 1
                if status == 'PASS':
                    date_data[date]['passed'] += 1
                elif status == 'FAIL':
                    date_data[date]['failed'] += 1
                    
            except Exception as e:
                print(f"Erreur de traitement des données: {e}")
                continue
        
        if not date_data:
            print("Aucune donnée valide après traitement")
            self._show_empty_chart(ax, "Données insuffisantes")
            self.widget.trends_canvas.draw()
            return
        
        # Trier les dates
        dates = sorted(date_data.keys())
        passed = [date_data[d]['passed'] for d in dates]
        failed = [date_data[d]['failed'] for d in dates]
        
        # Créer le graphique
        try:
            # Convertir les dates pour matplotlib
            mpl_dates = mdates.date2num(dates)
            
            # Créer un graphique empilé
            ax.stackplot(mpl_dates, passed, failed,
                        colors=['#4CAF50', '#F44336'],  # Vert et rouge
                        alpha=0.7,
                        labels=['Réussis', 'Échoués'])
            
            # Configuration du graphique
            ax.set_title('Tendance des Exécutions de Tests', pad=15, fontweight='bold')
            ax.set_ylabel('Nombre de Tests')
            
            # Formater l'axe des dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//5)))
            
            # Rotation des labels de date
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Ajouter une légende
            ax.legend(loc='upper left')
            
            # Ajouter une grille
            ax.grid(True, linestyle='--', alpha=0.3)
            
        except Exception as e:
            print(f"Erreur de création du graphique: {e}")
            self._show_empty_chart(ax, "Erreur d'affichage")
        
        # Dessiner le canvas
        self.widget.trends_fig.tight_layout()
        self.widget.trends_canvas.draw()

    def _update_test_status_distribution(self, data):
        """Pie chart showing test status distribution"""
        ax = self.widget.status_ax
        ax.clear()
        
        total = data.get('total_tests', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        
        if total == 0:
            logging.debug("No test data available for status distribution")
            self._show_empty_chart(ax, "No test data available")
            self.widget.status_canvas.draw()
            return
            
        try:
            # Data
            sizes = [passed, failed, max(0, total - passed - failed)]
            labels = ['Passed', 'Failed', 'Other']
            colors = ['#2ecc71', '#e74c3c', '#f39c12']
            explode = (0.05, 0.05, 0)
            
            # Pie chart
            wedges, texts, autotexts = ax.pie(
                sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=90, pctdistance=0.85,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1},
                textprops={'fontsize': 9}
            )
            
            # Center circle
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            # Formatting
            ax.set_title('Test Status Distribution', pad=15, fontweight='bold')
            ax.axis('equal')
            
        except Exception as e:
            logging.error(f"Error drawing status distribution: {str(e)}", exc_info=True)
            self._show_empty_chart(ax, "Error displaying status")
        
        self.widget.status_fig.tight_layout()
        self.widget.status_canvas.draw()

    def _update_failure_analysis(self, data):
        """Failure reasons analysis"""
        ax = self.widget.failure_ax
        ax.clear()
        
        test_details = data.get('test_details', [])
        if not test_details:
            logging.debug("No test details available for failure analysis")
            self._show_empty_chart(ax, "No test details available")
            self.widget.failure_canvas.draw()
            return
            
        try:
            # Extract failure messages
            failure_messages = defaultdict(int)
            for test in test_details:
                if not isinstance(test, dict):
                    continue
                    
                if test.get('status', '').upper() == 'FAIL' and test.get('message'):
                    # Extract first line of message and clean it
                    message = str(test['message']).split('\n')[0].strip()
                    if message:
                        failure_messages[message] += 1
            
            if not failure_messages:
                logging.debug("No failures with messages found")
                self._show_empty_chart(ax, "No failures with messages")
                self.widget.failure_canvas.draw()
                return
                
            # Get top failure reasons
            sorted_failures = sorted(failure_messages.items(), 
                                    key=lambda x: x[1], reverse=True)[:5]
            reasons = [x[0] for x in sorted_failures]
            counts = [x[1] for x in sorted_failures]
            
            # Truncate long reasons
            reasons = [r[:50] + '...' if len(r) > 50 else r for r in reasons]
            
            # Horizontal bar chart
            y_pos = np.arange(len(reasons))
            bars = ax.barh(y_pos, counts, color='#e74c3c', height=0.6, alpha=0.7)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}', ha='left', va='center', color='#333333')
            
            # Formatting
            ax.set_yticks(y_pos)
            ax.set_yticklabels(reasons, fontsize=8)
            ax.set_xlabel('Occurrences', labelpad=10)
            ax.set_title('Top Failure Reasons', pad=15, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logging.error(f"Error drawing failure analysis: {str(e)}", exc_info=True)
            self._show_empty_chart(ax, "Error displaying failures")
        
        self.widget.failure_fig.tight_layout()
        self.widget.failure_canvas.draw()

    def _update_execution_time_analysis(self, data):
        """Execution time distribution analysis"""
        ax = self.widget.time_ax
        ax.clear()
        
        execution_times = data.get('execution_times', [])
        if not execution_times:
            logging.debug("No execution time data available")
            self._show_empty_chart(ax, "No execution time data")
            self.widget.time_canvas.draw()
            return
            
        try:
            # Convert and filter valid times
            times = []
            for t in execution_times:
                try:
                    times.append(float(t))
                except (ValueError, TypeError):
                    continue
            
            if not times:
                logging.debug("No valid time data points")
                self._show_empty_chart(ax, "No valid time data")
                self.widget.time_canvas.draw()
                return
                
            times = np.array(times)
            
            # Filter outliers using IQR
            q75, q25 = np.percentile(times, [75, 25])
            iqr = q75 - q25
            upper_bound = q75 + (1.5 * iqr)
            filtered_times = times[times <= upper_bound]
            
            # Adjust bin count based on data
            bin_count = min(15, len(filtered_times))
            if bin_count < 1:
                logging.debug("Not enough data points for histogram")
                self._show_empty_chart(ax, "Not enough data points")
                self.widget.time_canvas.draw()
                return
                
            # Histogram with dynamic bins
            n, bins, patches = ax.hist(
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
            logging.error(f"Error drawing time distribution: {str(e)}", exc_info=True)
            self._show_empty_chart(ax, "Error displaying times")
        
        self.widget.time_fig.tight_layout()
        self.widget.time_canvas.draw()

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