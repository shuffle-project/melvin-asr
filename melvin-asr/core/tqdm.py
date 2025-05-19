import os
import sys
from contextlib import contextmanager


@contextmanager
def disable_tqdm():
    devnull = open(os.devnull, "w")
    stderr = sys.stderr
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = stderr
