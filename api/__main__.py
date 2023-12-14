""" Entry point for the API """
from dotenv import dotenv_values
from run import run

PORT = 1234
WEBSOCKET_PORT = 1235
ENVIRONMENT = "development"

# .env setup
config = dotenv_values()
print("DOTENV: " + str(config))
if "PORT" in config:
    PORT = config["PORT"]
if "WEBSOCKET_PORT" in config:
    WEBSOCKET_PORT = config["WEBSOCKET_PORT"]
if "ENVIRONMENT" in config:
    ENVIRONMENT = config["ENVIRONMENT"]

print(
    "PORT: " + str(PORT),
    "WEBSOCKET_PORT: " + str(WEBSOCKET_PORT),
    "ENVIRONMENT: " + str(ENVIRONMENT),
)

run(PORT, WEBSOCKET_PORT, ENVIRONMENT)
