# ASR-API

ASR-API is an application serving REST and WebSocket endpoints for the transcription of audio files. 

**REST API**: The API is based on HTTP requests that handles the transcription of files in an async workflow, enabling user to send an audio file in a first request and receive the transcription via a second request as soon as the transcript is ready. See [REST Documentation](docs/rest-api.md)

**WebSocket API**: The API does provide streaming capabilities. See [WebSocket Documentation](docs/websocket-api.md)

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shuffle-project/asr-api.git
   ```
2. Build and run the app using Docker Compose from the root directory:
   ```bash
   docker-compose up
   ``` 
5. Access the REST-API in your web browser at http://localhost:8393 or using an HTTP client like curl or Postman.
5. Access the Websocket-API at http://localhost:8394 using a websocket client. This is build upon python's websockets package.
6. To stop the API, press Ctrl+C in the terminal where the docker-compose up command is running.

## Local Development

Besides the local Docker Compose stack, there is an option to run both services directory on your local machine.

### Prerequisites

Before you begin, ensure you have installed the following tools:

- Python 3.10
- Docker
- Docker Compose
- Visual Studio Code
- ffmpeg

### Install dependencies
```bash
pip install -r ./requirements.txt
```

### Run the app
Locally for a development environment the websocket and the flask api are started seperatly.

```bash
python ./app.py
``` 

## Configuration
The configuration of the ASR-API is done in the `config.yml` and `config.local.yml` file. These files are read by the `src/config.py` module, which is providing configurations to the service logic.

The `config.local.yml` is used for local development.

Please make sure to set the required options:

### Configuration

See the config-files for more information.

The following options are important:

1. *debug* - Actives debug more for logging
1. *api_keys* - Set the key that are used to access the REST API.
1. *transcription_default* - Faster-whisper transcriptions settings passed to all transcription workflows of the system. Set all settings available for faster-whisper.
1. *websocket_stream* - Defined the models for CPU and CUDA GPUs running to provide the websocket stream endpoint. Disable GPU is you do not have a CUDA GPU installed!
1. *rest_runner*- Defined the models running to provide the http transcription

## Testing

### Ruff

VS Code Extension: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff

Linting is done with Ruff (https://github.com/astral-sh/ruff) for all `*.py` files checked in to Git.

```bash
ruff check .    
``` 

Ruff allows formatting as well.

```bash
ruff format . 
```

### Pytest

To test our code we are writing tests utilizing the official Python recommendation: **pytest**. Each subfolder in `/src` has its own `/test` folder holding the testfiles. We are thriving to keep a coverage of 80% of our `/src` folder.
Shared test functionality, which is used in multiple test files can be found in `src/helper/test_base`.

## Deployment
ASR-API is delivered and deployed as a docker container. Depending on the usage of GPU or CPU, there are different factors that come in play. See [Deployment Documentation](docs/deployment.md)

## Code Integration

We are maintaining our code following trunk based development. This means we are working on features branches, integrating into one trunk, the main branch. Please keep your side branches small, and bring them back to main as soon as possible.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shuffle-project/asr-api/blob/feat/license/LICENSE) file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [FFmpeg](https://ffmpeg.org/)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
