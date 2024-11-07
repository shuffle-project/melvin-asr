# Melvin ASR

Melvin ASR is an application serving REST and WebSocket endpoints for the transcription of audio files.

**REST API**: The API is based on HTTP requests that handles the transcription of files in an async workflow, enabling user to send an audio file in a first request and receive the transcription via a second request as soon as the transcript is ready. See [REST Documentation](docs/rest-api.md)

**WebSocket API**: The API does provide streaming capabilities. See [WebSocket Documentation](docs/websocket-api.md)

## Getting Started

### Prerequisites

Before you begin, ensure you have installed the following tools:

- Python 3.11+
- Docker & Docker Compose
- Visual Studio Code
- ffmpeg

### Run docker compose

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shuffle-project/melvin-asr.git
   ```

1. Build and run the app using Docker Compose from the root directory:

   ```bash
   docker-compose up
   ```

1. Access the REST-API at <http://localhost:8393>
1. Access the Websocket-API at <http://localhost:8394>. This is build upon python's websockets package.

## Local Development

Besides the local Docker Compose stack, there is an option to run both services directory on your local machine.

### Install dependencies

```bash
pip install -r ./requirements.txt
```

### Run locally

Locally for a development environment the websocket and the flask api are started seperatly.

```bash
python app.py
```

## Research

To optimize ASR there have been multiple Proof-of-concepts to find out which solutions are working most efficiently. Take a look at the following pages:

- [Parallel transcription utilizing one and multiple Whisper models](docs/research/parallel_transcription/parallel_transcription.md)
- [Optimizing the streaming architecture](docs/research/streaming_architecture.md)

## Configuration

The configuration of the service is done in the `config.yml` and `config.local.yml` file. The `config.local.yml` is used for local development, `config.yml` for Docker.

These files are read by the `src/helper/config.py` module, which is providing configurations to the service logic.

## Linting & Testing

The project uses Ruff for linting and formating code, Pytest for Unit tests. See [Test Documentation](docs/test.md)

## Deployment

The project is delivered and deployed as a docker container. Depending on the usage of GPU or CPU, there are different factors that come in play. See [Deployment Documentation](docs/deployment.md)

## Code Integration

We are maintaining our code following trunk based development. This means we are working on features branches, integrating into one trunk, the main branch. Please keep your side branches small, and bring them back to main as soon as possible.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shuffle-project/melvin-asr/blob/feat/license/LICENSE) file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [FFmpeg](https://ffmpeg.org/)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
