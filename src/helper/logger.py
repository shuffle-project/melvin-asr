"""simple Logger to keep track of the program's progress"""

import logging
import random

from faster_whisper.utils import os


class Color:
    """This class contains ANSI escape sequences for colored output."""

    ENDC = "\033[0m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    @staticmethod
    def random():
        """Returns a random color."""
        return [
            Color.RED,
            Color.GREEN,
            Color.YELLOW,
            Color.BLUE,
            Color.MAGENTA,
            Color.CYAN,
            Color.WHITE,
        ][random.randint(0, 6)]


class LogFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Color.BLUE,
        logging.INFO: Color.WHITE,
        logging.WARNING: Color.BRIGHT_YELLOW,
        logging.ERROR: Color.YELLOW,
        logging.CRITICAL: Color.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the string and set its color based on the log level"""
        return (
            self.FORMATS.get(record.levelno, Color.WHITE)
            + super().format(record)
            + Color.ENDC
        )


def init_logger() -> None:
    """Set the LogFormatter as a formatter for the global logger"""
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    # set a format which is simpler for console use
    # Note: identifier is only given by some classes that use this similar to a traceID
    formatter = LogFormatter(
        "[%(asctime)s %(name)s:%(lineno)d] %(levelname)s %(message)s"
    )
    # tell the handler to use this format
    console.setFormatter(formatter)
    # set to be the only logger
    # Ensure that only one handler is currently configured
    assert len(logging.getLogger("").handlers) == 1
    # Replace the current logger with the logger with the custom formatting
    logging.getLogger("").handlers = [console]


def get_logger_with_id(name: str, id: str) -> logging.Logger:
    """Uniform way to get a formatted logger with the id in its name"""
    return logging.getLogger(f"{name} ({id})")


def set_global_loglevel(level: str):
    levelMap = logging.getLevelNamesMapping()
    if level not in levelMap:
        logging.getLogger(__name__).info(
            f"The configured loglevel of {level} is not a valid loglevel. Defaulting to INFO!"
        )
    logging.basicConfig(level=levelMap.get(level, "info"))
