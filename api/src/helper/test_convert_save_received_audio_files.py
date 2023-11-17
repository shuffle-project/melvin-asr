""" tests convert_save_received_audio_files.py functions"""
import unittest
import io
import os
from pydub import AudioSegment
from werkzeug.datastructures import FileStorage
from convert_save_received_audio_files import (
    convert_to_wav,
)  # make sure to import your function


class TestConvertTestAudio(unittest.TestCase):
    """covers all testing function"""

    def test_convert_to_wav_success(self):
        """tests convert_to_wav  function"""
        # Create an in-memory byte-stream to simulate a file
        simulated_audio_file = io.BytesIO()
        AudioSegment.silent(duration=1000).export(simulated_audio_file, format="mp3")
        simulated_audio_file.seek(0)  # Go to the start of the stream

        # Create a FileStorage object
        audio_file_storage = FileStorage(
            stream=simulated_audio_file,
            filename="test_audio.mp3",
            content_type="audio/mp3",
        )

        # Define the output directory and filename
        output_directory = "src/helper/"
        output_filename = "converted_audio"
        output = output_directory + output_filename + ".wav"

        # Call the function under test
        result_message = convert_to_wav(
            audio_file_storage, output_directory, output_filename
        )

        self.assertEqual(
            result_message, {'success': True, 'message': 'Data converted successfully'}, "The function did not return the expected message."
        )

        # Check that the output file was created and is a valid WAV file
        self.assertTrue(os.path.exists(output_directory), "The WAV file was not created.")

        # Additional checks can be performed such as file content analysis, duration, etc.
        converted_audio = AudioSegment.from_file(output)
        self.assertEqual(
            converted_audio.frame_rate, 16000, "The frame rate is not 16kHz."
        )
        self.assertEqual(converted_audio.channels, 1, "The audio is not mono.")

        # Clean up the created file after the test
        os.remove(output)


if __name__ == "__main__":
    unittest.main()
