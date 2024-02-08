"""example for vosk local"""
import os
import sys
import wave
from vosk import Model, KaldiRecognizer

# Load the model you downloaded
model = Model(os.getcwd() + "/vosk-models/vosk-model-en-us-0.22-lgraph")

# Open a wav file
wf = wave.open(os.getcwd() + "/input.wav", "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format mono PCM.")
    sys.exit(1)

# Create a recognizer object
rec = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(22050)
    # An audio frame, or sample, contains amplitude (loudness) information at that point in time.
    # To produce sound, tens of thousands of frames are played in sequence to produce frequencies.
    # In the case of CD quality audio or uncompressed wave audio,
    # there are around 44,100 frames/samples per second.
    # Each frame contains 16-bits of resolution, allowing for representations of the sound levels.
    # CD audio is stereo, there is twice as much information,
    # 16-bits for the left channel, 16-bits for the right.
    # => 44100 / 2 = ~22050 Frames per second

    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print(rec.PartialResult())

print(rec.FinalResult())
