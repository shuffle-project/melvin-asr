"""Installs the models in /runner_config.py"""

import os
import sys
import json
import inspect
import subprocess

# load whisper models from shared-config.json
with open("shared/config.json", encoding="utf-8") as json_data:
    data = json.load(json_data)
WHISPER_MODELS = data["models"]

# Set the current and parent directory paths
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

print("WHISPER_MODELS:", WHISPER_MODELS)
if not isinstance(WHISPER_MODELS, list):
    raise ValueError("WHISPER_MODELS must be a list")


def run_bash_command(command):
    """Function to run a bash command and allow its output to print to command line"""
    subprocess.run(command, shell=True, check=True)


def download_models(models):
    """Download all models"""
    for model in models:
        print(f"Downloading {model} model...")
        run_bash_command(f"./whisper.cpp/models/download-ggml-model.sh {model}")


# Run the function with the WHISPER_MODELS config
download_models(WHISPER_MODELS)
