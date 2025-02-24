# Facebooks Seamless M4T tests

**Sample text**

```txt
And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
```

## CPU results

**English to German**
Run on CPU: AMD Ryzen 5 3600XT 6-Core Processor

| Type | Duration in s | Personal-Evaluation | Comment                                                        |
| ---- | ------------- | ------------------- | -------------------------------------------------------------- |
| S2ST | 16            | 7/10                | No similar breaks in the speech, and the voice is not natural. |
| S2TT | 10            | 10/10               | Perfekt translation                                            |
| T2TT | 7.5           | 10/10               | Perfekt translation                                            |
| T2TT | 8             | 7/10                | Segmented (from faster-whisper): 10% slower, constext issues   |


## Attempts

**Live Transcription**
cloudn't get live transcription running with SeamlessM4T

// TODO
Test GPU
Test how long loading time is
Test how to switch model for runner in GPU
Test if possible to 2 models in CUDA

in die Yaml integrieren, dass Translation nicht aktiviert werden muss, ob mans will oder nicht, nochmal gemeinsam angucken.
Cuda 0 for whisper and Cuda 1 for Seamless, oder beide auf Cuda 0
Model mitgeben, damit schnell austauschbar ist.
