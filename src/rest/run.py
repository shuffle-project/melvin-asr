"""Entry point for the REST API."""

import logging
import multiprocessing
import waitress
from src.rest.runner import Runner
from src.helper.config import CONFIG
from src.rest.flask_app import create_app

LOGGER = logging.getLogger(__name__)


def run_rest_api(port, host) -> dict:
    """Returns the models.yaml file as dict."""
    flask_process = multiprocessing.Process(
        target=run_flask_app,
        args=(port, host),
    )

    runner_process = multiprocessing.Process(
        target=start_runners,
        args=(),
    )

    flask_process.start()
    runner_process.start()
    flask_process.join()
    runner_process.join()


def run_flask_app(port, host):
    """Starts the flask app for production."""
    LOGGER.info(f"Starting Flask app prod on '{host}:{port}'")
    app = create_app()
    waitress.serve(app, port=port, url_scheme="https", host=host)


def start_runners() -> dict:
    """Returns the models.yaml file as dict."""
    new_runner = []
    runner_id = 1
    for config in CONFIG["rest_runner"]:
        new_runner.append(
            multiprocessing.Process(
                target=start_runner,
                args=(config, runner_id),
            )
        )
        runner_id += 1

    for runner in new_runner:
        runner.start()
    for runner in new_runner:
        runner.join()


def start_runner(config: dict, identifier: int) -> None:
    """Starts a file transcriber."""
    LOGGER.info(f"Starting REST runner with config: {config}..")
    runner = Runner(config, identifier)
    runner.run()
