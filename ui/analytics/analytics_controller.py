from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
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
        self.data_loader.data_loaded.connect(self._handle_data_loaded)
        
    def _handle_data_loaded(self, data):
        """Handle loaded data and update UI"""
        try:
            if not data or not isinstance(data, dict):
                print("Invalid or empty data received in analytics")
                self._show_empty_state()
                return
                
            print(f"Analytics data received: {data.keys()}")  # Debug
            
            self._update_time_series(data)
            self._update_failure_analysis(data)
            
        except Exception as e:
            print(f"Analytics update error: {e}")
            self._show_empty_state()

    def _update_time_series(self, data):
        """Update the time series chart"""
        self.widget.time_series_ax.clear()
        
        recent_runs = data.get('recent_runs', [])
        print(f"Updating time series - Runs: {len(recent_runs)}")  # Debug
        
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
        if len(dates) < 2:
            self._show_empty_chart(self.widget.time_series_ax, "Not enough data points")
            self.widget.time_series_canvas.draw()
            return
            
        # Prepare data
        times = [date_stats[d]['total_time'] for d in dates]
        failures = [date_stats[d]['failures'] for d in dates]
        counts = [date_stats[d]['count'] for d in dates]
        failure_rates = [f/c if c > 0 else 0 for f, c in zip(failures, counts)]
        
        # Convert dates to matplotlib format
        mpl_dates = mdates.date2num(dates)
        
        # Plot execution time
        self.widget.time_series_ax.plot_date(
            mpl_dates, times, 
            '-o', color='#3498db', 
            label='Total Execution Time (s)'
        )
        self.widget.time_series_ax.set_ylabel('Execution Time (s)', color='#3498db')
        self.widget.time_series_ax.tick_params(axis='y', labelcolor='#3498db')
        
        # Plot failure rate on secondary axis
        ax2 = self.widget.time_series_ax.twinx()
        ax2.plot_date(
            mpl_dates, failure_rates,
            '-s', color='#e74c3c',
            label='Failure Rate'
        )
        ax2.set_ylabel('Failure Rate', color='#e74c3c')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        ax2.set_ylim(0, 1)  # Rate between 0-1
        
        # Formatting
        self.widget.time_series_ax.xaxis.set_major_formatter(
            mdates.DateFormatter('%Y-%m-%d')
        )
        self.widget.time_series_ax.xaxis.set_major_locator(
            mdates.DayLocator()
        )
        self.widget.time_series_fig.autofmt_xdate()
        
        self.widget.time_series_ax.set_title('Test Execution Trends')
        self.widget.time_series_ax.grid(True, linestyle='--', alpha=0.6)
        self.widget.time_series_ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        self.widget.time_series_canvas.draw()

    def _update_failure_analysis(self, data):
        """Update the failure analysis chart"""
        self.widget.failure_ax.clear()
        
        test_details = data.get('test_details', [])
        print(f"Updating failure analysis - Tests: {len(test_details)}")  # Debug
        
        if not test_details:
            self._show_empty_chart(self.widget.failure_ax, "No test details available")
            self.widget.failure_canvas.draw()
            return
            
        # Count failures by test
        failure_counts = {}
        for test in test_details:
            if test.get('status') == 'FAIL':
                test_name = f"{test.get('suite', '?')}.{test.get('test', '?')}"
                failure_counts[test_name] = failure_counts.get(test_name, 0) + 1
        
        if not failure_counts:
            self._show_empty_chart(self.widget.failure_ax, "No failures recorded")
            self.widget.failure_canvas.draw()
            return
            
        # Get top 10 failing tests
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        test_names = [x[0][:30] + '...' if len(x[0]) > 30 else x[0] for x in sorted_failures]
        fail_counts = [x[1] for x in sorted_failures]
        
        # Create horizontal bar chart
        y_pos = range(len(test_names))
        self.widget.failure_ax.barh(
            y_pos, fail_counts,
            color='#e74c3c'
        )
        self.widget.failure_ax.set_yticks(y_pos)
        self.widget.failure_ax.set_yticklabels(test_names)
        self.widget.failure_ax.set_xlabel('Failure Count')
        self.widget.failure_ax.set_title('Top Failing Tests')
        self.widget.failure_ax.grid(True, linestyle='--', alpha=0.6)
        
        self.widget.failure_canvas.draw()

    def _show_empty_state(self):
        """Show empty state for both charts"""
        self._show_empty_chart(self.widget.time_series_ax, "No data available")
        self._show_empty_chart(self.widget.failure_ax, "No data available")
        self.widget.time_series_canvas.draw()
        self.widget.failure_canvas.draw()

    def _show_empty_chart(self, ax, message):
        """Display message on empty chart"""
        ax.clear()
        ax.text(
            0.5, 0.5, message,
            ha='center', va='center',
            transform=ax.transAxes
        )
        ax.set_title('')
        ax.grid(False)