# ASR-API

ASR-API is a simple toolkit of two services providing REST and Websocket endpoints for the transcription of audio files. 

1. **API**: A Flask API handling audio files and returning the transcriptions as JSON objecets.(`./api`)

2. **WhisperCPP_runner**: A handler of WhisperCPP that works with the API to transcribe the incoming audio files. (`./whispercpp_runner`)

## Prerequisites

Before you begin, ensure you have installed the following tools:

- Python 3.12
- Docker
- Docker Compose
- Visual Studio Code
- ffmpeg

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shuffle-project/asr-api.git
   ```
2. Navigate to the `whispercpp_runner` directory:   
   ```bash
   cd asr-api/whispercpp_runner
   ```
3. Clone the whisper.cpp repository:
   ```bash
   https://github.com/ggerganov/whisper.cpp.git
   ```
4. Build and run the app using Docker Compose from the root directory:
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
    pip install -r api/requirements.txt
    pip install -r whispercpp_runner/requirements.txt
```

### Run API-Service
Locally for a development environment the websocket and the flask api are started seperatly.

   ```bash
   python api websocket
   ``` 

   ```bash
   python api flask
   ``` 

### Run Whispercpp_runner-Service
   ```bash
   python whispercpp_runner
   ``` 


## Usage

> :warning: Some of the following endpoints require authentication using a API key:
> - `/transcriptions`
> - `/transcriptions/<transcription_id>`
> 
> To authenticate, add the following header to your request:
> key: shuffle2024
> :warning: TBD: Update key and remove from .env once API goes public

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

### /transcriptions Endpoint (POST)
- **Description:** Submit an audio file for transcription.
- **Method:** POST
- **URL:** `/transcriptions`
- **Request Body:**
  - `file`: Audio file (multipart/form-data)
  - `settings`: Any value (see chapter down below for settings options)
- **Response:** Confirmation of transcription request submission.

### /transcriptions/<transcription_id> Endpoint (GET)
- **Description:** Get the transcription status for a given transcription ID.
- **Method:** GET
- **URL:** `/transcriptions/<transcription_id>`

- **Parameters:**
  - `transcription_id`: ID received upon submitting a transcription request.
- **Response:** Transcription status file for the given ID.

### /health Endpoint (GET)
- **Description:** Check the status of the API.
- **Method:** GET
- **URL:** `/health`
- **Response:** Status of the API (online/reachable).

## Transcription Settings
Software Configuration Options
This documentation provides an overview of specific configuration options available in the software, along with their default values and purposes.
Please send these options as on object to the ```/transcriptions Endpoint (POST)```, e.g. ```{"language": "auto"}```

### Audio Processing Options
- offset_t: Time offset in milliseconds for audio processing. Default value is 0.
- offset_n: Segment index offset. Default value is 0.
- duration: Duration of the audio to process, specified in milliseconds. Default value is 0.
### Context and Length Settings
- max_context: Maximum number of text context tokens to store. Default is -1, indicating no limit.
- max_len: Maximum length for a text segment, measured in characters. Default value is 0.
### Text Segmentation
- split_on_word: Determines whether to split text based on words. Default is False, indicating splitting on tokens.
### Decoding and Search Settings
- best_of: Number of best candidates to keep during processing. Default value is 2.
- beam_size: Size of the beam for beam search algorithms. Default is -1, which implies a standard setting.
- word_thold: Threshold for word timestamp probability. Default value is 0.01.
- entropy_thold: Entropy threshold for the decoder to identify fail conditions. Default value is 2.40.
- logprob_thold: Log probability threshold for decoder failure conditions. Default value is -1.00.
### Debugging and Modes
- debug_mode: Toggles debug mode. Default is False.
- translate: Enables translation from the source language to English. Default is False.
- diarize: Enables stereo audio diarization. Default is False.
- tinydiarize: Activates a smaller, possibly less resource-intensive diarization model. Default is False.
- no_fallback: Disables the use of temperature fallback while decoding. Default is False.
- no_timestamps: Opts out of printing timestamps in outputs. Default is False.
### Language and Input Settings
- language: Specifies the language of the input. Default is None, which may imply automatic detection or a standard language setting.
- prompt: Initial prompt for the system. Default is None, indicating no initial prompt.
- Hardware and Execution Settings
- ov_e_device: Specifies the OpenVINO device used for encode inference. Default setting is "CPU".

! Not all of these Settings have been tested for our setup, please refer to https://github.com/ggerganov/whisper.cpp for more information

## Testing

### Pytest

For unit testing we are using the pytest library.

```bash
pytest -s -v --asyncio-mode=auto
``` 

### Pylint

Linting is done with pylint for all `*.py` files checked in to Git.

```bash
pylint $(git ls-files '*.py')  
``` 

### Integration Tests

To imporove our code quality, we are testing and linting each Pull Request adding new code to main.
See `.github/workflows/test.yml`

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
