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

## APIs

ASR-API provides two APIs for different usecases. 
One is based on REST-like HTTP requests and handles the transcription of files in an async workflow, enabling user to send an audio file in a first request and receive the transcription via a second request as soon as the transcript is ready. See [REST Documentation](docs/rest-api.md)
The other one, a Websocket endpoint, does provide streaming capabilities. See [Websocket Documentation](docs/websocket-api.md)

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

### Code Integration

We are maintaining our code in trunk based development. This means we are working on features branches, integrating into one trunk, the main branch.
**main**: Our main branch is the development base we are integrating in while developing. New code is tested in this set.

### Integration Tests

To imporove our code quality, we are linting and unit-testing each Pull Request adding new code to main.
This includes a test of the unit-test coverage for our our `/src` folder of 80%.
See `.github/workflows/test.yml`.

### Smoke Tests

To make sure that new code is working, there are 2 smoke tests, one for the rest endpoint and one for the websockets endpoint.
See `/infrastrcture/smoke-test`.

**rest.py**
Call `python rest.py {port} {auth_key}` to test the REST endpoints.

**websocket.py**
Call `python websocket.py {port}` to test the Websockets endpoints.


### Deploy Process

For deploying the the ASR-API to a production stage, there is a Docker Compose & GitHub Actions solution set up. The deployment is handled partialy by GitHub Actions, see the `.github/workflows/deploy-publish.yml` for more information. And partialy by manual steps.

Steps in Deployment:
1. **Build Docker images**: We are building a container using the Dockerfile in the root directory of the repository.

2. **Publish Docker images**: After the build process, both images are published to the GitHub packages registry of the [Shuffle-project](https://github.com/orgs/shuffle-project/).

3. **Deployment**: Once the container is packed and published to the registry, the `docker-compose.yml` and the `/infrastructure` script are copied to the Shuffle server.

4. **Starting Docker Compose**: After the deployment pipeline copied all files, the startup of the new containers is handled manually. Use Docker Compose to shut the current containers down and start the new ones. The commands are `docker compose down` and `docker compose up`. In case the Containers are not working, keep the old images to rollback the service.

5. **Smoke Tests**: As described in the section above, there are smoke tests for the REST-API and the Websocket-API of the ASR-API service. Run both against the newly running containers to make sure everything is up and running. Rollback in case there are any troubles. The REST-Endpoints `/` and `/health` can be used for an health-check as well.

6. **Config.yml**: The ASR-API is configured in the `config.yml` file. In order to spin up the docker container using docker compose, make sure the config file is availible in the `docker-compose.yml`'s directory

## Configuration
The configuration of the ASR-API is done in the `config.yml` and `config.dev.yml`. These files are read by the `src/config.py` module, which is providing configurations to the service logic. 
Please make sure to set the required options:

### Required Configuration

1. *debug* - Actives debug more for logging
2. *api_keys* - Set the key that are used to access the REST API.
3. *stream_runner* - Defined the models running to provide the websocket transcription (*currently only one is supported!*)
4. *rest_runner*- Defined the models running to provide the http transcription

See the files for more information.


## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shuffle-project/asr-api/blob/feat/license/LICENSE) file for details.

## Acknowledgements

- Flask: https://flask.palletsprojects.com/
- FFmpeg: https://ffmpeg.org/
- Waitress: https://flask.palletsprojects.com/en/3.0.x/deploying/waitress/
- whisper.cpp: https://github.com/ggerganov/whisper.cpp
