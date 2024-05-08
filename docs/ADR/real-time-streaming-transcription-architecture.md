# Real Time Streaming Transcription Architecture

## Topics of interest
*What is the issue that we're seeing that is motivating this decision or change?*

Topics we discussed and evaluated on our way building a real-time streaming solution.

### Partials & Full results
- **Typical Streaming Interface**: Cloud providers typically print partials (incomplete segments) while transcribing a sentence. As soon as the sentence is completed (complete segment), a final is printed

https://docs.aws.amazon.com/transcribe/latest/dg/streaming-partial-results.html

- **Context recognition, cutting doublicated texts**: 
>The      
>The Amazon.
>The Amazon is
>The Amazon is the law.
>The Amazon is the largest
>The Amazon is the largest ray
>The Amazon is the largest rain for
>The Amazon is the largest rainforest.
>The Amazon is the largest rainforest on the
>The Amazon is the largest rainforest on the planet.

There are streaming solutions trying to cut text duplicates out of the partials, to make it easier for the reader. 
e.g. https://ufallab.ms.mff.cuni.cz/~machacek/pre-prints/AACL23-2.11.2023-Turning-Whisper-oral.pdf
This does require a good understanding for the context and is not useful if the sentence is not completed. 

### VAD
**Context Recognition**
We want to find out if we can detect logical seperation of contexts in our audio bytes using VAD. 
This could help to find out when a partial is a logic context that is ready to be send as final.

- SileroVAD? https://github.com/snakers4/silero-vad?tab=readme-ov-file

**Whisper VAD**
Whisper VAD does run VAD automatically before running the transcription on the audio chunk. This does not help with context recognition.
We should try it out for better result quality.

### Chunk size & Chunk cache size
- **Chunk size**: We need to collect 2sec of audio bytes to archive useful transcriptions by transcribing with Whsiper. That is why we need to collect partials bigger than 2 seconds. 
- **Cache size**: The client does send different sized chunks from (around 0.1 sec to 2 sec long), the server is required to handle this by transcribing cached audio data and not each incoming chunk. Chunk size is set by the client, not the server.
- **big Chunk sizes**: Chunk sizes bigger than 10sec do increase the transcription times drastically. This is why we need to print finals regularly or use a moving windows transcribing.

### Monitoring
We want to track the performance and latency of the stream by measuring the time passed since the stream started and comparing it to the overall audio byte time passed (Length of audio bytes that have been send to the server) and the transcribed byte time (Length of audio bytes that have been transcribed by the server).

=> This is the foundation to improve and measure latency.

### Transcription Workflow
- **Async**: We had issues with a client-workflow where the websocket protocoll did wait for a message to receive before sending the message to the server. This brought us to the conclution that we want to handle each incoming and outgoing message asnycronously on the server and the client. This is how websocket is design and it does allow messages to fail (in transcription or handling) while the server keeps operating. 

### Model setup and size

## Decision made
*What is the change that we're proposing and/or doing?*

### Length of finals and partial printing
We decided to create an interface close to cloud providers: https://docs.aws.amazon.com/transcribe/latest/dg/streaming-partial-results.html
We want partials that build up sentences (logical seperated segemnets).
Each Partial should not get bigger than 15 sec.
After a logic seperated segment is recognized, a final should be printed. 

### Test Setup
- Melvin Server incl. RTX A5000 for Faster_Whisper Models

## Consequences
*What becomes easier or more difficult to do because of this change?*