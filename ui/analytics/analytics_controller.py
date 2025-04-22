from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class AnalyticsController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self._setup_chart_styles()
        self._connect_signals()
        
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
            'grid.alpha': 0.2,
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
            if not data or not isinstance(data, dict):
                self._show_empty_state()
                return
                
            self._update_time_series(data)
            self._update_failure_analysis(data)
            
        except Exception as e:
            print(f"Error updating analytics: {e}")
            self._show_empty_state()

    def _update_time_series(self, data):
        """Update the time series chart with improved styling"""
        ax = self.widget.time_series_ax
        ax.clear()
        
        recent_runs = data.get('recent_test_runs', [])
        if not recent_runs:
            self._show_empty_chart(ax, "No test runs available")
            self.widget.time_series_canvas.draw()
            return
            
        # Group by date with improved aggregation
        date_stats = {}
        for run in recent_runs:
            date = run['timestamp'].date()
            if date not in date_stats:
                date_stats[date] = {'total_time': 0, 'failures': 0, 'count': 0}
            date_stats[date]['total_time'] += run.get('duration', 0)
            date_stats[date]['failures'] += 1 if run.get('status') == 'FAIL' else 0
            date_stats[date]['count'] += 1
        
        dates = sorted(date_stats.keys())
        if len(dates) < 1:
            self._show_empty_chart(ax, "Not enough data points")
            self.widget.time_series_canvas.draw()
            return
            
        # Prepare data with smoothing
        times = [date_stats[d]['total_time']/max(1, date_stats[d]['count']) for d in dates]  # Avg time per test
        failure_rates = [date_stats[d]['failures']/max(1, date_stats[d]['count']) for d in dates]
        
        # Main plot (execution time)
        ax.plot(dates, times, '-o', color='#3498db', linewidth=2, markersize=8,
                markerfacecolor='white', markeredgewidth=1.5,
                label='Avg Execution Time (s)')
        ax.set_ylabel('Time (s)', color='#3498db')
        ax.tick_params(axis='y', labelcolor='#3498db')
        ax.set_ylim(bottom=0)  # Force zero baseline
        
        # Failure rate plot
        ax2 = ax.twinx()
        ax2.plot(dates, failure_rates, 's--', color='#e74c3c', linewidth=1.5, markersize=6,
                markerfacecolor='white', markeredgewidth=1.5,
                label='Failure Rate')
        ax2.set_ylabel('Failure Rate', color='#e74c3c')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        ax2.set_ylim(0, 1.05)  # Slight padding
        
        # Formatting
        ax.set_title('Test Execution Trends', pad=15, fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//5)))
        
        # Combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper left', framealpha=0.9)
        
        # Remove dark borders
        for spine in ax.spines.values():
            spine.set_visible(False)
        for spine in ax2.spines.values():
            spine.set_visible(False)
            
        self.widget.time_series_fig.tight_layout()
        self.widget.time_series_canvas.draw()

    def _update_failure_analysis(self, data):
        """Update the failure analysis chart"""
        ax = self.widget.failure_ax
        ax.clear()
        
        test_details = data.get('test_details', [])
        if not test_details:
            self._show_empty_chart(ax, "No test details available")
            self.widget.failure_canvas.draw()
            return
            
        # Count failures by test
        failure_counts = {}
        for test in test_details:
            if test.get('status') == 'FAIL':
                test_name = test.get('name', 'Unknown')
                failure_counts[test_name] = failure_counts.get(test_name, 0) + 1
        
        if not failure_counts:
            self._show_empty_chart(ax, "No failures recorded")
            self.widget.failure_canvas.draw()
            return
            
        # Get top 10 failing tests
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        test_names = [x[0] for x in sorted_failures]
        fail_counts = [x[1] for x in sorted_failures]
        
        # Create horizontal bar chart
        y_pos = range(len(test_names))
        bars = ax.barh(y_pos, fail_counts, color='#e74c3c', height=0.6, edgecolor='white')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{width}', ha='left', va='center', color='#333333')
        
        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels(test_names)
        ax.set_xlabel('Failure Count', labelpad=10)
        ax.set_title('Top Failing Tests', pad=15, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.2)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        self.widget.failure_fig.tight_layout()
        self.widget.failure_canvas.draw()

    def _show_empty_state(self):
        self._show_empty_chart(self.widget.time_series_ax, "No data available")
        self._show_empty_chart(self.widget.failure_ax, "No data available")
        self.widget.time_series_canvas.draw()
        self.widget.failure_canvas.draw()

    def _show_empty_chart(self, ax, message):
        ax.clear()
        ax.text(0.5, 0.5, message, ha='center', va='center', transform=ax.transAxes,
               color='#777777', fontsize=10)
        ax.set_title('')
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)