always run in the ./api directory!

Update pylance extension paths to support imports in sub-packages api and runner

run: 
    python api
    python whispercpp_runner

test: 
    pytest

lint:
    pylint $(git ls-files '*.py')  

install: 
    pip install -r api/requirements.txt
    pip install -r whispercpp_runner/requirements.txt

local testing docker compose:
    docker compose -f docker-compose.local.yml up