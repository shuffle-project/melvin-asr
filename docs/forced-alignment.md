# Forced Alignment

## Introduction

Forced alignment is the process of synchronizing spoken audio with its corresponding textual transcription by 
determining the exact time boundaries for each word or token. 
Whisper by OpenAI provides robust transcription capabilities and can be extended for forced alignment tasks.
With forced alignment we can ensure to have a ground truth transcript when sometimes the model can not perform adequately.
Using this implementation, we also drop dependency for [stable-ts](https://github.com/jianfch/stable-ts).


## Methodology

The approach is based on the [libskibidi](https://github.com/milkey-mouse/libskibidi/tree/master)-Project that generates aligned
summary videos of paper abstracts stored in the *arXiv*-Archive for scholarly articles. With few modifications, we could 
implement the underlying alignment process.

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

## Drawbacks

As the wisper model currently supports ~448 tokens per segment, sentences have to be broken up into small 
segments which then get iterated through. Alignment tasks often take up quite some time depending on audio duration.

