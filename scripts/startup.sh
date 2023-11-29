#!/bin/bash

# Navigate to the directory containing the docker-compose.yml file
cd /home/shuffle/asr-api-prod

# Start Docker Compose
docker compose down --rmi local
docker compose up -d

# Remove all unused images with name "asr-api"
docker rmi $(docker images | grep 'asr-api')   

