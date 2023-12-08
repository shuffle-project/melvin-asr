"""This class handles the transcription configuration of the websockets server."""

class WebsocketsTranscriptionsConfig:

    def __init__(self):
        # Config used by vosk server (https://github.com/alphacep/vosk-server/blob/master/websocket/asr_server.py)
        self.phrase_list = []
        self.sample_rate = 16000
        self.model = None
        self.words = False
        self.max_alternatives = 1


