import os
import json

DATA_BASE_PATH = os.path.join(os.getcwd(), "data")
EXPORT_BASE_PATH = os.path.join(os.getcwd(), "export")

def load_file_list(size: str):
    dirpath = os.path.join(DATA_BASE_PATH, size)
    return [
        os.path.join(dirpath, f)
        for f in os.listdir(dirpath)
        if os.path.isfile(os.path.join(dirpath, f)) and f.endswith(".wav")
    ]

def load_export_file_list():
    return [
        os.path.join(EXPORT_BASE_PATH, f)
        for f in os.listdir(EXPORT_BASE_PATH)
        if os.path.isfile(os.path.join(EXPORT_BASE_PATH, f)) and f.endswith(".json")
    ]


def get_corresponding_transcript(export_path: str, scale: str):
    path = export_path.replace(f"{EXPORT_BASE_PATH}", f"{os.path.join(DATA_BASE_PATH, scale)}")

    with open(path) as f:
        d = json.load(f)
        return str(d["transcript"])

def get_file_name(path, scale):
    return path.replace(f"{os.path.join(DATA_BASE_PATH, scale)}/", "")

def get_file_id(export_dir_path):
    p = export_dir_path.replace(f"{EXPORT_BASE_PATH}/", "")
    return p.removesuffix(".json")

def clean_export_dir():
    dir = os.path.join(os.getcwd(), "export")
    for f in os.listdir(dir):
        if not f.endswith(".json"):
            continue
        os.remove(os.path.join(dir, f))
