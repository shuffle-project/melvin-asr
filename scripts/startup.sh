#!/bin/bash

# Navigate to the directory containing the docker-compose.yml file
cd /home/shuffle/asr-api-prod

# Start Docker Compose
docker compose down --rmi local
docker compose up -d
