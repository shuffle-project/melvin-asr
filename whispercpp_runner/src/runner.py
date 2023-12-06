""" This module contains the handler for the transcription process. """
import time
import os
from datetime import datetime
import json
# pylint: disable=C0301
from runner_config import AUDIO_FILE_PATH, AUDIO_FILE_FORMAT, MODEL_PATH_FROM_ROOT, WHISPER_CPP_PATH, WHISPER_MODELS, \
    FALLBACK_MODEL, STATUS_PATH, TRANSCRIPT_PATH
from binding.transcribe_to_json import transcribe_to_json


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, ident: int, model: str):
        """Constructor of the Runner class."""
        self.ident = ident
        if model in WHISPER_MODELS:
            print("RUNNER: Model is valid, running " + model + ".")
            self.model = model
        else:
            print("RUNNER: Model is not valid, fallback to " + FALLBACK_MODEL + ".")
            self.model = FALLBACK_MODEL

    # pylint: disable=W0718
    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        while True:
            transcription_id = self.get_oldest_audio_file()
            if transcription_id == "None":
                print("No files to process.")
                time.sleep(3)
                continue
            print("Processing file: " + transcription_id)
            try:
                self.run_whisper(transcription_id)
            except Exception as e:
                print("Error running whisper: " + str(e))
                self.update_status_file("error", str(e))
                continue

            os.remove(os.getcwd() + AUDIO_FILE_PATH + transcription_id + AUDIO_FILE_FORMAT)
            self.merge_transcript_to_status(transcription_id)

    def get_oldest_audio_file(
            self, directory=STATUS_PATH
    ) -> str:
        """Gets the oldest .wav file from the audio_files directory."""
        full_dir = os.getcwd() + directory

        files = os.listdir(full_dir)

        status_files = list(files)
        if len(status_files) == 0:
            return "None"

        return self.get_oldest_transcription_in_query(full_dir)

    def get_oldest_transcription_in_query(self, folder_path) -> str:
        """Gets the oldest transcription in query."""
        oldest_start_time = None
        oldest_transcription_id = None

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding="utf-8") as file:
                    data = json.load(file)
                    current_status = data.get('status')
                    if current_status == "in_query":
                        current_start_time = data.get('start_time')
                        if current_start_time:
                            current_datetime = datetime.fromisoformat(current_start_time.replace('Z', '+00:00'))
                            if oldest_start_time is None or current_datetime < oldest_start_time:
                                oldest_start_time = current_datetime
                                oldest_transcription_id = data.get('transcription_id')

        if oldest_transcription_id:
            return oldest_transcription_id
        return "None"

    def run_whisper(self, transcription_id: str) -> None:
        """Runs whisper"""

        self.update_status_file("in_progress", transcription_id)

        audio_file_name = f"{transcription_id}{AUDIO_FILE_FORMAT}"

        print("Running whisper on file: " + audio_file_name)

        transcribe_to_json(
            main_path=WHISPER_CPP_PATH,
            model_path=MODEL_PATH_FROM_ROOT + f"ggml-{self.model}.bin",
            audio_file_path=AUDIO_FILE_PATH + audio_file_name,
            output_file="/data/transcripts/" + audio_file_name,
            debug=True,
        )

    def update_status_file(self, status: str, transcription_id: str, status_file_path: str = STATUS_PATH, error_message: str = None):
        """Updates the status file of the transcription."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(status_file_path, file_name)

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)
                data['status'] = status
                if status == "done":
                    data['end_time'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                if error_message is not None:
                    data['error_message'] = error_message

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
                print(f"Status updated for {transcription_id} to {status}")
        else:
            print(f"File for transcription ID {transcription_id} not found.")

    def merge_transcript_to_status(self, transcription_id: str):
        """Merges the transcript file to the status file."""
        transcript_file_name = f"{transcription_id}{AUDIO_FILE_FORMAT}.json"
        status_file_name = f"{transcription_id}.json"

        transcript_file_path = os.path.join(TRANSCRIPT_PATH, transcript_file_name)
        status_file_path = os.path.join(STATUS_PATH, status_file_name)

        if os.path.exists(transcript_file_path) and os.path.exists(status_file_path):
            with open(transcript_file_path, 'r', encoding="utf-8") as transcript_file:
                transcript_data = json.load(transcript_file)

            with open(status_file_path, 'r', encoding="utf-8") as status_file:
                status_data = json.load(status_file)
                status_data['transcript'] = transcript_data  # Merge transcript data into status JSON

            with open(status_file_path, 'w', encoding="utf-8") as status_file:
                json.dump(status_data, status_file, indent=4)
                print(f"Transcript merged into {status_file_name}")

            os.remove(transcript_file_path)  # Delete the transcript file
            print(f"{transcript_file_name} deleted.")
            self.update_status_file("done", transcription_id)
        else:
            print(f"Transcript or Status file for {transcription_id} not found.")
            self.update_status_file("error", transcription_id, STATUS_PATH, "Transcript file not found.")
