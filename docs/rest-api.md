
# REST

> :warning: Some of the following endpoints require authentication using an API key:
>
> - `/transcriptions`
> - `/transcriptions/<transcription_id>`
>
> To authenticate, add the following header to your request:
>
> **default key: shuffle2024**
>
> Set the key in your `.env` file if you want to change it

## / Endpoint (GET)

- **Description:** Retrieve basic information.
- **Method:** GET
- **URL:** `/`
- **Response:** JSON object containing basic information about the API.
-

## /transcriptions Endpoint (GET)

- **Description:** Retrieve a list of all transcription id's and their current status.
- **Method:** GET
- **URL:** `/transcriptions`
- **Response:** JSON object containing a list of all transcription id's and their current status.

Example:

```text
GET /transcriptions
```

## /transcriptions Endpoint (POST)

- **Description:** Submit an audio file for transcription.
- **Method:** POST
- **URL:** `/transcriptions`
- **Request Body:**
  - `file`: Audio file (multipart/form-data)
  - `settings`: Any value (see chapter down below for settings options)
  - `model` (optional): The name of the model that needs to transcribe the audio_file
      (! In case the model is not running, the file will not be transcribed at all)
- **Response:** Confirmation of transcription request submission.

Example:

```text
Header: key: shuffle2024
Body: settings: {"test": "test"}, model: "large-v3", file: "test.wav"
POST /transcriptions
```

## /transcriptions/<transcription_id> Endpoint (GET)

- **Description:** Get the transcription status for a given transcription ID.
- **Method:** GET
- **URL:** `/transcriptions/<transcription_id>`

- **Parameters:**
  - `transcription_id`: ID received upon submitting a transcription request.
- **Response:** Transcription status file for the given ID.

Example:

```text
Header: key: shuffle2024
GET /transcriptions/9a35a78e-9c65-4ff0-9a19-d2bb2adb11db
```

### /health Endpoint (GET)

- **Description:** Check the status of the API.
- **Method:** GET
- **URL:** `/health`
- **Response:** Status of the API (online/reachable).
-

Example:

```text
GET /health
```

## Streaming Export

These streaming export endpoits provide finished streams audio and transcripts to be exported.
The transcription IDs of the stream are provided via the Websocket-API as soon as the "eof" message is send by the client, ending the stream.

### /export/transcript/<transcription_id> Endpoint (GET)

- **Description:** Retrieve the transcription in JSON format for a given transcription ID.
- **Method:** GET
- **URL:** `/export/transcript/<transcription_id>`
- **Parameters:**
  - `transcription_id`: ID of the transcription to retrieve.
- **Response:** JSON file containing the transcription for the given ID.

Example:

```text
Header: key: shuffle2024
GET /export/transcript/9a35a78e-9c65-4ff0-9a19-d2bb2adb11db
```

### /export/audio/<transcription_id> Endpoint (GET)

- **Description:** Retrieve the audio file in WAV format for a given transcription ID.
- **Method:** GET
- **URL:** `/export/audio/<transcription_id>`
- **Parameters:**
  - `transcription_id`: ID of the transcription to retrieve.
- **Response:** Audio file (WAV) for the given ID.

Example:

```text
Header: key: shuffle2024
GET /export/audio/9a35a78e-9c65-4ff0-9a19-d2bb2adb11db
```

## Transcription Settings

Software Configuration Options
This documentation provides an overview of specific configuration options available in the software, along with their default values and purposes.

### Configuration Parameters

```text
- **language**: `str | None` (Default: `None`)  
  The language code (e.g., "en", "fr") of the spoken language in the audio. If not provided, the language is detected in the first 30 seconds of the audio.

- **task**: `str` (Default: `"transcribe"`)  
  The task to execute, options are "transcribe" or "translate".

- **beam_size**: `int` (Default: `5`)  
  Beam size used for decoding.

- **best_of**: `int` (Default: `5`)  
  Number of candidates considered when sampling with non-zero temperature.

- **patience**: `float` (Default: `1.0`)  
  Beam search patience factor.

- **length_penalty**: `float` (Default: `1.0`)  
  Exponential length penalty constant.

- **repetition_penalty**: `float` (Default: `1.0`)  
  Penalty applied to the score of previously generated tokens.

- **no_repeat_ngram_size**: `int` (Default: `0`)  
  Size of ngrams to prevent repetition (set 0 to disable).

- **temperature**: `float | List[float] | Tuple[float, ...]` (Default: `[0, 0.2, 0.4, 0.6, 0.8, 1]`)  
  Temperature for sampling. A tuple of temperatures is used successively upon failures.

- **compression_ratio_threshold**: `float | None` (Default: `2.4`)  
  Threshold for treating a sample as failed based on gzip compression ratio.

- **log_prob_threshold**: `float | None` (Default: `-1`)  
  Threshold for treating a sample as failed based on average log probability over sampled tokens.

- **no_speech_threshold**: `float | None` (Default: `0.6`)  
  Threshold for considering a segment silent based on no_speech probability and log_prob_threshold.

- **condition_on_previous_text**: `bool` (Default: `True`)  
  Determines whether the previous output is used as a prompt for the next window.

- **prompt_reset_on_temperature**: `float` (Default: `0.5`)  
  Resets prompt if temperature is above this value.

- **initial_prompt**: `str | Iterable[int] | None` (Default: `None`)  
  Optional initial text or token ids for the first window.

- **prefix**: `str | None` (Default: `None`)  
  Optional text prefix for the first window.

- **suppress_blank**: `bool` (Default: `True`)  
  Suppress blank outputs at the beginning of the sampling.

- **suppress_tokens**: `List[int] | None` (Default: `[-1]`)  
  List of token IDs to suppress.

- **without_timestamps**: `bool` (Default: `False`)  
  Option to sample only text tokens, excluding timestamps.

- **max_initial_timestamp**: `float` (Default: `1`)  
  Maximum initial timestamp allowed.

- **word_timestamps**: `bool` (Default: `False`)  
  Extract word-level timestamps using cross-attention pattern and dynamic time warping.

- **prepend_punctuations**: `str` (Default: `"'“¿([{-"`)  
  Punctuations to merge with the next word when `word_timestamps` is enabled.

- **append_punctuations**: `str` (Default: `"'”.。,，!！?？:：”)]}、"`)  
  Punctuations to merge with the previous word when `word_timestamps` is enabled.

- **vad_filter**: `bool` (Default: `False`)  
  Enable voice activity detection to filter non-speech parts using the Silero VAD model.

- **vad_parameters**: `dict | VadOptions | None` (Default: `None`)  
  Parameters for the Silero VAD model.
```

! Not all of these Settings have been tested for our setup, please refer to <https://github.com/SYSTRAN/faster-whisper> for more information

### Rest API

Please send these options as on JSON object named "settings" in the body to the ```/transcriptions Endpoint (POST)```, e.g. ```{"language": "de"}```.
