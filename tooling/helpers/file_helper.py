import os
from pathlib import Path

DATA_BASE_PATH = os.path.join(os.getcwd(), "data")


def load_file_list(size: str):
    dirpath = os.path.join(DATA_BASE_PATH, size)
    return [
        os.path.join(dirpath, f)
        for f in os.listdir(dirpath)
        if os.path.isfile(os.path.join(dirpath, f)) and f.endswith(".wav")
    ]


def get_expected_transcription(path: str):
    content = Path(f"{path}.txt").read_text()
    content = content.replace("\n", "")
    return str(content)
