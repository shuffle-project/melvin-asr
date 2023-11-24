"""Installs the models in /runner_config.py"""

import os
import sys
import inspect
import subprocess

# Set the current and parent directory paths
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Need to explicitly import runner_config from parent directory
# pylint: disable=C0413
from runner_config import WHISPER_MODELS

# Print the WHISPER_MODELS to confirm it's a list
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
