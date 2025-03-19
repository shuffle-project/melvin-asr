from contextlib import contextmanager
import os
import sys

@contextmanager
def disable_tqdm():
    devnull = open(os.devnull, "w")
    stderr = sys.stderr
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = stderr
