""" Script to download and setup whisper.cpp models """
import os
import sys
import json
import inspect
import subprocess

# Load whisper models from shared-config.json
with open("shared/config.json", encoding="utf-8") as json_data:
    data = json.load(json_data)
WHISPER_MODELS = data["models"]

# Set the current and parent directory paths
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

print(f"WHISPER_MODELS: {WHISPER_MODELS}")
if not isinstance(WHISPER_MODELS, list):
    raise ValueError("WHISPER_MODELS must be a list")


def run_bash_command(command):
    """Function to run a bash command and allow its output to print to command line"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running command: {command}")
        print(e)
        sys.exit(1)

def clone_or_update_whisper_cpp():
    """Clone the whisper.cpp repository if it doesn't exist, or pull updates if it does"""
    repo_path = "whisper.cpp"
    if os.path.isdir(repo_path):
        print("whisper.cpp repository already exists. Pulling latest changes...")
        run_bash_command(f"cd {repo_path} && git pull")
    else:
        print("Cloning whisper.cpp repository...")
        run_bash_command("git clone https://github.com/ggerganov/whisper.cpp.git")

def download_models(models):
    """Download specified models"""
    for model in models:
        print(f"Downloading {model} model...")
        run_bash_command(f"./whisper.cpp/models/download-ggml-model.sh {model}")

def copy_models(path):
    """Copy all models to specified path"""
    for model in WHISPER_MODELS:
        print(f"Copying {model} model to {path}...")
        run_bash_command(f"cp whisper.cpp/models/ggml-{model}.bin {path}")


clone_or_update_whisper_cpp()
download_models(WHISPER_MODELS)
copy_models("./models")
