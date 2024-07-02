""" Entry point for the application """
import multiprocessing
import os
import signal
from src.helper.logger import Logger
from src.helper.config import CONFIG
from src.rest.run import run_rest_api
from src.websocket.run import run_websocket_api

LOGGER = Logger("app.py", True)


def run(port, websocket_port, host):
    """start flask & websockets apps"""
    websocket_server = multiprocessing.Process(
        target=run_websocket_api,
        args=(
            websocket_port,
            host,
        ),
    )
    flask_server = multiprocessing.Process(
        target=run_rest_api,
        args=(
            port,
            host,
        ),
    )
    websocket_server.start()
    flask_server.start()
    websocket_server.join()
    flask_server.join()


if __name__ == "__main__":
    LOGGER.print_log(str(CONFIG))
    try:
        run(CONFIG["rest_port"], CONFIG["websocket_port"], CONFIG["host"])
    except KeyboardInterrupt:
        current_pid = os.getpid()
        print(f"Terminating all processes for PID {current_pid}")
        os.killpg(current_pid, signal.SIGTERM)
