"""This gets the audio from the microphone and stores it in a file"""

# required pip installs for this file:
# pylint: disable=C0301
# 1. pip install pyaudio (Apple M-Chips https://stackoverflow.com/questions/73268630/error-could-not-build-wheels-for-pyaudio-which-is-required-to-install-pyprojec)
# 2. pip install speechRecognition

import threading
import time
import speech_recognition as sr

# Function to handle the audio listening
def listen_for_speech(recognizer, stop_event):
    with sr.Microphone() as source:
        i = 0
        while True:
            i += 1
            print("Say something!")
            # Start listening in the background
            audio_data = recognizer.listen(source, phrase_time_limit=2)
            # Stop the listening process if the stop event is set
            if stop_event.is_set():
                print("Listening stopped.")
                return

            with open(f"output{i}.wav", "wb") as f:
                f.write(audio_data.get_wav_data())
            print("Audio saved to output.wav")

# Main program
if __name__ == '__main__':
    # Initialize recognizer and stop event
    r = sr.Recognizer()
    stop_listening = threading.Event()

    # Start the listening thread
    listen_thread = threading.Thread(target=listen_for_speech, args=(r, stop_listening))
    listen_thread.start()

    # Wait for a command to stop listening
    try:
        while True:
            time.sleep(0.1)  # Sleep briefly to avoid busy waiting
            # You can implement any condition to set the stop event here
            # For example, a keyboard input or a certain signal
    except KeyboardInterrupt:
        # When you press Ctrl+C, the stop event is set, and the thread will finish
        stop_listening.set()
        listen_thread.join()

    print("Program ended.")