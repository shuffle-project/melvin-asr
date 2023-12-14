"""This class handles the transcription configuration of the websockets server."""


class WebsocketsTranscriptionsConfig:
    """This class handles the transcription configuration of the websockets server."""

    def __init__(self):
        self.language = "auto"

    def get_settings(self):
        """Function to get the settings"""
        return {
            "language": self.language,
        }
