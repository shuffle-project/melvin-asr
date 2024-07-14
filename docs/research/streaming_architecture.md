# Real Time Streaming Transcription Architecture

In this file we discuss and evaluate ways for building a real-time streaming solution.

## Transcription Workflow

### Partials & Full results

A typical Streaming Interface of Cloud providers  print partials (incomplete segments) while transcribing a sentence. As soon as the sentence is completed (complete segment), a final is printed

<https://docs.aws.amazon.com/transcribe/latest/dg/streaming-partial-results.html>

  > The
  >
  > The Amazon.
  >
  > The Amazon is
  >
  > The Amazon is the law.
  >
  > The Amazon is the largest
  >
  > The Amazon is the largest ray
  >
  > The Amazon is the largest rain for
  >
  > The Amazon is the largest rainforest.
  >
  > The Amazon is the largest rainforest on the
  >
  > The Amazon is the largest rainforest on the planet.

There are streaming solutions trying to cut text duplicates out of the partials, to make it easier for the reader.
e.g. <https://ufallab.ms.mff.cuni.cz/~machacek/pre-prints/AACL23-2.11.2023-Turning-Whisper-oral.pdf>
This does require a good understanding for the context and is not useful if the sentence is not completed.

### Length of finals and partial printing

We decided to create an interface close to cloud providers.
We want partials that build up sentences (logical seperated segemnets).
Each Partial should not get bigger than 15 sec.
After a logic seperated segment is recognized, a final should be printed. After some tests, 6 sec. where the sweet spot for readability with good context. This is the size we are currently using by default.

### Chunk size & Chunk cache size

- **Chunk size**: We need to collect 2sec of audio bytes to archive useful transcriptions by transcribing with Whsiper. That is why we need to collect finals bigger than 2 seconds.

- **Cache size**: The client does send different sized chunks from (around 0.1 sec to 2 sec long), the server is required to handle this by transcribing cached audio data and not each incoming chunk. So the Chunk size set by the client does not matter for the transcription workflow.

- **big Chunk sizes**: Chunk sizes bigger than 10sec do increase the transcription times drastically. This is why we need to print finals regularly and delete the context with them or use a moving windows with chunks smaller than 10 seconds.

- **Async**: We had issues with a client-workflow where the websocket protocoll did wait for a message to receive before sending the message to the server. This brought us to the conclution that we want to handle each incoming and outgoing message asnycronously on the server and the client. This is how websocket is design and it does allow messages to fail (in transcription or handling) while the server keeps operating.
Our setup collects the messages no matter how fast the server is capable to respond.

### Automated Threshold adjustments

There are 2 main factors for transcribing partials and finals in our system.

1. The length of a partial chunk when it is transcribed
2. The length of a final chunk when it is transcribed

By monitoring the latecy between received and transcribed audio data, we can increase the partial chunk size between transcriptions to lower cpu/gpu usage when it is using to much power.
This allows us to make sure that the stream is not falling behind to much, when the transcriptions are not going fast enough.

## Context Recognition

The main issue of live-streaming transcripts is the requirement to cut the audio stream to smaller audio chunks in order to guarantee a low latency for the user. This is caused by the whisper model which does allow transcription of one file at a time, not an incoming stream with split up context. When cutting at the wrong place, its hard for the whisper model to transcribe a logical text because there may be missing context. This causes a high WER (Word Error Rate) between two finals.

### Detect Punctuation

See `/example/POC_detect_punctuation`

To get the context of a full sentence, we tried to detect sentence ending by punctuation. For that, we transcribed a partial chunk of the audio and detected if there is a sentence ending punctuation in the transcript. If there is, we save the timestamp of that punctuation and cut the chunk of audio according to that.
We did not follow this idea further because of the problems described below.

**Problems:**

- Too many punctuations in the transcripts because of the short audio chunks
- The timestamps are not accurate enough to cut the audio by them

### Levenshtein Distance

Another idea to get more context for the transcripts was to use the Levenshtein distance for connecting two finals. For that, we wanted to pass the last audio second of the previous final to the new one to extend the context and use the Levenshtein distance to remove the overlapping part in the new final.

We did not follow the idea further because of missing packages/libraries implementing the Levenshtein distance in the scope of the project.

### Prompting & Cross final context

We had the problem that even with the large model, the transitions between two finals are often problematic, as words are cut off or the context is no longer given due to the separation of the audio track. This often resulted in a poor word error rate at this point.
We were able to successfully solve this problem with the Whisper Model's prompting option.

It is possible to give the model an audio track that contains an already known part, for example that of the previous final, and then pass the text-results of the previous final to the prompt, whereby the model automatically removes the duplicated results and only returns the new words and results of the current final. In this way, we can use better context and solve the problems with the transition between two finals without implementig a dedicated logic.

The prompt we are using is: `"Beginning of transcription:" + <Text of the previous final>`

## VAD

Whisper VAD does run VAD automatically before running the transcription on the audio chunk. This does not help with context recognition but it does increase the transcription time. MacBook M2 on 1 second chunks at a tiny model: From 0,7-0,8sec transcription time to 0.5-0.6 transcription time.

## Monitoring

We want to track the performance and latency of the stream by measuring the time passed since the stream started and comparing it to the overall audio byte time passed (Length of audio bytes that have been send to the server) and the transcribed byte time (Length of audio bytes that have been transcribed by the server).

=> This is the foundation to improve and measure latency.

## Big Blue Button
Our streaming setup can be used with Big Blue Button. If we connect both services, we get live captioning for BBB meetings. 
To archive this, we need a configured BBB instance running on a different server. This is recommended by BBB so that the service runs in a clean environment. Our BBB instance runs on a separate Azure VM.

In the BBB configuration file, we need to specify which transcription method we want to use (VOSK) and which languages are enabled for transcription (DE).

Then we configured an additional service called `bbb-transcription-controller`. We set the websocket domain (our transcription endpoint) to the German translation. This can be done inside the repo's config yaml file. This was a bit tricky, because if you clone the official repo, change the configuration and run the `app.js` it won't work. We had to do `sudo apt install bbb-transcription-controller` and configure the files in the folder of the apt installation.

On our side, we had to expose the docker port for the transcription service and add a subdomain in nginx to forward this port.
