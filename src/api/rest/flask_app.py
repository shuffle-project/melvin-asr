"""Flask app to handle the REST API requests"""
import json
import os
import time
import uuid
from functools import wraps
from pydub import AudioSegment
from flask import Flask, jsonify, request
from src.config import CONFIG
from src.helper.convert_save_received_audio_files import convert_to_wav
from src.helper.transcription_request_handling.transcription import (
    Transcription,
    TranscriptionNotFoundError,
    TranscriptionRunnerType,
    TranscriptionStatusValue,
)
from src.helper.welcome_message import welcome_message


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
            print(api_key)
            print(request.headers)
            return (
                jsonify({"error": "Unauthorized. Please provide a valid API key"}),
                401,
            )

        return wrapper

    @app.route("/")
    def welcome():
        """Function that returns basic information about the API usage."""
        return welcome_message()

    # API endpoint to get all transcriptions and their status in a list
    @app.route("/transcriptions", methods=["GET"])
    @require_api_key
    def get_transcriptions():
        status_files = list(os.listdir(CONFIG["STATUS_PATH"]))
        transcriptions = []
        for file_name in status_files:
            with open(
                os.path.join(CONFIG["STATUS_PATH"], file_name), "r", encoding="utf-8"
            ) as file:
                data = json.load(file)
                transcription_id = data.get("transcription_id")
                status = data.get("status")
                transcriptions.append(
                    {"transcription_id": transcription_id, "status": status}
                )

        return jsonify(transcriptions)

    @app.route("/transcriptions", methods=["POST"])
    @require_api_key
    def transcribe_audio():
        """API endpoint to transcribe an audio file"""
        print("request.files", request.files)
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            transcription = Transcription(uuid.uuid4(), TranscriptionRunnerType.REST)
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

    @app.route("/transcriptions/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_transcription_status_route(transcription_id):
        """API endpoint to get the status of a transcription"""
        try:
            file_path = os.path.join(
                os.getcwd() + CONFIG["STATUS_PATH"], f"{transcription_id}.json"
            )
            print("file_path", file_path)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    return jsonify(json.load(file))
            else:
                print("TranscriptionNotFoundError")
                raise TranscriptionNotFoundError(transcription_id)
        except TranscriptionNotFoundError as e:
            return jsonify(str(e)), 404

    @app.route("/health", methods=["GET"])
    def health_check():
        """return health status"""
        print("health check")
        return "OK"

    return app
