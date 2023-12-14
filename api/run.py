"""
This module contains the Flask app and the API endpoints.
"""
import asyncio
import multiprocessing
import sys
import waitress

from rest.flask_app import create_app
from websocket.websockets_app import WebSocketServer


# startup functions for flask & websockets apps
def run_websocket_app(websocket_port):
    """Starts the websocket server."""
    web_socket_server = WebSocketServer(websocket_port)
    asyncio.run(web_socket_server.start_server())


def run_flask_app_dev(port):
    """Starts the flask app for development."""
    app = create_app()
    app.run(debug=True, port=port)


def run_flask_app_prod(port):
    """Starts the flask app for production."""
    app = create_app()
    print("starting Flask app on port " + port)
    waitress.serve(app, port=port, url_scheme="https")


# start flask & websockets apps for development and production based on environment
def run(port: str, websocket_port: str, environment: str):
    """Starts the flask and websocket apps."""
    if environment == "production":
        print("Running production..")
        websocket_server = multiprocessing.Process(
            target=run_websocket_app, args=(websocket_port,)
        )
        flask_server = multiprocessing.Process(target=run_flask_app_prod, args=(port,))
        websocket_server.start()
        flask_server.start()
        websocket_server.join()
        flask_server.join()

    elif environment == "development":
        print("Running development..")
        if len(sys.argv) > 1:
            if sys.argv[1] == "websocket":
                run_websocket_app(websocket_port)
            elif sys.argv[1] == "flask":
                run_flask_app_dev(port)
            else:
                print("Invalid argument, please use 'websocket' or 'flask'")
        else:
            print(
                "No specific server type provided,"
                + " please use 'python api websocket' or 'python api flask'"
            )

    else:
        print("ENVIRONMENT is not set correctly")
