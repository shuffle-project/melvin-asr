"""Welcome message for the API."""


def welcome_message() -> str:
    """Function that returns information about the API usage."""
    return """
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
