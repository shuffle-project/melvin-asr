always run in the ./api directory!

run: 
    flask run
    python app.py --debug
test: 
    pytest
install: 
    pip install -r api/requirements.txt