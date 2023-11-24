FROM python:3.12

WORKDIR /api

COPY . .
COPY ./.env.prod ./.env

RUN pip install -r ./requirements.txt

EXPOSE 80

WORKDIR /

CMD ["python", "api"]
