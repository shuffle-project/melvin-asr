"""
This module contains the Flask app and the API endpoints.
"""
import asyncio
import multiprocessing
import sys
import waitress
from dotenv import dotenv_values

from rest.flask_app import create_app
from websocket.websockets_app import WebSocketServer

# .env setup
config = dotenv_values()
print("DOTENV: " + str(config))
if "PORT" not in config:
    print("DOTENV: PORT is None, default to 1234")
    config["PORT"] = 1234
if "WEBSOCKET_PORT" not in config:
    print("DOTENV: WEBSOCKET_PORT is None, default to 1235")
    config["WEBSOCKET_PORT"] = 1235
if "ENVIRONMENT" not in config:
    print("DOTENV: ENVIRONMENT is None, default to development")
    config["ENVIRONMENT"] = "development"


# startup functions for flask & websockets apps
def run_websocket_app():
    """Starts the websocket server."""
    web_socket_server = WebSocketServer(config["WEBSOCKET_PORT"])
    asyncio.run(web_socket_server.start_server())


def run_flask_app_dev():
    """Starts the flask app for development."""
    app = create_app()
    app.run(debug=True, port=config["PORT"])


def run_flask_app_prod():
    """Starts the flask app for production."""
    app = create_app()
    waitress.serve(app, port=config["PORT"], url_scheme="https")


# start flask & websockets apps for development and production based on environment
if config["ENVIRONMENT"] == "production":
    print("Running production..")
    websocket_server = multiprocessing.Process(target=run_websocket_app)
    flask_server = multiprocessing.Process(target=run_flask_app_prod)
    websocket_server.start()
    flask_server.start()
    websocket_server.join()
    flask_server.join()

elif config["ENVIRONMENT"] == "development":
    print("Running development..")
    if len(sys.argv) > 1:
        if sys.argv[1] == "websocket":
            run_websocket_app()
        elif sys.argv[1] == "flask":
            run_flask_app_dev()
        else:
            print("Invalid argument, please use 'websocket' or 'flask'")
    else:
        print(
            "No specific server type provided," +
            "please use 'python api websocket' or 'python api flask'"
        )
        
else:
    print("ENVIRONMENT is not set correctly")
