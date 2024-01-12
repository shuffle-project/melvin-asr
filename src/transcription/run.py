"""
This module contains the Startup functions for the file transcriber.
"""
import multiprocessing
import os

import yaml
from src.helper.model_handler import ModelHandler
from src.config import CONFIG
from src.helper.logger import Color, Logger
from src.transcription.rest_runner import Runner

LOGGER = Logger("run_file_transcriber", True, Color.YELLOW)


def run_file_transcriber() -> dict:
    """Returns the models.yaml file as dict."""
    path = os.getcwd() + CONFIG["MODEL_CONFIG_YAML_PATH"]
    with open(path, "r", encoding="utf-8") as data:
        config = yaml.safe_load(data)
        LOGGER.print_log(f"Starting file transcription runners..\nConfig: {config}")

        ## make sure to allow 10 runners max
        if (len(config["rest_runner"].items()) > 10):
            LOGGER.print_log("Too many runners in rest_runner config file, please use 10 or less.")
            return

        ## Add new Runner to Multiprocessing
        new_runner = []
        for runner_name, runner in config["rest_runner"].items():
            new_runner.append(multiprocessing.Process(
                target=start_runner,
                args=(runner["model"], runner_name, runner["device"], runner["compute_type"]),
            ))
        for runner in new_runner:
            runner.start()
        for runner in new_runner:
            runner.join()


def start_runner(
    model_name: str, identifier: str, device: str, compute_type: str
) -> None:
    """Starts a file transcriber."""
    ModelHandler().setup_model(model_name)
    Logger("run_file_transcriber", True, Color.BRIGHT_WHITE).print_log(
        f"Starting file transcription runner: {identifier} with model {model_name}.."
    )
    runner = Runner(model_name, identifier, device, compute_type)
    runner.run()
