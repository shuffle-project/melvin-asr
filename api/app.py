"""Module is starting the models and handling queued requests"""
from whispercpp_binding.transcribe_to_json import transcript_to_json
from transcription_handler import *
from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
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



@app.route("/")
def hello_world():
    """Function that returns the string 'Hello, World!'"""
    return "Hello, World!"

# API-Endpunkt für die Transkription von Audiodateien über HTTP
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    return handle_transcription_request()

@app.route('/get_transcription_status/<transcription_id>', methods=['GET'])
def get_transcription_status_route(transcription_id):
    return get_transcription_status(transcription_id)

# API-Endpunkt für die Transkription von Streaming Audio über Websockets
@app.route("/stream_transcribe", methods=["POST"])
def stream_transcribe():
    """transcribes an audio stream"""

