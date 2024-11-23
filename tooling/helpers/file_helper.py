import os
import json

DATA_BASE_PATH = os.path.join(os.getcwd(), "data")
ERR_CODE = -1000

def load_file_list(size: str):
    dirpath = os.path.join(DATA_BASE_PATH, size)
    return [
        os.path.join(dirpath, f)
        for f in os.listdir(dirpath)
        if os.path.isfile(os.path.join(dirpath, f)) and f.endswith(".wav")
    ]


def get_expected_transcription(path: str):
    json_path = f"{path[:-4]}.json"

    with open(json_path) as f:
        d = json.load(f)
        return str(d["transcript"])


def transform_value_for_table(val, round_value=2):
    if val is None:
        return "-"
    elif val == ERR_CODE:
        return "ERR"
    return round(val, round_value)


def get_file_name(path, scale):
    return path.replace(f"{os.path.join(DATA_BASE_PATH, scale)}/", "")
