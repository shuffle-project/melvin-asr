""" tests convert_save_received_audio_files.py functions"""
import unittest
import io
import os
from pydub import AudioSegment
from werkzeug.datastructures import FileStorage
from convert_save_received_audio_files import convert_to_wav  # make sure to import your function

class TestConvertTestAudio(unittest.TestCase):
    """covers all testing function"""
    def test_convert_to_wav_success(self):
        """ tests convert_to_wav  function"""
        # Create an in-memory byte-stream to simulate a file
        simulated_audio_file = io.BytesIO()
        AudioSegment.silent(duration=1000).export(simulated_audio_file, format="mp3")
        simulated_audio_file.seek(0)  # Go to the start of the stream

        # Create a FileStorage object
        audio_file_storage = FileStorage(stream=simulated_audio_file, filename="test_audio.mp3", content_type="audio/mp3")

        # Define the output directory and filename
        output_directory = "src"
        output_filename = "converted_audio"

        # Call the function under test
        result_path = convert_to_wav(audio_file_storage, output_directory, output_filename)

        # Check that the output file was created and is a valid WAV file
        self.assertTrue(os.path.exists(result_path), "The WAV file was not created.")
        
        # Additional checks can be performed such as file content analysis, duration, etc.
        converted_audio = AudioSegment.from_file(result_path)
        self.assertEqual(converted_audio.frame_rate, 16000, "The frame rate is not 16kHz.")
        self.assertEqual(converted_audio.channels, 1, "The audio is not mono.")

        # Clean up the created file after the test
        os.remove(result_path)

if __name__ == '__main__':
    unittest.main()
