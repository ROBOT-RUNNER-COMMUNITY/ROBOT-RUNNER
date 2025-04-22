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
        
    def _setup_chart_styles(self):
        """Configure consistent styling for all charts"""
        rcParams.update({
            'axes.edgecolor': '#dddddd',
            'axes.labelcolor': '#555555',
            'text.color': '#333333',
            'xtick.color': '#777777',
            'ytick.color': '#777777',
            'axes.grid': True,
            'grid.alpha': 0.2,
            'grid.linestyle': '--'
        })

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
        times = [date_stats[d]['total_time']/date_stats[d]['count'] for d in dates]  # Avg time per test
        failure_rates = [date_stats[d]['failures']/date_stats[d]['count'] if date_stats[d]['count'] > 0 else 0 
                         for d in dates]
        
        # Main plot (execution time)
        ax.plot(dates, times, '-o', color='#3498db', linewidth=2, markersize=8,
                label='Avg Execution Time (s)')
        ax.set_ylabel('Time (s)', color='#3498db')
        ax.tick_params(axis='y', labelcolor='#3498db')
        ax.set_ylim(bottom=0)  # Force zero baseline
        
        # Failure rate plot
        ax2 = ax.twinx()
        ax2.plot(dates, failure_rates, 's--', color='#e74c3c', linewidth=2, markersize=6,
                label='Failure Rate')
        ax2.set_ylabel('Failure Rate', color='#e74c3c')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        ax2.set_ylim(0, 1.05)  # Slight padding
        
        # Formatting
        ax.set_title('Test Execution Trends', pad=20, fontsize=12, fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        
        # Combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper left')
        
        # Remove dark borders
        for spine in ax.spines.values():
            spine.set_visible(False)
        for spine in ax2.spines.values():
            spine.set_visible(False)
            
        self.widget.time_series_fig.tight_layout()
        self.widget.time_series_canvas.draw()