always run in the ./api directory!

Update pylance extension paths to support imports in sub-packages api and runner

run: 
    flask run
    python app.py --debug
test: 
    pytest
lint:
    pylint $(git ls-files '*.py')  
install: 
    pip install -r api/requirements.txt