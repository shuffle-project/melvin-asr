# Benchmarking

To properly and reliably evaluate approaches and general changes to the code base benchmarking techniques have to be defined.

Excluding benchmarking the solution for translation there are 4 areas the can and should be benchmarked:

- Quality of Partials (How much to Partials change words that have already been displayed) (Websockets)
- Speed of translation (How fast is the transcription done) (primarily Websockets)
- Accuracy of transcription (Does the transcription match the audio) (REST and Websockets)
- Accuracy of timestamps (How well does the transcription line up) (REST only)

## Quality of partials

Partials (described in [websocket docs](./streaming_architecture.md)) are primarily used for displaying currently spoken words in video conferecing software.    
The main issue for partials is that they operate based on fairly small amounts of audio and therefore are prone to being inaccurate or wrong.    
As a result of this partials may also change in retrospect. For instance:

```
How are
Howard is
```

In this case the model 'misunderstood' the words spoken at first and had to change these words lateron.    
Ideally the model would not have to revise words and be 100% accurate when matched to the corresponding final.

Levenshtein_distance?
