FROM python:3.9

WORKDIR /app

COPY ./flask-api /app

RUN pip install -r /app/requirements.txt

EXPOSE 80

ENV NAME Placeholder

# CMD ["python", "/app/app.py"]
# Change -w 1 to amount of available CPU cores
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "app:app"]
