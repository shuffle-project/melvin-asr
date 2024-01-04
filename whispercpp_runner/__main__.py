"""This File initializes the runners for the transcription process"""
import os
from dotenv import dotenv_values
from src.runner import Runner

def read_config():
    """Read the config from .env or environment variables"""
    dontenv_config = dotenv_values()  # Load .env file

    # Try to get MODEL from .env, otherwise from environment variable
    model = dontenv_config.get("MODEL", os.getenv("MODEL"))

    # Try to get RUNNER_TYPE from .env, otherwise from environment variable
    runner_type = dontenv_config.get("RUNNER_TYPE", os.getenv("RUNNER_TYPE"))

    # Validate RUNNER_TYPE
    if runner_type not in ["rest", "stream"]:
        print("RUNNER_TYPE not valid, fallback to rest")
        runner_type = "rest"

    return {"MODEL": model, "RUNNER_TYPE": runner_type}

config = read_config()
print(config)

runner = Runner(config["MODEL"], config["RUNNER_TYPE"])
runner.run()
