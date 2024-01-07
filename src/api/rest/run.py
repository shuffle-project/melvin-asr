""" This module contains the functions to run the flask app. """
import waitress
from src.helper.logger import Color, Logger
from src.api.rest.flask_app import create_app

log = Logger("run_file_transcriber", True, Color.UNDERLINE)


def run_flask_app_dev(port, host):
    """Starts the flask app for development."""
    log.print_log(f"starting Flask app dev on '{host}:{port}'")
    app = create_app()
    app.run(debug=True, port=port, host=host)


def run_flask_app_prod(port, host):
    """Starts the flask app for production."""
    log.print_log(f"starting Flask app prod on '{host}:{port}'")
    app = create_app()
    waitress.serve(app, port=port, url_scheme="https", host=host)
