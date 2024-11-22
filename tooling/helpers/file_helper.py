import os
import json

DATA_BASE_PATH = os.path.join(os.getcwd(), "data")


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
    elif val == -1000:
        return "ERR"
    return round(val, round_value)


def safe_divide_for_table(sum, amount, round_value=2):
    if amount == 0:
        return "N/A"
    return round((sum / amount), round_value)


def get_file_name(path, scale):
    return path.replace(f"{os.path.join(DATA_BASE_PATH, scale)}/", "")
