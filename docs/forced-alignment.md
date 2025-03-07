# Forced Alignment

## Introduction

Forced alignment is the process of synchronizing spoken audio with its corresponding textual transcription by 
determining the exact time boundaries for each word or token. 
Whisper by OpenAI provides robust transcription capabilities and can be extended for forced alignment tasks.

## Methodology

### Preprocessing
Audio Decoding: The input audio file is decoded to extract data at an appropriate sampling rate.

Feature Extraction: The decoded audio is transformed into a spectrogram representation using Whisper’s feature extractor.

Text Tokenization: Thet sentence is tokenized into subword units using Whisper’s tokenizer.