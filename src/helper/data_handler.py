"""This module works as Interface for the access to the data folder."""
from json import JSONDecodeError
import os
from datetime import datetime
from src.helper.transcription import TranscriptionStatusValue
from src.config import CONFIG
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
        self.status_path = self.root_path + CONFIG["STATUS_PATH"]
        self.audio_file_path = self.root_path + CONFIG["AUDIO_FILE_PATH"]
        self.audio_file_format = CONFIG["AUDIO_FILE_FORMAT"]

    def get_status_file_by_id(self, transcription_id: str) -> dict:
        """Returns the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path + file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            return data
        return None

    def write_status_file(self, transcription_id: str, data: dict) -> None:
        """Writes the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path + file_name)
        self.file_handler.write_json(file_path, data)

    def get_audio_file_path_by_id(self, transcription_id: str) -> str:
        """Returns the audio file path by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path + file_name)
        if os.path.isfile(file_path):
            return file_path
        return None

    def update_status_file(
        self, status: str, transcription_id: str, error_message: str = None
    ):
        """Updates the status file with the given status."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            data["status"] = status
            if status == TranscriptionStatusValue.FINISHED.value:
                data["end_time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            if error_message is not None:
                data["error_message"] = error_message
            self.file_handler.write_json(file_path, data)
            self.log.print_log(f"Status file {file_name} updated (status: {status})")
        else:
            self.log.print_error(
                f"File for transcription ID {transcription_id} not found, PATH: {self.status_path}"
            )

    def merge_transcript_to_status(
        self, transcription_id: str, transcript_data: dict
    ) -> None:
        """Merges the transcript file to the status file."""
        status_data = self.get_status_file_by_id(transcription_id)
        if transcript_data and status_data:
            status_data["transcript"] = transcript_data
            self.write_status_file(transcription_id, status_data)
            self.log.print_log(f"Transcript added for {transcription_id}")
            self.update_status_file(
                TranscriptionStatusValue.FINISHED.value, transcription_id
            )
        else:
            self.log.print_error(
                f"Transcript or Status file for {transcription_id} not found."
            )
            self.update_status_file(
                TranscriptionStatusValue.ERROR.value,
                transcription_id,
                "Transcript file not found.",
            )

    def get_oldest_status_file_in_query(self) -> str:
        """Gets the oldest transcription in query."""
        oldest_start_time = None
        oldest_transcription_id: str = None

        for filename in os.listdir(self.status_path):
            try:
                if filename.endswith(".json"):
                    data = self.file_handler.read_json(
                        os.path.join(self.status_path, filename)
                    )
                    current_status = data.get("status")
                    current_datetime = datetime.fromisoformat(
                        data.get("start_time").replace("Z", "+00:00")
                    )
                    if current_status != "in_query":
                        continue
                    if (
                        oldest_start_time is None
                        or current_datetime < oldest_start_time
                    ):
                        oldest_start_time = current_datetime
                        oldest_transcription_id = data.get("transcription_id")

            # Catch unreadable JSON files and delete them
            except JSONDecodeError as jde:
                self.log.print_error(
                    f"Caught JSONDecodeError getting oldest status file: {str(jde)}"
                )
                self.file_handler.delete(os.path.join(self.status_path, filename))
                continue

            # need to catch all exceptions here to not break the loop in runner.py
            # pylint: disable=W0718
            except Exception as e:
                self.log.print_error(
                    f"Caught Exception of type {type(e).__name__}" +
                    f"while getting oldest status file: {str(e)}"
                )
                continue

        if oldest_transcription_id:
            return oldest_transcription_id
        return "None"

    def clean_up_status_files(self, max_old_status_files: int = 100):
        """Deletes the oldest status files with
        current_status=TranscriptionStatusValue.FINISHED or TranscriptionStatusValue.ERROR
        if there are more than set in CONFIG MAX_OLD_STATUS_FILES number."""
        cleanup_files = []
        for filename in os.listdir(self.status_path):
            if filename.endswith(".json"):
                data = self.file_handler.read_json(
                    os.path.join(self.status_path, filename)
                )
                current_status = data.get("status")
                if current_status in (
                    TranscriptionStatusValue.FINISHED.value,
                    TranscriptionStatusValue.ERROR.value,
                ):
                    cleanup_files.append((filename, data.get("start_time")))

        if len(cleanup_files) > max_old_status_files:
            cleanup_files.sort(
                key=lambda x: datetime.fromisoformat(x[1].replace("Z", "+00:00"))
            )
            for i in range(len(cleanup_files) - max_old_status_files):
                file_to_delete = cleanup_files[i][0]
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

    def delete_audio_file(self, transcription_id: str) -> None:
        """Deletes the audio file by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            self.log.print_log(f"Audio file {file_name} deleted.")
        else:
            self.log.print_error(f"Audio file {file_name} not found.")
