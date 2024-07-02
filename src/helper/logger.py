""" simple Logger to keep track of the program's progress """

from datetime import datetime
import random
from src.helper.config import CONFIG

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


class Logger:
    """This class handles the logging of the program."""

    def __init__(
        self,
        identifier: str,
        debug: bool = CONFIG["debug"],
        debug_color: Color = Color.BLUE,
        pre_identifier: str = "",
        error_color: Color = Color.FAIL,
    ):
        """Constructor of the Logger class."""
        self.debug = debug
        self.identifier = identifier
        self.debug_color = debug_color
        self.pre_identifier = pre_identifier
        self.error_color = error_color

    def print_log(self, message: str) -> None:
        """Prints a log message."""
        if self.debug:
            print(
                self.debug_color
                + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {self.identifier}] {self.pre_identifier + message}"
                + Color.ENDC
            )

    def print_error(self, message: str) -> None:
        """Prints an error message."""
        print(
            self.error_color
            + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {self.identifier}] {self.pre_identifier + message}"
            + Color.ENDC
        )
