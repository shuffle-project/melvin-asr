#!/bin/bash

# Navigate to the directory containing the docker-compose.yml file
cd /home/shuffle/asr-api-prod

# Start Docker Compose
docker compose down
docker compose up -d

# Remove all unused images
docker images -a | grep 'asr-api-api' | awk '{print $3}' | xargs -r docker rmi    
docker images -a | grep 'asr-api-whispercpp_runner' | awk '{print $3}' | xargs -r docker rmi
