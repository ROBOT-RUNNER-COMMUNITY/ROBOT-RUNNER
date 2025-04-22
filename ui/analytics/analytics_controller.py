# ui/analytics/analytics_controller.py
from PyQt6.QtCore import QObject
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class AnalyticsController(QObject):
    def __init__(self, widget, data_loader):
        super().__init__()
        self.widget = widget
        self.data_loader = data_loader
        self._connect_signals()
        
    def _connect_signals(self):
        self.widget.refresh_button.clicked.connect(lambda: self.data_loader.load_data(force=True))
        self.data_loader.data_loaded.connect(self.update_analytics)
        
    def update_analytics(self, data):
        try:
            if not data or not isinstance(data, dict) or not data.get('recent_test_runs'):
                self._show_empty_state()
                return
                
            self._update_time_series(data)
            self._update_failure_analysis(data)
            
        except Exception as e:
            print(f"Error updating analytics: {e}")
            self._show_empty_state()

    def _update_time_series(self, data):
        self.widget.time_series_ax.clear()
        
        recent_runs = data.get('recent_test_runs', [])
        if not recent_runs:
            self._show_empty_chart(self.widget.time_series_ax, "No test runs available")
            self.widget.time_series_canvas.draw()
            return
            
        # Group by date
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
            self._show_empty_chart(self.widget.time_series_ax, "Not enough data points")
            self.widget.time_series_canvas.draw()
            return
            
        # Prepare data
        times = [date_stats[d]['total_time'] for d in dates]
        failures = [date_stats[d]['failures'] for d in dates]
        counts = [date_stats[d]['count'] for d in dates]
        failure_rates = [f/c if c > 0 else 0 for f, c in zip(failures, counts)]
        
        # Plot execution time
        self.widget.time_series_ax.plot(dates, times, '-o', color='#3498db', label='Execution Time (s)')
        self.widget.time_series_ax.set_ylabel('Time (s)', color='#3498db')
        self.widget.time_series_ax.tick_params(axis='y', labelcolor='#3498db')
        
        # Plot failure rate
        ax2 = self.widget.time_series_ax.twinx()
        ax2.plot(dates, failure_rates, 'r--', label='Failure Rate')
        ax2.set_ylabel('Failure Rate', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim(0, 1)
        
        # Formatting
        self.widget.time_series_ax.set_title('Test Execution Trends', pad=10)
        self.widget.time_series_ax.grid(True, linestyle='--', alpha=0.6)
        self.widget.time_series_ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        # Format x-axis dates
        self.widget.time_series_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.widget.time_series_ax.xaxis.set_major_locator(mdates.DayLocator())
        self.widget.time_series_fig.autofmt_xdate()
        
        self.widget.time_series_fig.tight_layout()
        self.widget.time_series_canvas.draw()

    def _update_failure_analysis(self, data):
        self.widget.failure_ax.clear()
        
        test_details = data.get('test_details', [])
        if not test_details:
            self._show_empty_chart(self.widget.failure_ax, "No test details available")
            self.widget.failure_canvas.draw()
            return
            
        # Count failures by test
        failure_counts = {}
        for test in test_details:
            if test.get('status') == 'FAIL':
                test_name = test.get('name', 'Unknown')
                failure_counts[test_name] = failure_counts.get(test_name, 0) + 1
        
        if not failure_counts:
            self._show_empty_chart(self.widget.failure_ax, "No failures recorded")
            self.widget.failure_canvas.draw()
            return
            
        # Get top 10 failing tests
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        test_names = [x[0] for x in sorted_failures]
        fail_counts = [x[1] for x in sorted_failures]
        
        # Create horizontal bar chart
        y_pos = range(len(test_names))
        bars = self.widget.failure_ax.barh(y_pos, fail_counts, color='#e74c3c')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            self.widget.failure_ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                                      f'{width}', ha='left', va='center')
        
        # Formatting
        self.widget.failure_ax.set_yticks(y_pos)
        self.widget.failure_ax.set_yticklabels(test_names)
        self.widget.failure_ax.set_xlabel('Failure Count')
        self.widget.failure_ax.set_title('Top Failing Tests', pad=10)
        self.widget.failure_ax.grid(True, linestyle='--', alpha=0.6)
        self.widget.failure_fig.tight_layout()
        self.widget.failure_canvas.draw()

    def _show_empty_state(self):
        self._show_empty_chart(self.widget.time_series_ax, "No data available")
        self._show_empty_chart(self.widget.failure_ax, "No data available")
        self.widget.time_series_canvas.draw()
        self.widget.failure_canvas.draw()

    def _show_empty_chart(self, ax, message):
        ax.clear()
        ax.text(0.5, 0.5, message, ha='center', va='center', transform=ax.transAxes)
        ax.set_title('')
        ax.grid(False)