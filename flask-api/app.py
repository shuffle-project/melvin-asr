from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# API-Endpunkt für die Transkription von Audiodateien über HTTP
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    pass

# API-Endpunkt für die Transkription von Streaming Audio über Websockets
@app.route('/stream_transcribe', methods=['POST'])
def stream_transcribe():
    pass

#if __name__ == '__main__':
#    app.run()
