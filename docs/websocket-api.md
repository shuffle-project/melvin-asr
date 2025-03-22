# WebSocket

## Overview

This documentation provides a concise guide on connecting to the WebSocket server for streaming audio data and receiving transcriptions. The server processes audio chunks in real-time, providing partial and final transcriptions.

## WebSocket Server Details

**URL** `ws://{*host*}:8394`

## Workflow

This is how the workflow for a client does look like:

1. Connect to the WebSocket server.
1. Authenticate via api key
1. Capture Audio in chunks of 0.1 - 1 seconds and send them to the server continuously. You do not need to wait for a message in response.
1. Receive Transcriptions from the server:
    - Partial Transcriptions: Sent periodically based on server’s latency adjustments, part of the next final.
    - Final Transcriptions: Sent after a set duration, providing a good quality transcript of the current context.
1. Send “eof” when audio capture is complete to finalize and export the transcription.
1. Close Connection.
1. Get the audio file and transcript of you stream via the REST APIs `export` endpoints. See [REST Documentation](docs/rest-api.md).

### Authentication

When first connecting via websocket the server expects authentication via an api key (specified in the config).
To do this the first message must be a valid json of format `{"Authorization":"<your api key here>"}`.
If the authorization is invalid an error message is send and the websocket connection is closed by the server.

When using the Melvin-Asr Websocket backend with BBB ensure that the [first message in configured](https://github.com/bigbluebutton/bbb-transcription-controller/blob/4561ca29dade8923c7af9c1f5ecbb5e66862da7a/config/default.example.yml#L38) accordingly.

### Multi Client Workflow

The WebSocket server is built to handle multiple clients simultaneously on both CPU and GPU models. The following points describe the behavior to expect when multiple clients are added to the stream.

- The `worker_seats`options in the `config.yml` files does configure how many clients are allowed to enter a stream. If there are no available seats, the websocket connection to client will not be closed, instead the server sends a reminder every 10 seconds that indicates a waiting status of the client. If a seat becomes available, it will be given to the client. Currently there is no queue for the clients.
- If the client gets a worker seat, it is not obvious if it is a CPU or GPU seat, the handling is always the same for both types.
- Currenlty streaming with CPU is only possible with a `tiny` faster-whisper model. The CPU option should only be used as a fallback or testing option as the quality is bad.

## Message Options

The WebSocket server expects two types of data.

### Audio Data

- Type: bytes
- Description: Raw audio data sent to the server for transcription.
- Format: Raw audio data in binary format
- Sample Rate: 16000 Hz
- Sample Width: 2 bytes (16-bit PCM)
- Channels: 1 (mono)

See this example for Audio Chunk preperation (Python).

    from pydub import AudioSegment
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio_data = recognizer.record(source, duration=0.5)
        audio_segment = AudioSegment(
            data=audio_data.get_wav_data(),
            sample_width=audio_data.sample_width,
            frame_rate=audio_data.sample_rate,
            channels=1,
        )
        resampled_audio = audio_segment.set_frame_rate(16000).set_channels(1)
        audio_chunk = resampled_audio.raw_data

### Control Messages

- Type: str
- Options:
- "eof": Signals the end of the audio stream, prompting the server to finalize and export the transcription.

## Partial and Final Transcriptions

This is how the messages you receive from the server will look like. Partials are building up the sentence, until a final does provide the entire context of the last partials. As soon as a final is printed, the current context is removed an it starts again.

    {
    "partial": ""
    }

    {
    "partial": " Das ist ein..."
    }

    {
    "partial": " Das ist ein Beispiel für..."
    }

    {
    "partial": " Das ist ein Beispiel für Final."
    }

    {
    "result": [
        {
        "conf": 0.8052,
        "start": 6.792375,
        "end": 7.452375,
        "word": "Das"
        },
        {
        "conf": 0.995533,
        "start": 7.452375,
        "end": 7.832375000000001,
        "word": "ist"
        },
        {
        "conf": 0.943805,
        "start": 7.832375000000001,
        "end": 8.292375,
        "word": "ein"
        },
        {
        "conf": 0.860385,
        "start": 8.292375,
        "end": 8.832375,
        "word": "Beispiel"
        },
        {
        "conf": 0.974582,
        "start": 8.832375,
        "end": 10.112375,
        "word": "für"
        },
        {
        "conf": 0.495881,
        "start": 10.112375,
        "end": 10.892375000000001,
        "word": "Final."
        }
    ],
    "text": " Das ist ein Beispiel für Final."
    }

### EOF Message

As soon as a message is send to the server including "eof", the server will export the transcript and the audio-data of the stream and close the connection.
The export can be accessed under the ID you are getting as soon as you send "eof to the server. There are REST-endpoints waiting to provide the data, take a look at the docs there.
