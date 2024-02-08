# pylint: disable-all

import io
import json
from faster_whisper import WhisperModel
import wave
import sys
import traceback

from segment_info_parser import parse_segments_and_info_to_dict

model = WhisperModel("tiny", device="cpu", compute_type="int8")
MOVING_CHUNK_CACHE = b""
ALL_CHUNK_CACHE = b""

def transcribe_chunk_partial(
    chunk, sample_rate, num_channels, sampwidth
):
    """Function to transcribe a chunk of audio"""
    global MOVING_CHUNK_CACHE
    global ALL_CHUNK_CACHE
    MOVING_CHUNK_CACHE = MOVING_CHUNK_CACHE + chunk
    ALL_CHUNK_CACHE = ALL_CHUNK_CACHE + chunk

    # If the chunk cache is larger than 10 times the size of the chunk
    if len(MOVING_CHUNK_CACHE) >= (len(chunk) * 10):
        #cut the first bytes of the length of the new chunk
        MOVING_CHUNK_CACHE = MOVING_CHUNK_CACHE[len(chunk):]
    # Create a WAV file in memory with the correct headers
    if len(MOVING_CHUNK_CACHE) > 0:
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                # Set the parameters of the wav file
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sampwidth)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(MOVING_CHUNK_CACHE)
            # Seek to the beginning so it can be read by model
            wav_io.seek(0)
            # Transcribe the audio chunk
            segments, info = model.transcribe(wav_io, word_timestamps=True)

            data = parse_segments_and_info_to_dict(segments, info)
            if "segments" in data:
                for segment in data["segments"]:
                    print(segment["text"])



def main(audio_file_path):
    with wave.open(audio_file_path, "rb") as wf:
        sample_rate = wf.getframerate()
        print(sample_rate)
        num_channels = wf.getnchannels()
        print(num_channels)
        sampwidth = wf.getsampwidth()
        print(sampwidth)
        buffer_size = int(sample_rate * 1)  # Adjust buffer size if needed

        try:
            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                transcribe_chunk_partial(
                    data, sample_rate, num_channels, sampwidth
                )

        except Exception as err:
            print(
                "".join(traceback.format_exception(type(err), err, err.__traceback__))
            )


if __name__ == "__main__":
    main(sys.argv[1])
