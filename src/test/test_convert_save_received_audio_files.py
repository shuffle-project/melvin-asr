""" tests api/src/helper/convert_save_received_audio_files.py """
import unittest
import io
import os
from pydub import AudioSegment

from src.helper.convert_save_received_audio_files import convert_to_wav


class TestConvertTestAudio(unittest.TestCase):
    """Test cases for the convert_to_wav function."""

    def setUp(self):
        # This method will run before each test
        self.output_directory = "/" + os.getcwd() + "/api/test/outdir"
        self.output_filename = "converted_audio"
        self.output_file = os.path.join(
            self.output_directory, self.output_filename + ".wav"
        )

        # Create a test directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def test_convert_to_wav_success(self):
        """Tests if the convert_to_wav function successfully converts an audio file."""
        simulated_audio_file = io.BytesIO()
        AudioSegment.silent(duration=1000).export(simulated_audio_file, format="mp3")
        simulated_audio_file.seek(0)

        # Convert FileStorage to AudioSegment
        audio_file_storage = AudioSegment.from_file(simulated_audio_file, format="mp3")

        result = convert_to_wav(
            audio_file_storage, self.output_directory, self.output_filename
        )

        self.assertEqual(
            result,
            {"success": True, "message": "Data converted successfully"},
            "The function did not return the expected message.",
        )

        self.assertTrue(
            os.path.exists(self.output_file), "The WAV file was not created."
        )

        converted_audio = AudioSegment.from_file(self.output_file)
        self.assertEqual(
            converted_audio.frame_rate, 16000, "The frame rate is not 16kHz."
        )
        self.assertEqual(converted_audio.channels, 1, "The audio is not mono.")

    def tearDown(self):
        # This method will run after each test
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists(self.output_directory):
            os.rmdir(self.output_directory)


if __name__ == "__main__":
    unittest.main()
