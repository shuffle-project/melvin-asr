""" This module contains the functions to run the flask app. """
import waitress
from src.api.rest.flask_app import create_app


def run_flask_app_dev(port, host):
    """Starts the flask app for development."""
    app = create_app()
    app.run(debug=True, port=port, host=host)


def run_flask_app_prod(port, host):
    """Starts the flask app for production."""
    app = create_app()
    print(f"starting Flask app on '{host}:{port}'")
    waitress.serve(app, port=port, url_scheme="https", host=host)
