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

<details>

  <summary>benchmarking results</summary>

Reference Value (main at commit 39a75f9d6ff436121b055fb7911a1b1345635539)

| Statistic                          | Duration     | WER         | Average Levenshtein Distance |
|------------------------------------|--------------|-------------|------------------------------|
| Count                              | 184.000000   | 184.000000  | 184.000000                   |
| Mean                               | 142.204907   | 0.507875    | 9.211218                     |
| Standard Deviation (Std)           | 77.758936    | 0.188119    | 2.381541                     |
| Minimum (Min)                      | 67.450931    | 0.020468    | 4.271429                     |
| 25th Percentile (25%)              | 104.875387   | 0.362659    | 7.618866                     |
| Median (50%)                       | 120.544210   | 0.481180    | 8.864444                     |
| 75th Percentile (75%)              | 150.024140   | 0.647103    | 10.028701                    |
| Maximum (Max)                      | 621.784362   | 0.983399    | 18.133333                    |


No prompting

| Statistic                  | Duration | WER | Average Levenshtein Distance |
|----------------------------|--------------------|--------------|----------------------------|
| Count                      |  184.000000        | 184.000000   | 184.000000                 |
| Mean                       |  137.807137        | 0.500073     | 14.538975                   |
| Standard Deviation (Std)   |  69.722124         | 0.010093     | 2.465187                    |
| Minimum (Min)              |  65.319508         | 0.429048     | 8.071429                    |
| 25th Percentile (25%)      |  104.127028        | 0.496749     | 12.998778                   |
| Median (50%)               |  118.233081        | 0.500727     | 14.239808                   |
| 75th Percentile (75%)      |  142.518800        | 0.504331     | 15.513872                   |
| Maximum (Max)              |  585.291125        | 0.529438     | 22.693333                   |

</details>

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

### Local Agreement

Local agreement is a strategy for determining the longest common prefix among n audio chunks during sequence-to-sequence speech recognition. See also the corresponding [paper](https://www.isca-archive.org/interspeech_2020/liu20s_interspeech.pdf). At the core of local agreement is the idea that if a "hypothesis" (i.e., a transcription of a sequence) is validated or reinforced by additional subsequent inputs, it is unlikely to change (or need to be changed) and can therefore be considered promising.

However, this approach inherently results in a system that can only provide a definitive transcription for audio chunk n once audio chunk n+1 has been transcribed. Before the transcription of n+1, the conditions required for the transcription of n to be deemed "promising" are not yet satisfied.

Our first step was to apply local agreement to partial transcriptions directly, without making further changes to the partial-to-final system already in place. This already yielded improvements over the baseline (see below). The use of local agreement stabilized partial transcriptions and eliminated jitter between them, albeit with the tradeoff of some added latency.<details>

  <summary>benchmarking results</summary>

Reference Value (main at commit 39a75f9d6ff436121b055fb7911a1b1345635539)

| Statistic                          | Duration     | WER         | Average Levenshtein Distance | Average WER Last Partial to Final |
|------------------------------------|--------------|-------------|------------------------------|------------------------------------|
| Count                              | 184.000000   | 184.000000  | 184.000000                   | 184.000000                        |
| Mean                               | 142.204907   | 0.507875    | 9.211218                     | 9.211218                          |
| Standard Deviation (Std)           | 77.758936    | 0.188119    | 2.381541                     | 2.381541                          |
| Minimum (Min)                      | 67.450931    | 0.020468    | 4.271429                     | 4.271429                          |
| 25th Percentile (25%)              | 104.875387   | 0.362659    | 7.618866                     | 7.618866                          |
| Median (50%)                       | 120.544210   | 0.481180    | 8.864444                     | 8.864444                          |
| 75th Percentile (75%)              | 150.024140   | 0.647103    | 10.028701                    | 10.028701                         |
| Maximum (Max)                      | 621.784362   | 0.983399    | 18.133333                    | 18.133333                         |


Local Agreement (same partial <-> final system as above)

| Statistic                          | Duration     | WER         | Average Levenshtein Distance | Average WER Last Partial to Final |
|------------------------------------|--------------|-------------|------------------------------|------------------------------------|
| Count                              | 184.000000   | 184.000000  | 184.000000                   | 184.000000                        |
| Mean                               | 135.436777   | 0.236248    | 5.831115                     | 5.831115                          |
| Standard Deviation (Std)           | 70.528878    | 0.211362    | 1.380471                     | 1.380471                          |
| Minimum (Min)                      | 63.915297    | 0.014451    | 2.814286                     | 2.814286                          |
| 25th Percentile (25%)              | 100.581711   | 0.076304    | 5.018676                     | 5.018676                          |
| Median (50%)                       | 115.228423   | 0.147290    | 5.625143                     | 5.625143                          |
| 75th Percentile (75%)              | 142.558473   | 0.324637    | 6.441364                     | 6.441364                          |
| Maximum (Max)                      | 580.561308   | 0.879463    | 14.750000                    | 14.750000                         |


</details>

### Local Agreement partials

Up until this point, the partial-final logic has been implemented by transcribing an audio segment and, after a certain time, promoting the transcription to a final. Following this, the audio data was completely discarded, and the transcription process continued with a new audio segment. While this approach worked, it led to the issue of context being lost between segments. Additionally, using a fixed cutoff duration introduced the possibility of audio being cut off in the middle of a spoken word.

#### Solution: Local Agreement-Based Buffering

To address the above-described issue using local agreement, the buffer within *melvin* (used for transcription) is now divided into three parts:

- **Finalized**: Already confirmed by local agreement and sent as a final.
- **Pending**: Confirmed by local agreement but not yet sent as a final.
- **Provisional**: Unconfirmed, sent as a partial.

This means that content from **Provisional** is promoted to **Pending** once confirmed by local agreement and then to **Finalized** after being sent to the client as a final. 

The promotion from **Pending** to **Finalized** (i.e., the condition that must be met for a final to be sent) occurs when either:  

1. **Pending** reaches a length of > *N*, or  
2. **Pending** contains a sentence-terminating character (`.` `!` `?`).
3. The time since publishing the last final has exceeded a given threshold.

#### Buffer Size Management

To prevent the buffer (and **Finalized**) from growing indefinitely with long-running WebSocket connections, the buffer size is limited to a predefined maximum (in bytes).
Trimming the sliding window down to the target window size is performed after a final is published. 

#### Timing Adjustments Based on Hardware Capabilities

The switch to a sliding window approach also required modifications to the runtime threshold adjustments described in a [previous chapter](#automated-threshold-adjustments). Due to the nature of `asyncio` (i.e., the event loop), transcription calls must be scheduled while accounting for the transcription time.

Similar to the previous approach, there are (in theory) two possible ways to adjust transcription behavior:

1. **Increase the time between transcriptions** based on the transcription duration.
2. **Reduce the sliding window size** if the transcription duration exceeds the delay between transcriptions.

In our case, we found that focusing on the first factor was the most reasonable approach, as adjusting the window size could degrade transcription quality too much.  
Additionally, the window size is currently set to **15 seconds of audio**. On an **AMD Ryzen 7 2700X (16) @ 3.7 GHz** using the *tiny* model, this takes approximately **1.5 seconds** to process. On a **high-end GPU**, transcription is usually fast enough that the first adjustment method alone is sufficient.

#### Additional Notes

When using local agreement and adjusting the time between transcriptions to align with the available hardware, partials were sometimes published very late, as they were only sent once confirmed by local agreement. However, manual testing showed that, due to the sliding window approach, most unconfirmed (i.e., initial) transcriptions were accurate and highly usable.  

To allow for faster publishing of partials (with only a very minor decrease in accuracy), the configuration option **`fast_partials`** was introduced.

