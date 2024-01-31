""" Entry point for the API """
import multiprocessing
import os
import signal
from src.helper.logger import Color, Logger
from src.api.rest.run import run_flask_app_prod
from src.api.websocket.run import run_websocket_app
from src.config import CONFIG
from src.transcription.run import run_file_transcriber

LOGGER = Logger("app.py", True, Color.GREEN)


def run(port, websocket_port, host):
    """start flask & websockets apps"""
    transcription_runner = multiprocessing.Process(
        target=run_file_transcriber,
        args=(),
    )
    websocket_server = multiprocessing.Process(
        target=run_websocket_app,
        args=(
            websocket_port,
            host,
        ),
    )
    flask_server = multiprocessing.Process(
        target=run_flask_app_prod,
        args=(
            port,
            host,
        ),
    )
    transcription_runner.start()
    websocket_server.start()
    flask_server.start()
    transcription_runner.join()
    websocket_server.join()
    flask_server.join()


if __name__ == "__main__":
    LOGGER.print_log(CONFIG)
    try:
        run(CONFIG["PORT"], CONFIG["WEBSOCKET_PORT"], CONFIG["HOST"])
    except KeyboardInterrupt:
        current_pid = os.getpid()
        print(f"Terminating all processes for PID {current_pid}")
        os.killpg(current_pid, signal.SIGTERM)
