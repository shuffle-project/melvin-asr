# Forced Alignment

## Introduction

Forced alignment is the process of synchronizing spoken audio with its corresponding textual transcription by 
determining the exact time boundaries for each word or token. 
Whisper by OpenAI provides robust transcription capabilities and can be extended for forced alignment tasks.

With forced alignment we can ensure to have a ground truth transcript when sometimes the model can not perform adequately.
Using a different approach would enable us to drop the dependency for [stable-ts](https://github.com/jianfch/stable-ts) 
by using functions included in the faster-whisper backend.

This new approach as tested in the *Forced Alignment POC* led to promising results with relatively fast alignment speeds but lacks 
the correct ending times of tokens and has deficits regarding task runtimes.
As a result, we had to re-enable *stable-ts* for the production environment of this application.

## Methodology

The approach is based on the [libskibidi](https://github.com/milkey-mouse/libskibidi/tree/master)-Project that generates 
aligned summary videos of paper abstracts stored in the *arXiv*-Archive for scholarly articles. With few modifications, 
we could implement the underlying alignment process.

### Preprocessing
*Audio Decoding:* The input audio file is decoded to extract data at an appropriate sampling rate.

*Feature Extraction:* The decoded audio is transformed into a spectrogram representation using Whisper’s feature extractor.

*Text Tokenization:* The sentence is tokenized into subwords units using Whisper’s tokenizer.

### Forced Alignment Process

*Segmented Processing:*
The audio is processed in fixed-size segments to handle long durations efficiently.
Each segment is padded or trimmed to fit Whisper’s expected input size.

*Whisper Encoding:*
The feature-extracted segment is passed through Whisper’s encoder to generate high-dimensional representations.

*Token-Audio Alignment:*
Whisper’s alignment mechanism maps tokens to their corresponding audio frames.
Start times for each token are initialized and updated based on alignment results.
End times are determined using the next token’s start time or a predefined frame duration.

*Word-Level Alignment:*
Token timestamps are aggregated into word boundaries.
Word start and end times are extracted from token-level alignments.

# Results

## Testing

We tested two different audio clips of various length with available ground-truth transcripts.
Each were processed using the proposed alignment method first and, for comparison, transcribed separately using the 
integrated transcribe function.
(Reference [Testing Environment](#Testing Environment) for system specifications)

Clip 1 - Length: 0:11 min
<details>
<summary>Align Original Transcript - Execution Time: 2.65s</summary>
"And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country."
</details>

<details>
<summary>Transcribe Audio - Execution Time: 11.77s</summary>
" And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country."
</details>


Clip 2 - Length: 2:57 min
<details>
<summary>Align Original Transcript - Execution Time 87.19s</summary>
"Of the many times he had examined mister Wicker's window and pored over the rope, the ship and the Nubian boy, he had 
never gone into mister Wicker's shop. So now, alone until someone should answer the bell, he looked eagerly, if 
uneasily, around him. What with the one window and the lowering day outside, the long narrow shop was somber. 
Heavy hand hewn beams crossed it from one side to the other. mister Wicker's back being toward the source of light, 
Chris could not see his face. The double fans of minute wrinkles breaking from eye corner to temple and joining with 
those over the cheekbones were drawn into the horizontal lines across the domed forehead. Little tufts of white fuzz 
above the ears were all that remained of the antiquarian's hair, but what drew and held Chris's gaze were the old man's 
eyes. Chris blinked and looked again. Yes, they were still there. Chris swallowed and his voice came back to him. 
Yes sir, he said. I saw your sign, and I know a boy who needs the job. He's a schoolmate of mine. Jakey Harris, 
his name is, and he really needs the job. I I just wondered if the place was still open. What he saw was a fresh 
cheeked lad tall for thirteen, sturdy, with sincerity and good humor in his face, and something sensitive and appealing 
about his eyes. He guessed there must be a lively fire in that room beyond. Would that interfere with Jakey's getting 
the job, sir? But even as he slowly turned, the thought pierced his mind, Why had he not seen the reflection of the 
headlights of the cars moving up around the corner of Water Street and up the hill toward the traffic signals? 
The room seemed overly still. Then, in that second, he turned and faced about. The wide bow window was there before him, 
the three objects he liked best showing frosty in the moonlight that poured in from across the water. Across the water 
Where was the freeway? It was no longer there, nor were the high walls and smokestacks of factories to be seen. 
The warehouses were still there. Flabbergasted and breathless, Chris was unaware that he had moved closer to peer out 
the window in every direction. No electric signs, no lamplit streets. Where the People's Drugstore had stood but a half 
hour before, rose the roofs of what was evidently an inn. A courtyard was sparsely lit by a flaring torch or two, 
showing a swinging sign hung on a post. The post was planted at the edge of what was now a broad and muddy road. 
A coach with its top piled high with luggage stamped to a halt beside the flagged courtyard. They moved into the inn 
the coach rattled off to the stable. My window has a power for those few who are to see."
</details>

<details>
<summary>Transcribe Audio - Execution Time: 44.46s</summary>
" After many times he examined Mr. Worker's window and poured over the rope, the ship, and the Nubian boy, 
he had never gone into Mr. Worker's shop. So now, alone until someone should answer the bell, they looked eagerly, 
if uneasily, around him. What with the one window and the lowering day outside, the long, narrow shop was somber. 
Heavy hand-hewn beams crossed it from one side to the other. Mr. Worker's back being toward the source of light, 
Chris could not see his face. The double fans and minute wrinkles breaking from eye-corner to temple and joining 
with those over the cheekbones were drawn into the horizontal lines across the domed forehead. Little tufts of 
white fuzz above the ears were all that remained of the antiquarian's hair. But what drew and held Chris's gaze 
were the old man's eyes. Chris blinked and looked again. Yes, they were still there. Chris swallowed. 
And his voice came back to him. Yes, sir, he said. I saw your sign, and I know a boy who needs the job. 
He's a schoolmate of mine. J.D. Harris' name is, and he really needs the job. I just wondered if the place 
was still open. What he saw was a fresh-cheeked lad, tall for thirteen, sturdy, with sincerity and good humor 
in his face, and something sensitive and appealing about his eyes. he guessed there must be a lively fire in that 
room beyond would that interfere with jakey getting the job sir but even as he slowly turned the thought pierced 
his mind why have you not seen the reflection of the headlights of the cars moving up around the corner of wall 
under street and up the hill toward the traffic signals The wide bow window was there before him. The three objects 
he liked best, showing Frosty and the moonlight that poured in from across the water. Across the water? 
Where was the freeway? It was no longer there. Nor were the high walls and smokestacks of factories to be seen. 
The warehouses were still there. Flabbergasted and breathless, Chris was unaware that he had moved closer to peer 
out the window in every direction. No electric signs. No lamplit streets. Where the people's drugstore had stood 
but half an hour before rose the roofs of what was evidentially an inn. A courtyard was firstly lit by a flaring 
torch or two, showing a swinging sign hung on a post. The post was planted at the edge of what was now a broad and 
muddy road. The coach with its top piled high with luggage stamped to a halt beside the flagged courtyard. 
they moved into the inn the coach rattled off to the stable my window has a power for those few who are to see"
</details>

It is apparent, that for shorter sequences (Clip 1), the proposed method executes relatively fast in comparison to a full 
transcription while also retaining the perfect script. The transcribed version is nearly identical with only 
punctuation being different. 

As Clip 2 had to be split up into different sections, processing time was nearly doubled for the alignment task compared
to a full transcription. It is noteworthy, that the transcript text is vastly different to the original script (e.g. 
the protagonist's name is misspelled).

The alignment timestamp results were quite close compared to the faster-whisper transcription timestamps only differing 
about 0.5s for some tokens. For the longer Clip 2 we observed abnormal duration for tokens, leading to misalignment for 
the remainder of the transcript:

```
{
"text": "Yes sir, he said.",
"start": 60.9,
"end": 90.46,
"words": [
  {
    "text": "Yes",
    "start": 60.9,
    "end": 60.9,
    "probability": 0.99
  },
  {
    "text": "sir,",
    "start": 61.42,
    "end": 90.4,
    "probability": 0.99
  },
  {
    "text": "he",
    "start": 90.4,
    "end": 90.4,
    "probability": 0.99
  },
  {
    "text": "said.",
    "start": 90.4,
    "end": 90.44,
    "probability": 0.99
  }
]
}
```
This error was reproducible with a different audio file and as such, the proposed method could not be implemented 
further. 

Using stable-ts, the alignment process took 33.07s to execute compared to 87.19s with the POC. 
Utilizing a GPU (nVidia RTX 4080) the same alignment task was processed in only 2.1 seconds.

## Conclusion

As the wisper model currently supports ~448 tokens per segment, sentences have to be broken up into small 
segments which then get iterated through. Longer Alignment tasks therefore take up quite some time, 
even longer than a full transcription.
Since the current POC is only partly working, we still rely on stable-ts for audio alignment.
As a sidenote: According to 
[stable-ts documentation](https://github.com/jianfch/stable-ts) alignment is slower on Faster-Whisper models than on 
vanilla models. We could research if loading a non-faster-whisper model speeds up the task.

Stable-ts is using its attention weights to calculate the timestamps. To further improve on this POC, 
future works could implement a similar algorithm. 


### Testing Environment
MacBook Pro 14 - M4 Pro - 12 Core CPU - 24GB RAM <br>
Transcription in CPU Mode