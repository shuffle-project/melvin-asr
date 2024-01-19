"""Flask app to handle the REST API requests"""
import json
import time
import uuid
from datetime import datetime
from functools import wraps
from pydub import AudioSegment
from flask import Flask, jsonify, request
from src.helper.logger import Color, Logger
from src.config import CONFIG
from src.helper.types.transcription_status import (
    TranscriptionStatus,
)
from src.api.rest.endpoints.welcome import welcome_message
from src.helper.data_handler import DataHandler

LOGGER = Logger("FlaskApp", False, Color.GREEN)
DATA_HANDLER = DataHandler()


def create_app(auth_key=CONFIG["API_KEY"]):
    """Function to create the Flask app"""

    app = Flask(__name__)

    def require_api_key(func):
        """Decorator function to require an API key for a route"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("key")

            if api_key and api_key == auth_key:
                return func(*args, **kwargs)

            LOGGER.print_error(
                "Unauthorized REST API request. "
                + f"api_key: {api_key}, config_key: {auth_key}"
            )

            return (
                jsonify("Unauthorized"),
                401,
            )

        return wrapper

    @app.route("/")
    def welcome():
        """Function that returns basic information about the API usage."""
        return welcome_message()

    @app.route("/health", methods=["GET"])
    def health_check():
        """return health status"""
        return "OK"

    @app.route("/transcriptions", methods=["GET"])
    @require_api_key
    def get_transcriptions():
        """API endpoint to get all transcriptions and their status in a list"""
        transcriptions = []
        for file_name in DATA_HANDLER.get_all_status_filenames():
            try:
                file_name = file_name[:-5]  # remove .json
                data = DATA_HANDLER.get_status_file_by_id(file_name)
                transcriptions.append(
                    {
                        "transcription_id": data["transcription_id"],
                        "status": data["status"],
                    }
                )
            # pylint: disable=broad-except
            except Exception as e:
                LOGGER.print_error(f"Error while reading status file {file_name}: {e}")
                DATA_HANDLER.delete_status_file(file_name)
        return jsonify(transcriptions)

    @app.route("/transcriptions/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_transcriptions_id(transcription_id):
        """API endpoint to get the status of a transcription"""
        file = DATA_HANDLER.get_status_file_by_id(transcription_id)
        if file:
            return jsonify(file), 200
        return "Transcription ID not found", 404

    @app.route("/transcriptions", methods=["POST"])
    @require_api_key
    def post_transcription():
        """API endpoint to transcribe an audio file"""
        try:
            if "file" not in request.files:
                return "No file posted", 400
            file = request.files["file"]
            if file:
                # store audio file
                transcription_id = str(uuid.uuid4())
                result = DATA_HANDLER.save_audio_file(
                    AudioSegment.from_file(file.stream), transcription_id
                )
                if result["success"] is not True:
                    return jsonify(result["message"]), 400

                # sleep to make sure that the file is saved before the transcription starts
                time.sleep(0.1)

                # create transcription status file
                settings = (
                    json.loads(request.form["settings"])
                    if "settings" in request.form
                    else None
                )
                data = {
                    "transcription_id": transcription_id,
                    "status": TranscriptionStatus.IN_QUERY.value,
                    "start_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "settings": settings,
                }

                DATA_HANDLER.write_status_file(transcription_id, data)
                return jsonify(data), 200
        # pylint: disable=broad-except
        except Exception as e:
            LOGGER.print_error(f"Error while POST Transcriptions: {e}")
        return "Something went wrong"

    return app
