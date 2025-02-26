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

## Notes

It is important to note, that the maximum token size is defaulted to 256, it can be increased up to 4096, but the results seem to get worse with larger token sizes. For the best results, it is recommended to use a token size of 256. This is important to be implemented for the tokenization itself, it is not done automatically by the provided tokenizer.
For the purpose of the text preparation we use RecursiveCharacterTextSplitter from langchain. The chunk size is set to 512, since it is character based it should yield a token count of over 256, but just to be sure we also set that to 512, not expecting the quality to change due to the reasoning.

**GPU**
The GPU is performing significantly faster, as expected, and easily supports multiple GPUs e.g. `cuda:0`.
During testing it is unclear if the issue is the limited power of hardware `NVIDIA GeForce RTX 2080 Super, 8GB VRAM`, but in tests the inferenz time showed significant variations. Thus it couldn't be benchmarked properly.

**Loading**
The Model should be cached and first loaded from it if available. In tests using docker it did not use the cache if the image was rebuild, despite the model existing in the provided volume. This is important to note, since the loading time is significant and can be a bottleneck.


// TODO
Test how to switch model for runner in GPU
Test if possible to 2 models in CUDA