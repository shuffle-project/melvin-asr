"""This handles the transcription configuration of the websockets server."""


def default_websocket_settings():
    """Function to get the settings for the websockets server"""
    return {
        "word_timestamps": True,
    }
