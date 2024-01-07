"""A simple system monitor for logging RAM usage."""
import psutil
from src.helper.logger import Logger


class SystemMonitor:
    """A simple system monitor for logging RAM usage."""

    def __init__(self):
        """Initialize the system monitor with a log file."""
        self.log = Logger("SystemMonitor", True)

    def return_cpu_usage(self) -> str:
        """Log the current CPU usage."""
        cpu_usage = psutil.cpu_percent()
        return f"Current CPU usage: {cpu_usage}%"

    def return_ram_usage(self):
        """Log the current RAM usage."""
        ram_usage = psutil.virtual_memory().percent
        return f"Current RAM usage: {ram_usage}%"
