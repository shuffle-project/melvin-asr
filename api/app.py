"""
This module contains the Flask app and the API endpoints.
"""
import json
import os
import time
from flask import Flask, request, jsonify
from CONFIG import AUDIO_FILE_PATH, SETTING_PATH
from src.helper.welcome_message import welcome_message
from src.transcription_request_handling.transcription import (
    Transcription,
    TranscriptionStatusValue,
)
from src.helper.convert_save_received_audio_files import convert_to_wav

app = Flask(__name__)
transcriptions: [Transcription] = []

if __name__ == "__main__":
    app.run(debug=True, port=5000)

# Base endpoint with API usage information
@app.route("/")
def welcome():
    """Function that returns basic information about the API usage."""
    return welcome_message()


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """API endpoint to transcribe an audio file"""
    # access and store audio file as wav
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

        time.sleep(3)

        # access and store settings as json
        settings = json.loads(request.form["settings"])
        with open(os.getcwd() + SETTING_PATH + transcription.transcription_id + ".json", "w", encoding="utf-8") as json_file:
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
    error_message = jsonify(f"Could not get transcription of id {transcription_id}")
    if len(transcriptions) == 0:
        return error_message
    for transcription in transcriptions:
        if transcription.transcription_id == transcription_id:
            transcription.update_status()
            return jsonify(transcription.print_object())
        # else create transcription object
        return error_message


# @app.route("/stream_transcribe", methods=["POST"])
# def stream_transcribe():
#     """transcribes an audio stream"""
