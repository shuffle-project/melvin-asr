"""
This module contains the Startup functions for the file transcriber.
"""
import multiprocessing
from src.helper.model_handler import ModelHandler
from src.config import CONFIG
from src.helper.logger import Color, Logger
from src.transcription.rest_runner import Runner

LOGGER = Logger("run_file_transcriber", True, Color.YELLOW)


def run_file_transcriber() -> dict:
    """Returns the models.yaml file as dict."""
    new_runner = []
    runner_id = 0
    for runner in CONFIG["rest_runner"]:
        new_runner.append(
            multiprocessing.Process(
                target=start_runner,
                args=(
                    runner["model"],
                    runner_id,
                    runner["device"],
                    runner["compute_type"],
                ),
            )
        )
        runner_id += 1

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
