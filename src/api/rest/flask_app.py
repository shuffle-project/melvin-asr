"""Flask app to handle the REST API requests"""
import json
import time
import uuid
from datetime import datetime
from functools import wraps
from pydub import AudioSegment
from flask import Flask, jsonify, request, make_response
from src.helper.logger import Color, Logger
from src.config import CONFIG
from src.helper.types.transcription_status import (
    TranscriptionStatus,
)
from src.helper.data_handler import DataHandler

LOGGER = Logger("FlaskApp", False, Color.GREEN)
DATA_HANDLER = DataHandler()


def create_app(api_keys=CONFIG["api_keys"]):
    """Function to create the Flask app"""

    app = Flask(__name__)

    def require_api_key(func):
        """Decorator function to require an API key for a route"""

        
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("key")

            if api_key and api_key in api_keys:
                return func(*args, **kwargs)

            LOGGER.print_error(
                "Unauthorized REST API request. "
                + f"api_key: {api_key}, config_key: {api_keys}"
            )

            return (
                jsonify("Unauthorized"),
                401,
            )

        return wrapper

    @app.route("/")
    @require_api_key
    def show_config():
        """Function that returns the config of this service."""
        config_info = CONFIG.copy()
        # remove api_keys from config, as we don't want to show them
        config_info.pop("api_keys")
        return make_response(json.dumps(config_info, indent=4), 200, {"Content-Type": "application/json"})

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
                LOGGER.print_error(f"Error while reading status file {file_name}: {e}")
                DATA_HANDLER.delete_status_file(file_name)
        return make_response(jsonify(transcriptions), 200, {"Content-Type": "application/json"})

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
                transcription_id = str(uuid.uuid4())
                result = DATA_HANDLER.save_audio_file(
                    AudioSegment.from_file(file.stream), transcription_id
                )
                if result["success"] is not True:
                    return make_response(jsonify(result["message"]), 400, {"Content-Type": "application/json"})

                # sleep to make sure that the file is saved before the transcription starts
                time.sleep(0.1)

                settings = None
                model = None
                if "settings" in request.form:
                    settings = json.loads(request.form["settings"])
                if "model" in request.form:
                    model = request.form["model"]

                data = {
                    "transcription_id": transcription_id,
                    "status": TranscriptionStatus.IN_QUERY.value,
                    "start_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "settings": settings,
                    "model": model,
                }

                DATA_HANDLER.write_status_file(transcription_id, data)
                return make_response(jsonify(data), 200, {"Content-Type": "application/json"})

        except Exception as e:
            LOGGER.print_error(f"Error while POST /transcriptions: {e}")
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
            response.headers.set('Content-Type', 'audio/wav')
            response.headers.set('Content-Disposition', 'attachment', filename=f"{transcription_id}.wav")
            return response
        return jsonify({"error": "File not found"}), 404


    return app
