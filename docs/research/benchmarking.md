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

To measure the distance between partials we can simply use the Levenshtein distance. The Levenshtein distance is defined of the minimum transformation cost to get from string A to string B via the operators delete/add/replace on a character level. Using the Levenshtein Distance on partials directly however would always lead to a cost > 0, due to the fact that partials get longer over time.
Therefore the comparison is done by comparing the first *n* characters of the partial at time *t+1* with the partial at *t* with n being the length of partial at time *t*.

## Accuracy of transcription

An accurate transcription of the audio is important in both websocket (i.e. real time) and rest scenarios.
To measure the accuracy of transcriptions the word error rate (WER) metric is rather standard to use.    
The WER is calculated by considering the words that have been changed (substitutions), words that have been added by the model (insertions) and words the model did not pick up on (deletions) when compared to the expected transcript.

While for the rest evaluations just using the transcript returned is fine, for evaluating the quality of the websocket transcript the combination of all finals from the live transcription is used.
