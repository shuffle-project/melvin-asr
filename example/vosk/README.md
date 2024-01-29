# VOSK

the files in this folder are used to test vosks functionality. 

## Vosk Client
The file `vosk_client.py` does rely on a docker container serving a vosk model via a websocket connection.

The container can be started using `docker run -d -p 2700:2700 alphacep/kaldi-en:latest`.
See `https://alphacephei.com/vosk/server` for more information.