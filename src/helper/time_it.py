import time

from src.helper.model_handler import LOGGER


def time_it(func):
    """Decorator function to measure and print the execution time of a function."""

    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        LOGGER.debug(
            f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute."
        )
        return result

    return wrapper
