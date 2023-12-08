"""This class handles the transcription configuration of the websockets server."""

class WebsocketsTranscriptionsConfig:

    def __init__(self):
        # Config used by vosk server (https://github.com/alphacep/vosk-server/blob/master/websocket/asr_server.py)
        self.phrase_list = []
        self.sample_rate = 16000
        self.model = None
        self.words = False
        self.max_alternatives = 1
    
    def get_settings(self):
        """Function to get the settings"""
        return {
            "phrase_list": self.phrase_list,
            "sample_rate": self.sample_rate,
            "model": self.model,
            "words": self.words,
            "max_alternatives": self.max_alternatives
        }


