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
5. Access the API in your web browser at http://localhost:8041 or using an HTTP client like curl or Postman.
6. To stop the API, press Ctrl+C in the terminal where the docker-compose up command is running.

## Usage

### / Endpoint (GET)
- **Description:** Retrieve basic information.
- **Method:** GET
- **URL:** `/`
- **Response:** JSON object containing basic information about the API.

### /transcriptions Endpoint (POST)
- **Description:** Submit an audio file for transcription.
- **Method:** POST
- **URL:** `/transcriptions`
- **Request Body:**
  - `file`: Audio file (multipart/form-data)
  - `settings`: Any value (work in progress for future updates)
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


## Testing

### Pytest

For unit testing we are using the pytest library.

```bash
pytest
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
 
