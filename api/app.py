"""
This module contains the Flask app and the API endpoints.
"""
from flask import Flask, request, jsonify
from whispercpp_binding.transcribe_to_json import transcript_to_json
from src.transcription_handling.transcription_model import (
    Transcription,
    TranscriptionStatusValue,
)
from src.helper.convert_save_received_audio_files import convert_to_wav

# from src.transcription_handling.transcription_handler import (
#     get_transcription_status,
#     handle_transcription_request,
# )

app = Flask(__name__)
transcriptions: [Transcription] = []

if __name__ == "__main__":
    app.run()


def main() -> None:
    """Loop to handle request queue"""
    results = transcript_to_json(
        main_path="/whisper.cpp/main",
        model_path="/whisper.cpp/models/ggml-small.bin",
        audio_file_path="/whisper.cpp/samples/jfk.wav",
        output_file="/data/main",
        debug=True,
    )
    print(results)


# main()


# Base endpoint with API usage information
@app.route("/")
def welcome():
    """Function that returns information about the API usage."""
    api_info = """
Welcome to the Transcription API!

Here are the available endpoints:

1. `/transcribe` (POST): Transcribe audio files over HTTP.
   Example: curl -X POST http://your-server-address/transcribe -H "Content-Type: audio/*" --data-binary @your-audio-file.mp3

2. `/get_transcription_status/<transcription_id>` (GET): Get transcription status for a given transcription ID.
   Example: curl http://your-server-address/get_transcription_status/your-transcription-id

3. `/stream_transcribe` (POST): Transcribe streaming audio over Websockets.
   Example: Implement WebSocket connection and send audio data. (Work in progress)

Feel free to explore and use these endpoints for your transcription needs!
"""

    return api_info


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """API endpoint to transcribe an audio file"""
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file:
        transcription = Transcription()
        result = convert_to_wav(
            file, "data/audio_files", transcription.transcription_id
        )
        if result["success"] is True:
            transcriptions.append(transcription)
        else:
            transcription.status = TranscriptionStatusValue.ERROR
            transcription.error_message = result["message"]
        return jsonify(transcription.print_object())


@app.route("/get_transcription_status/<transcription_id>", methods=["GET"])
def get_transcription_status_route(transcription_id):
    """API endpoint to get the status of a transcription"""
    for transcription in transcriptions:
        if transcription.transcription_id == transcription_id:
            return jsonify(transcription.print_object())
        return "Could not get transcription_id {transcription_id}"


# @app.route("/stream_transcribe", methods=["POST"])
# def stream_transcribe():
#     """transcribes an audio stream"""
