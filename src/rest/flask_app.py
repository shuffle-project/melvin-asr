"""Flask app to handle the REST API requests"""

import json
import logging
import time
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, make_response, request
from pydub import AudioSegment

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.types.transcription_status import TranscriptionStatus

LOGGER = logging.getLogger(__name__)
DATA_HANDLER = DataHandler()


def create_app(overwrite_api_key=None):
    """Function to create the Flask app"""

    app = Flask(__name__)
    config = CONFIG

    if overwrite_api_key is not None:
        config["api_keys"].append(overwrite_api_key)

    def require_api_key(func):
        """Decorator function to require an API key for a route"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("Authorization")

            if api_key and api_key in config["api_keys"]:
                return func(*args, **kwargs)

            LOGGER.warning("Unauthorized REST API request.")

            return (
                jsonify("Unauthorized"),
                401,
            )

        return wrapper

    @app.route("/")
    @require_api_key
    def show_config():
        """Function that returns the config of this service."""
        config_info = config.copy()
        # remove api_keys from config, as we don't want to show them
        config_info.pop("api_keys")
        return make_response(
            json.dumps(config_info, indent=4), 200, {"Content-Type": "application/json"}
        )

    @app.route("/health", methods=["GET"])
    @require_api_key
    def health_check():
        """return health status"""
        return make_response("OK", 200)

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

            except Exception as e:
                LOGGER.error(f"Error while reading status file {file_name}: {e}")
                DATA_HANDLER.delete_status_file(file_name)
        return make_response(
            jsonify(transcriptions), 200, {"Content-Type": "application/json"}
        )

    @app.route("/transcriptions/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_transcriptions_id(transcription_id):
        """API endpoint to get the status of a transcription"""
        file = DATA_HANDLER.get_status_file_by_id(transcription_id)
        if file:
            return make_response(file, 200, {"Content-Type": "application/json"})
        return make_response("Transcription ID not found", 404)

    @app.route("/transcriptions", methods=["POST"])
    @require_api_key
    def post_transcription():
        """API endpoint to transcribe an audio file"""
        try:
            if "file" not in request.files:
                return "No file posted", 400
            file = request.files["file"]
            if file:
                language = (
                    request.form["language"] if "language" in request.form else None
                )
                if language and language not in config["supported_language_codes"]:
                    return make_response(
                        jsonify(
                            {"message": "language code ({language}) is not supported"}
                        ),
                        400,
                        {"Content-Type": "application/json"},
                    )

                transcription_id = str(uuid.uuid4())
                result = DATA_HANDLER.save_audio_file(
                    AudioSegment.from_file(file.stream), transcription_id
                )
                if result["success"] is not True:
                    return make_response(
                        jsonify(result["message"]),
                        400,
                        {"Content-Type": "application/json"},
                    )

                # sleep to make sure that the file is saved before the transcription starts
                time.sleep(0.1)

                settings = None
                model = None
                if "settings" in request.form:
                    settings = json.loads(request.form["settings"])
                if "model" in request.form:
                    model = request.form["model"]

                task = request.form["task"] if "task" in request.form else "transcribe"

                text = request.form["text"] if "text" in request.form else None

                if task == "align":
                    if not text:
                        return make_response(
                            jsonify(
                                {"message": "property text is required for task align"}
                            ),
                            400,
                            {"Content-Type": "application/json"},
                        )
                    if not language:
                        return make_response(
                            jsonify(
                                {
                                    "message": "property language is required for task align"
                                }
                            ),
                            400,
                            {"Content-Type": "application/json"},
                        )

                data = {
                    "transcription_id": transcription_id,
                    "status": TranscriptionStatus.IN_QUERY.value,
                    "start_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "settings": settings,
                    "model": model,
                    "task": task,
                    "text": text,
                    "language": language,
                }

                DATA_HANDLER.write_status_file(transcription_id, data)
                return make_response(
                    jsonify(data), 200, {"Content-Type": "application/json"}
                )

        except Exception as e:
            LOGGER.error(f"Error while POST /transcriptions: {e}")
        return make_response("Something went wrong", 500)

    @app.route("/export/transcript/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_stream_transcript_export(transcription_id):
        """API endpoint to get the transcription and wav of a stream"""
        file = DATA_HANDLER.get_export_json_by_id(transcription_id)
        if file:
            return make_response(file, 200, {"Content-Type": "application/json"})
        return make_response("Transcription ID not found", 404)

    @app.route("/export/audio/<transcription_id>", methods=["GET"])
    @require_api_key
    def get_stream_audio_export(transcription_id):
        """API endpoint to get the transcription and wav of a stream"""
        file = DATA_HANDLER.get_audio_file_by_id(transcription_id)
        if file is not None:
            response = make_response(file)
            response.headers.set("Content-Type", "audio/wav")
            response.headers.set(
                "Content-Disposition", "attachment", filename=f"{transcription_id}.wav"
            )
            return response
        return jsonify({"error": "File not found"}), 404

    return app
