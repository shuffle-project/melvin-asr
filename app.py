""" Entry point for the API """
import multiprocessing
from src.helper.logger import Logger
from src.api.rest.run import run_flask_app_prod
from src.api.websocket.run import run_websocket_app
from src.config import CONFIG
from src.transcription.run import run_file_transcriber


def run(port, websocket_port, environment, host):
    """start flask & websockets apps for development and production based on environment"""

    log = Logger("app.py", True)

    if environment == "production":
        log.print_log("Running production..")
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

    # elif environment == "development":
    #     print("Running development..")
    #     if len(sys.argv) > 1:
    #         if sys.argv[1] == "websocket":
    #             run_websocket_app(websocket_port, host)
    #         elif sys.argv[1] == "rest":
    #             run_flask_app_dev(port, host)
    #         else:
    #             print("Invalid argument, please use 'websocket' or 'rest'")
    #     else:
    #         print(
    #             "No specific server type provided,"
    #             + " please use 'python api websocket' or 'python api rest'"
    #         )

    # else:
    #     print("ENVIRONMENT is not set correctly")


if __name__ == "__main__":
    run(CONFIG["PORT"], CONFIG["WEBSOCKET_PORT"], CONFIG["ENVIRONMENT"], CONFIG["HOST"])
