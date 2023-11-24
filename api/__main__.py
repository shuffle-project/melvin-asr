"""
This module contains the Flask app and the API endpoints.
"""
import json
import os
import time
import waitress
from flask import Flask, request, jsonify
from dotenv import dotenv_values
from config import AUDIO_FILE_PATH, SETTING_PATH
from src.helper.welcome_message import welcome_message
from src.transcription_request_handling.transcription import (
    Transcription,
    TranscriptionNotFoundError,
    TranscriptionStatusValue,
    search_undefined_transcripts,
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
    transcriptions: [Transcription] = []

    # Base endpoint with API usage information
    @app.route("/")
    def welcome():
        """Function that returns basic information about the API usage."""
        return welcome_message()

    @app.route("/transcribe", methods=["POST"])
    def transcribe_audio():
        """API endpoint to transcribe an audio file"""
        print("request.files", request.files)
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            transcription = Transcription()
            result = convert_to_wav(
                file, AUDIO_FILE_PATH, transcription.transcription_id
            )

            time.sleep(1)

            # access and store settings as json
            settings = json.loads(request.form["settings"])
            with open(
                os.getcwd() + SETTING_PATH + transcription.transcription_id + ".json",
                "w",
                encoding="utf-8",
            ) as json_file:
                json.dump(settings, json_file, indent=4)

            if result["success"] is True:
                transcriptions.append(transcription)
            else:
                transcription.status = TranscriptionStatusValue.ERROR
                transcription.error_message = result["message"]
            return jsonify(transcription.print_object())
        return "Something went wrong"

    @app.route("/get_transcription_status/<transcription_id>", methods=["GET"])
    def get_transcription_status_route(transcription_id):
        """API endpoint to get the status of a transcription"""
        # search for the transcription in RAM
        for transcription in transcriptions:
            if transcription.transcription_id == transcription_id:
                transcription.update_status()
                return jsonify(transcription.print_object())
        # search for the transcription in the file system
        try:
            new_transcription = search_undefined_transcripts(transcription_id)
            transcriptions.append(new_transcription)
            return jsonify(new_transcription.print_object())
        except TranscriptionNotFoundError as e:
            return e

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
