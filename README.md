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

## Configuration
The configuration of the ASR-API is done in the `config.yml` and `config.local.yml` file. These files are read by the `src/config.py` module, which is providing configurations to the service logic.

The `config.local.yml` is used for local development.

Please make sure to set the required options:

### Required Configuration

1. *debug* - Actives debug more for logging
2. *api_keys* - Set the key that are used to access the REST API.
3. *stream_runner* - Defined the models running to provide the websocket transcription (*currently only one is supported!*)
4. *rest_runner*- Defined the models running to provide the http transcription

See the files for more information.

## APIs

ASR-API provides two APIs for two different usecases:

1. A REST API based un HTTP requests that handles the transcription of files in an async workflow, enabling user to send an audio file in a first request and receive the transcription via a second request as soon as the transcript is ready. See [REST Documentation](docs/rest-api.md)
1. A Websocket API that does provide streaming capabilities. See [Websocket Documentation](docs/websocket-api.md)

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
Shared test functionality, which is used in multiple test files can be found in `src/test_base`.

## Deployment
ASR-API is delivered and deployed as a docker container. Depending on the usage of GPU or CPU, there are different factors that come in play. See [Deployment Documentation](docs/deployment.md)

## Code Integration

We are maintaining our code following trunk based development. This means we are working on features branches, integrating into one trunk, the main branch. Please keep your side branches small, and bring them back t o main as soon as possible.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shuffle-project/asr-api/blob/feat/license/LICENSE) file for details.

## Acknowledgements

- Flask: https://flask.palletsprojects.com/
- FFmpeg: https://ffmpeg.org/
- Waitress: https://flask.palletsprojects.com/en/3.0.x/deploying/waitress/
- whisper.cpp: https://github.com/ggerganov/whisper.cpp
