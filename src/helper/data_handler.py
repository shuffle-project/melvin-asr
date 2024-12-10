"""This module works as Interface for the access to the data folder."""

import io
import json
import logging
import os
import time
from datetime import datetime, timezone

from pydub import AudioSegment

from src.helper.config import CONFIG
from src.helper.file_handler import FileHandler
from src.helper.types.transcription_status import TranscriptionStatus


class DataHandler:
    """This class handles the data folder."""

    def __init__(
        self,
        status_path: str = CONFIG["status_file_path"],
        audio_file_path: str = CONFIG["audio_file_path"],
        audio_file_format: str = CONFIG["audio_file_format"],
        export_file_path: str = CONFIG["export_file_path"],
    ):
        self.log = logging.getLogger(__name__)
        self.root_path = os.getcwd()
        self.file_handler = FileHandler()

        self.status_path = self.root_path + status_path
        self.audio_file_path = self.root_path + audio_file_path
        self.audio_file_format = audio_file_format
        self.export_file_path = self.root_path + export_file_path

    def get_status_file_by_id(self, transcription_id: str) -> dict:
        """Returns the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path + file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            return data
        return None

    def get_all_status_filenames(self) -> list[str]:
        """Returns all status files."""
        status_files = []
        for filename in os.listdir(self.status_path):
            if filename.endswith(".json"):
                status_files.append(filename)
        return status_files

    def write_status_file(self, transcription_id: str, data: dict) -> None:
        """Writes the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.file_handler.write_json(file_path, data)

    def delete_status_file(self, transcription_id: str) -> bool:
        """Deletes the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        self.log.error(f"Status file {file_name} not found.")
        return False

    def get_audio_file_path_by_id(self, transcription_id: str) -> str:
        """Returns the audio file path by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path + file_name)
        if os.path.isfile(file_path):
            return file_path
        return None

    def update_status_file(
        self, status: str, transcription_id: str, error_message: str = None
    ) -> None:
        """Updates the status file with the given status."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            data["status"] = status
            if status == TranscriptionStatus.FINISHED.value:
                data["end_time"] = (
                    datetime.now(timezone.utc).replace(microsecond=0).isoformat()
                )
            if error_message is not None:
                data["error_message"] = error_message
            self.file_handler.write_json(file_path, data)
            self.log.info(f"Status file {file_name} updated (status: {status})")
        else:
            self.log.error(
                f"File for transcription ID {transcription_id} not found, PATH: {self.status_path}"
            )

    def merge_transcript_to_status(
        self, transcription_id: str, transcript_data: dict
    ) -> bool:
        """Merges the transcript file to the status file."""
        status_data = self.get_status_file_by_id(transcription_id)
        if transcript_data and status_data:
            status_data["transcript"] = transcript_data
            self.write_status_file(transcription_id, status_data)
            self.log.info(f"Transcript added for {transcription_id}")
            self.update_status_file(
                TranscriptionStatus.FINISHED.value, transcription_id
            )
            return True
        self.log.error(f"Transcript or Status file for {transcription_id} not found.")
        return False

    def clean_up_audio_and_status_files(
        self, keep_data_for_hours: int = CONFIG["keep_data_for_hours"]
    ) -> None:
        """Deletes status and audio files that are older than the keep_data_for_hours."""
        try:
            for filename in os.listdir(self.status_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.status_path, filename)
                    file_time = os.path.getmtime(file_path)
                    # 3600 seconds in an hour
                    if (time.time() - file_time) / 3600 > keep_data_for_hours:
                        os.remove(file_path)
                        self.log.debug(f"Deleted status file {filename}")
            for filename in os.listdir(self.audio_file_path):
                if filename.endswith(CONFIG["audio_file_format"]):
                    file_path = os.path.join(self.audio_file_path, filename)
                    file_time = os.path.getmtime(file_path)
                    # 3600 seconds in an hour
                    if (time.time() - file_time) / 3600 > keep_data_for_hours:
                        os.remove(file_path)
                        self.log.debug(f"Deleted audio file {filename}")
            for filename in os.listdir(self.export_file_path):
                if filename.endswith(".json") or filename.endswith(
                    CONFIG["audio_file_format"]
                ):
                    file_path = os.path.join(self.export_file_path, filename)
                    file_time = os.path.getmtime(file_path)
                    # 3600 seconds in an hour
                    if (time.time() - file_time) / 3600 > keep_data_for_hours:
                        os.remove(file_path)
                        self.log.debug(f"Deleted export file {filename}")

        except Exception as e:
            self.log.error(f"Error while cleaning up files: {str(e)}")

    def get_status_file_settings(self, transcription_id: str) -> dict:
        """Returns the settings from the status file."""
        try:
            file_name = f"{transcription_id}.json"
            file_path = os.path.join(self.status_path, file_name)
            data = self.file_handler.read_json(file_path)
            if data and "settings" in data:
                return data.get("settings")
        except Exception as e:
            self.log.error(f"Error getting settings from status file: {str(e)}" + e)
        return None

    def save_audio_file(self, audio, transcription_id) -> dict:
        """
        Convert an audio file to 16kHz mono WAV format and save it to a directory.
        """
        try:
            os.makedirs(self.audio_file_path, exist_ok=True)
            audio.set_frame_rate(16000).set_channels(1).export(
                os.path.join(
                    self.audio_file_path, f"{transcription_id}{self.audio_file_format}"
                )
            )
            return {"success": True, "message": "Conversion successful."}
        except Exception as e:
            error_message = f"Audio File creation failed for: {str(e)}"
            self.log.error(error_message)
            return {"success": False, "message": error_message}

    def delete_audio_file(self, transcription_id: str) -> bool:
        """Deletes the audio file by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        self.log.error(f"Audio file {file_name} not found.")
        return False

    def get_number_of_audio_files(self) -> int:
        """
        Returns the number of audio files
        with the config audio file format and
        in the config audio file path.
        """
        audio_files = [
            f
            for f in os.listdir(self.audio_file_path)
            if f.endswith(CONFIG["audio_file_format"])
        ]
        return len(audio_files)

    def export_wav_file(self, audio_chunk: bytes, name: str) -> str:
        """Exports a WAV file from an audio chunk to the export folder with a given base name."""
        file_name = f"{name}.wav"
        export_path = os.path.join(self.export_file_path, file_name)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        # Assuming audio_chunk is raw audio data, create an AudioSegment
        audio_segment = AudioSegment(
            data=audio_chunk,
            sample_width=2,  # Assuming 16-bit PCM
            frame_rate=16000,
            channels=1,
        )

        # Export the AudioSegment as a WAV file
        with open(export_path, "wb") as out_f:
            audio_segment.export(out_f, format="wav")

        self.log.debug(f"WAV file exported: {export_path}")
        return export_path

    def export_dict_to_json_file(self, data: dict, name: str) -> str:
        """Exports a dictionary to a JSON file in the export folder with a given base name."""
        file_name = f"{name}.json"
        export_path = os.path.join(self.export_file_path, file_name)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        self.log.debug(f"JSON file exported: {export_path}")
        return export_path

    def get_export_json_by_id(self, transcription_id: str) -> dict:
        """Returns the export json-file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.export_file_path + file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            return data
        return None

    def get_audio_file_by_id(self, transcription_id: str) -> bytes:
        """Returns the audio file data as bytes by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.export_file_path, file_name)
        if os.path.isfile(file_path):
            audio = AudioSegment.from_file(file_path)
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            return buffer.getvalue()
        return None
