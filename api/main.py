"""Module is starting the models and handling queued requests"""
from whispercpp_binding.transcribe_to_json import transcript_to_json


def main() -> None:
    """Loop to handle request queue"""
    results = transcript_to_json(
        main_path="/whisper.cpp/main",
        model_path="/whisper.cpp/models/ggml-small.bin",
        audio_file_path="/whisper.cpp/samples/jfk.wav",
        output_file="/data/main",
        debug=True
    )
    print(results)

main()