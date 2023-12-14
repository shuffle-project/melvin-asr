"""This module contains the DataHandler class to access the data folder easily."""
import os
from datetime import datetime
from runner_config import (
    MAX_DONE_FILES,
    AUDIO_FILE_FORMAT,
    STATUS_PATH,
    TRANSCRIPT_PATH,
)
from src.helper.file_handler import FileHandler
from src.helper.logger import Color, Logger

# Need this many instance attributes to fulfill business requirements
# pylint: disable=R0902
class DataHandler:
    """This class handles the data folder."""

    def __init__(self):
        self.log = Logger("DataHandler", False, Color.GREEN)
        self.root_path = os.getcwd()
        self.data_folder = os.path.join(self.root_path, "data")
        self.file_handler = FileHandler()

        # get config settings
        self.status_path = self.root_path + STATUS_PATH
        self.transcript_path = self.root_path + TRANSCRIPT_PATH
        self.audio_file_format = AUDIO_FILE_FORMAT
        self.max_done_files = MAX_DONE_FILES

    def update_status_file(
        self, status: str, transcription_id: str, error_message: str = None
    ):
        """Updates the status file with the given status."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            data["status"] = status
            if status == "done":
                data["end_time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            if error_message is not None:
                data["error_message"] = error_message
            self.file_handler.write_json(file_path, data)
            self.log.print_log(f"Status file {file_name} updated (status: {status})")
        else:
            self.log.print_error(
                f"File for transcription ID {transcription_id} not found, PATH: {self.status_path}"
            )

    def merge_transcript_to_status(self, transcription_id: str):
        """Merges the transcript file to the status file."""
        transcript_file_name = f"{transcription_id}{AUDIO_FILE_FORMAT}.json"
        status_file_name = f"{transcription_id}.json"

        transcript_file_path = os.path.join(self.transcript_path, transcript_file_name)
        status_file_path = os.path.join(self.status_path, status_file_name)

        transcript_data = self.file_handler.read_json(transcript_file_path)
        status_data = self.file_handler.read_json(status_file_path)

        if transcript_data and status_data:
            status_data["transcript"] = transcript_data
            self.file_handler.write_json(status_file_path, status_data)
            self.log.print_log(f"Transcript merged into {status_file_name}")

            self.file_handler.delete(transcript_file_path)
            self.log.print_log(f"{transcript_file_name} deleted.")

            self.update_status_file("done", transcription_id)
        else:
            self.log.print_error(
                f"Transcript or Status file for {transcription_id} not found."
            )
            self.update_status_file(
                "error", transcription_id, "Transcript file not found."
            )

    def get_oldest_status_file_in_query(self) -> str:
        """Gets the oldest transcription in query."""
        oldest_start_time = None
        oldest_transcription_id: str = None

        for filename in os.listdir(self.status_path):
            if filename.endswith(".json"):
                data = self.file_handler.read_json(
                    os.path.join(self.status_path, filename)
                )
                current_status = data.get("status")
                if current_status == "in_query":
                    current_start_time = data.get("start_time")
                    if current_start_time:
                        current_datetime = datetime.fromisoformat(
                            current_start_time.replace("Z", "+00:00")
                        )
                        if (
                            oldest_start_time is None
                            or current_datetime < oldest_start_time
                        ):
                            oldest_start_time = current_datetime
                            oldest_transcription_id = data.get("transcription_id")

        if oldest_transcription_id:
            return oldest_transcription_id
        return "None"

    def delete_oldest_done_status_files(self):
        """Deletes the oldest status files with current_status="done"
        if there are more than set in CONFIG MAX_DONE_FILES number."""
        done_files = []
        for filename in os.listdir(self.status_path):
            if filename.endswith(".json"):
                data = self.file_handler.read_json(
                    os.path.join(self.status_path, filename)
                )
                current_status = data.get("status")
                if current_status == "done":
                    done_files.append((filename, data.get("start_time")))

        if len(done_files) > self.max_done_files:
            done_files.sort(
                key=lambda x: datetime.fromisoformat(x[1].replace("Z", "+00:00"))
            )
            for i in range(len(done_files) - self.max_done_files):
                file_to_delete = done_files[i][0]
                os.remove(os.path.join(self.status_path, file_to_delete))

    def get_status_file_settings(self, transcription_id: str) -> dict:
        """Returns the settings from the status file."""
        try:
            file_name = f"{transcription_id}.json"
            file_path = os.path.join(self.status_path, file_name)
            data = self.file_handler.read_json(file_path)
            if data and "settings" in data:
                return data.get("settings")
        # need to catch all exceptions here to not break the loop in runner.py
        # pylint: disable=W0703
        except Exception as e:
            self.log.print_error(
                f"Error getting settings from status file: {str(e)}" + e
            )
        return None
