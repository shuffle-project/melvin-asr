import json
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


def load_example_translation():
    path = os.path.join(
        os.getcwd(), "src", "helper", "test_base", "example_translation.json"
    )
    with open(path, "r") as file:
        return json.load(file)
