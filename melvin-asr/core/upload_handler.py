import os
import uuid
from datetime import datetime
from typing import List

from models.upload import UploadResponse
from pydub import AudioSegment

from .paths import upload_path


class UploadHandler():
    def __init__(self):
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

    def get_file_path(self, filename: str) -> str:
        return os.path.join(upload_path, filename)
    
    def list_files(self) -> List[str]:
        files = []
        for filename in os.listdir(upload_path):
            file_path = self.get_file_path(filename)
            if os.path.isfile(file_path) and file_path.endswith(".wav"):
                files.append(filename)
        return files
    
    def get_file_created_at(self, filename: str) -> datetime:
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            return datetime.fromtimestamp(os.path.getctime(file_path))
        return datetime.fromtimestamp(0.0)

    def file_exists(self, filename: str) -> bool:
        file_path = self.get_file_path(filename)
        return os.path.exists(file_path)

    def create_audio_file(self, audio: AudioSegment) -> UploadResponse:
        filename = f"{uuid.uuid4()}.wav"
        audio.set_frame_rate(16000).set_channels(1).export(self.get_file_path(filename))
        return UploadResponse(filename=filename)

    def remove_file(self, filename: str):
        if self.file_exists(filename):
            file_path = self.get_file_path(filename)
            os.remove(file_path)
            return True
        return False
    
upload_handler = UploadHandler()