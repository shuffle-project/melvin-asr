from pathlib import Path

_root_path = Path(__file__).resolve().parents[2]
_data_path = Path(_root_path, "data").resolve()

jobs_path = Path(_data_path, "jobs").resolve()
config_path = Path(_root_path, "config.yml").resolve()
models_path = Path(_data_path, "models").resolve()
upload_path = Path(_data_path, "uploads").resolve()