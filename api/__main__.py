"""
This module contains the Flask app and the API endpoints.
"""
import json
import os
import time
import uuid

import waitress
from flask import Flask, request, jsonify
from dotenv import dotenv_values
from config import AUDIO_FILE_PATH, SETTING_PATH, STATUS_PATH
from src.helper.welcome_message import welcome_message
from src.transcription_request_handling.transcription import (
    Transcription,
    TranscriptionNotFoundError,
    TranscriptionStatusValue
)
from src.helper.convert_save_received_audio_files import convert_to_wav

# .env setup
config = dotenv_values()
print("DOTENV: " + str(config))
if "PORT" not in config:
    print("DOTENV: PORT is None, default to 5000")
    config["PORT"] = 5000
if "ENVIRONMENT" not in config:
    print("DOTENV: ENVIRONMENT is None, default to development")
    config["ENVIRONMENT"] = "development"

# bootstrap
def create_app():
    """Function to create the Flask app"""

    app = Flask(__name__)

    # Base endpoint with API usage information
    @app.route("/")
    def welcome():
        """Function that returns basic information about the API usage."""
        return welcome_message()


    @app.route("/transcriptions", methods=["POST"])
    def transcribe_audio():
        """API endpoint to transcribe an audio file"""
        # TODO: Once status handling is done, move this to a separate function
        print("request.files", request.files)
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            transcription = Transcription(uuid.uuid4())
            result = convert_to_wav(
                file, AUDIO_FILE_PATH, transcription.transcription_id
            )

            time.sleep(1)

            transcription.settings = json.loads(request.form["settings"])

            if result["success"] is not True:
                transcription.status = TranscriptionStatusValue.ERROR.value
                transcription.error_message = result["message"]

            transcription.save_to_file()
            return jsonify(transcription.get_status())
        return "Something went wrong"

    @app.route("/transcriptions/<transcription_id>", methods=["GET"])
    def get_transcription_status_route(transcription_id):
        """API endpoint to get the status of a transcription"""
        # TODO: Once status handling is done, move this to a separate function
        try:
            file_path = os.path.join(STATUS_PATH, f"{transcription_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return jsonify(json.load(file))
            else:
                raise TranscriptionNotFoundError(transcription_id)
        except TranscriptionNotFoundError as e:
            return jsonify(str(e)), 404

    @app.route("/health", methods=["GET"])
    def health_check():
        """return health status"""
        return "OK"

    # @app.route("/stream_transcribe", methods=["POST"])
    # def stream_transcribe():
    #     """transcribes an audio stream"""
    return app

# start flask app for development and waitress for production
if config["ENVIRONMENT"] == "production":
    print("Running production..")
    waitress.serve(create_app(), port=config["PORT"], url_scheme="https")
if config["ENVIRONMENT"] == "development":
    print("Running development..")
    create_app().run(debug=True, port=config["PORT"])
else:
    print("ENVIRONMENT is not set correctly")
