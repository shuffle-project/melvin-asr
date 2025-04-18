"""Entry point for the application"""
from src.helper.logger import init_logger, set_global_loglevel
init_logger()

import logging
import multiprocessing
import os
import signal
import sys
from src.helper.data_handler import DataHandler
from src.helper.config import CONFIG
from src.rest.run import run_rest_api
from src.websocket.run import run_websocket_api

if sys.version_info < (3, 11):
    sys.exit("Please use Python 3.11+")

LOGGER = logging.getLogger(__name__)


def run(port, websocket_port, host):
    """start fastapi & websockets apps"""
    websocket_server = multiprocessing.Process(
        target=run_websocket_api,
        args=(
            websocket_port,
            host,
        ),
    )
    rest_server = multiprocessing.Process(
        target=run_rest_api,
        args=(
            port,
            host,
        ),
    )
    websocket_server.start()
    rest_server.start()
    websocket_server.join()
    rest_server.join()


if __name__ == "__main__":
    set_global_loglevel(CONFIG.get("log_level", "INFO"))
    LOGGER.debug(str(CONFIG))
    DataHandler.cleanup_interrupted_jobs()
    try:
        run(CONFIG["rest_port"], CONFIG["websocket_port"], CONFIG["host"])
    except KeyboardInterrupt:
        current_pid = os.getpid()
        print(f"Terminating all processes for PID {current_pid}")
        os.killpg(current_pid, signal.SIGTERM)
