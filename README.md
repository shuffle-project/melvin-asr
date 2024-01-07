# ASR-API

ASR-API is an application serving REST and Websocket endpoints for the transcription of audio files. 

## Prerequisites

Before you begin, ensure you have installed the following tools:

- Python 3.10
- Docker
- Docker Compose
- Visual Studio Code
- ffmpeg

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shuffle-project/asr-api.git
   ```
2. Build and run the app using Docker Compose from the root directory:
   ```bash
   docker-compose -f docker-compose.local.yml up
   ``` 
5. Access the REST-API in your web browser at http://localhost:8393 or using an HTTP client like curl or Postman.
5. Access the Websocket-API at http://localhost:8394 using a websocket client. This is build upon python's websockets package.
6. To stop the API, press Ctrl+C in the terminal where the docker-compose up command is running.

## Local Development

Besides the local Docker Compose stack, there is an option to run both services directory on your local machine.

### Install dependencies
```bash
    pip install -r ./requirements.txt
```

### Run the app
Locally for a development environment the websocket and the flask api are started seperatly.

   ```bash
   python ./app.py
   ``` 

## Usage

> :warning: Some of the following endpoints require authentication using an API key:
> - `/transcriptions`
> - `/transcriptions/<transcription_id>`
> 
> To authenticate, add the following header to your request:
> 
> **default key: shuffle2024**
> 
> Set the key in your `.env` file if you want to change it 

### / Endpoint (GET)
- **Description:** Retrieve basic information.
- **Method:** GET
- **URL:** `/`
- **Response:** JSON object containing basic information about the API.
- 
### /transcriptions Endpoint (GET)
- **Description:** Retrieve a list of all transcription id's and their current status.
- **Method:** GET
- **URL:** `/transcriptions`
- **Response:** JSON object containing a list of all transcription id's and their current status.

Example:
```
GET /transcriptions
```

### /transcriptions Endpoint (POST)
- **Description:** Submit an audio file for transcription.
- **Method:** POST
- **URL:** `/transcriptions`
- **Request Body:**
  - `file`: Audio file (multipart/form-data)
  - `settings`: Any value (see chapter down below for settings options)
- **Response:** Confirmation of transcription request submission.

Example:
```
Header: key: shuffle2024
Body: settings: {"test": "test"}, file: "test.wav"
POST /transcriptions
```

### /transcriptions/<transcription_id> Endpoint (GET)
- **Description:** Get the transcription status for a given transcription ID.
- **Method:** GET
- **URL:** `/transcriptions/<transcription_id>`

- **Parameters:**
  - `transcription_id`: ID received upon submitting a transcription request.
- **Response:** Transcription status file for the given ID.

Example:
```
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
```
GET /health
```

## Transcription Settings
Software Configuration Options
This documentation provides an overview of specific configuration options available in the software, along with their default values and purposes.

### Configuration Parameters
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


! Not all of these Settings have been tested for our setup, please refer to https://github.com/SYSTRAN/faster-whisper for more information

### Rest API
Please send these options as on JSON object named "settings" in the body to the ```/transcriptions Endpoint (POST)```, e.g. ```{"language": "auto"}```.

### Websocket API
The Websocket API does not allow setting input by the client. All settings are fixed in the `src/api/websocket/websockets_settings.py` file.

## Testing

### Pylint

Linting is done with pylint for all `*.py` files checked in to Git.

```bash
pylint $(git ls-files '*.py')  
``` 

### Integration Tests

To imporove our code quality, we are linting each Pull Request adding new code to main.
See `.github/workflows/lint.yml`.

### Smoke Tests

To make sure that new code is working, there are 2 smoke tests, one for the rest endpoint and one for the websockets endpoint.
See `/infrastrcture/smoke-test`.

**rest.py**
Call `python rest.py {port} {auth_key}` to test the REST endpoints.

**websocket.py**
Call `python websocket.py {port}` to test the Websockets endpoints.

## Deployment

### Deploy Process
To ensure our code is tested and deployed as we want, we setup 2 branches to handle a development and production codebase.
1. **main**: Our main branch is the development base we are integrating in while developing. New code is tested in this set.
2. **deploy**: Our deploy branch is the production base we are holding code that is deployed to the production Server. This is where our deployment pipeline is running off.

### Deploy Pipeline

For deploying the both services to production, we have a docker-compose solution setup. The deployment is handled by GitHub Actions, see the `.github/workflows/deploy-publish.yml` for more information. 
Steps in Deployment:
1. **Build Docker images**: We are building both services in a container using the Dockerfile in the corresponding directory.

2. **Publish Docker images**: After the build process, both images are published to the GitHub packages registry of the [Shuffle-project](https://github.com/orgs/shuffle-project/).

3. **Deployment**: Once both services are packed in container and published to the registry, the `docker-compose.yml` and the `scripts/startup.sh` script are copied and run on the Shuffle server. This spins up both services to production.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shuffle-project/asr-api/blob/feat/license/LICENSE) file for details.

## Acknowledgements

- Flask: https://flask.palletsprojects.com/
- FFmpeg: https://ffmpeg.org/
- Waitress: https://flask.palletsprojects.com/en/3.0.x/deploying/waitress/
- whisper.cpp: https://github.com/ggerganov/whisper.cpp
