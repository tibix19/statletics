import time
from datetime import datetime
from pathlib import Path

class PerformanceLogger:
    def __init__(self):
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / 'search_performance.log'
    
    def log_search_performance(self, search_term: str, elapsed_time: float, endpoint: str):
        """Log search performance metrics to a file.
        
        Args:
            search_term (str): The search term used
            elapsed_time (float): Total time taken for the search in seconds
            endpoint (str): The API endpoint that was called
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} | {endpoint} | Search: {search_term} | Time: {elapsed_time:.2f}s\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to performance log: {e}")

# Create a singleton instance
performance_logger = PerformanceLogger()
