"""Flask app to handle the REST API requests"""
import json
import time
import uuid
from functools import wraps
from pydub import AudioSegment
from flask import Flask, jsonify, request
from src.helper.logger import Color, Logger
from src.config import CONFIG
from src.helper.convert_save_received_audio_files import convert_to_wav
from src.helper.transcription import (
    Transcription,
    TranscriptionStatusValue,
)
from src.api.rest.endpoints.welcome import welcome_message
from src.helper.data_handler import DataHandler

LOGGER = Logger("FlaskApp", False, Color.GREEN)
DATA_HANDLER = DataHandler()


def create_app():
    """Function to create the Flask app"""

    app = Flask(__name__)

    def require_api_key(func):
        """Decorator function to require an API key for a route"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("key")

            if api_key and api_key == CONFIG["API_KEY"]:
                return func(*args, **kwargs)
            return (
                LOGGER.print_error(
                    "Unauthorized REST API request. "
                    + f"api_key: {api_key}, config_key: {CONFIG['API_KEY']}"
                ),
                jsonify({"error": "Unauthorized. Please provide a valid API key"}),
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
            data = DATA_HANDLER.get_status_file_by_id(file_name)
            transcriptions.append(
                {
                    "transcription_id": data.get("transcription_id"),
                    "status": data.get("status"),
                }
            )
        return jsonify(transcriptions)

    @app.route("/transcriptions/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_transcriptions_id(transcription_id):
        """API endpoint to get the status of a transcription"""
        file = DATA_HANDLER.get_status_file_by_id(transcription_id)
        if file:
            return jsonify(file)
        return "Transcription not found", 404

    @app.route("/transcriptions", methods=["POST"])
    @require_api_key
    def transcribe_audio():
        """API endpoint to transcribe an audio file"""
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            transcription = Transcription(uuid.uuid4())
            audio = AudioSegment.from_file(file.stream)
            result = convert_to_wav(
                audio, CONFIG["AUDIO_FILE_PATH"], transcription.transcription_id
            )

            time.sleep(1)

            try:
                transcription.settings = json.loads(request.form["settings"])
            except KeyError:
                transcription.settings = None

            if result["success"] is not True:
                transcription.status = TranscriptionStatusValue.ERROR
                transcription.error_message = result["message"]

            transcription.save_to_file()
            return jsonify(transcription.get_status())
        return "Something went wrong"

    return app
