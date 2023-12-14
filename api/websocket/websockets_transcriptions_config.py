"""This class handles the transcription configuration of the websockets server."""


class WebsocketsTranscriptionsConfig:
    """This class handles the transcription configuration of the websockets server."""

    def __init__(self):
        self.language = "auto"
        self.translate = True
        self.split_on_word = True
        self.max_len = 1

    def get_settings(self):
        """Function to get the settings"""
        return {
            "language": self.language,
            "translate": self.translate,
            "split_on_word": self.split_on_word,
            "max_len": self.max_len,
        }
