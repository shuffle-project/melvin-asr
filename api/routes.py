"""Module providing a function printing python version."""
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    """Function that returns the string 'Hello, World!'"""
    return "Hello, World!"


# API-Endpunkt für die Transkription von Audiodateien über HTTP
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """returns a transcription of an audio file"""


# API-Endpunkt für die Transkription von Streaming Audio über Websockets
@app.route("/stream_transcribe", methods=["POST"])
def stream_transcribe():
    """transcribes an audio stream"""


# if __name__ == '__main__':
#    app.run()
