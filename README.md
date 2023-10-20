Abstract TBD

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or later
- Docker
- Docker Compose
- A code editor (e.g., Visual Studio Code)

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shuffle-project/asr-api.git
   ```
2. Navigate to the project directory:   
   ```bash
   cd asr-api
   ```
3. Build and run the app using Docker Compose:
   ```bash
   docker-compose up
   ``` 
4. Access the API in your web browser at http://localhost:80 or using an HTTP client like curl or Postman.
5. To stop the API, press Ctrl+C in the terminal where the docker-compose up command is running.

## Usage

- The default route (/) of the API returns a "Hello, World!" message. (Work in progress)
- ...

## Deployment

For deploying the API in a production environment, it is configured to use a production-ready WSGI Gunicorn server.

## License

This project is licensed under the ??? License - see the [LICENSE](tbd) file for details.

## Acknowledgements

- Flask: https://flask.palletsprojects.com/
- Gunicorn: https://gunicorn.org/

 