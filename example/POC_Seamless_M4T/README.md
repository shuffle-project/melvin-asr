# Facebooks Seamless M4T tests

**Sample text**

```txt
And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
```

## CPU results

**English to German**
Run on CPU: AMD Ryzen 5 3600XT 6-Core Processor

| Type | Duration in s | Personal-Evaluation | Comment                                                             |
| ---- | ------------- | ------------------- | ------------------------------------------------------------------- |
| S2ST | 16            | 7/10                | No similar breaks in the speech, and the voice is not natural.      |
| S2TT | 10            | 10/10               | Perfekt translation                                                 |
| T2TT | 7.5           | 10/10               | Perfekt translation (<256 token default>)                           |
| T2TT | 8             | 7/10                | Segmented (from faster-whisper): 10% slower, constext issues        |
| T2TT | 8             | 8.5/10              | Segmented using RecursiveCharacterTextSplitter Algo on longer texts |

## Attempts

**Live Transcription**
Couldn't get live transcription running with SeamlessM4T

## Notes

It is important to note, that the maximum token size is defaulted to 256, it can be increased up to 4096, but the results seem to get worse with larger token sizes. For the best results, it is recommended to use a token size of 256. This is important to implement a segmentation prior to the tokenization itself, it is not done automatically by the provided tokenizer.
For the purpose of the text preparation we use `RecursiveCharacterTextSplitter` from `langchain`. The chunk size is set to 512, since it is character based it should not yield a token count of over 256, but just to be sure we also set the allowed max tokens to 512.

## Model

SM4T is a multimodal model and supports all the above listed functionalities. Unfortunately it is not possible to just load part of the model, e.g. only the translation part, as it is a single model. This is important to note, as the model is quite large and the loading time is significant.

**Not tested**
Out of scope would be using distillation to create a smaller model.
Performance impact of using quantization was not tested.
Also it was not tested how big the performance impact is when using a translation only smaller and **older** models, e.g. [`facebook/m2m100_418M`.](https://huggingface.co/facebook/m2m100_418M)

**GPU**
The GPU is performing significantly faster, as expected, and easily supports multiple GPUs e.g. `cuda:0`.
During testing it is unclear if the issue is the limited power of hardware `NVIDIA GeForce RTX 2080 Super, 8GB VRAM`, but in tests the inferenz time showed significant variations. Thus it couldn't be benchmarked properly.

**Loading**
The model should be cached and loaded from there first if available. In tests with Docker, the cache was not used when the image was rebuilt, even though the model existed in the volume provided. This is important to note as the load time is significant and can be a bottleneck.

### Text to Text Dedicated

**To run on Windows** (using Docker) as a single run

```sh
docker run --rm --gpus all --user root -v ${PWD}:/workspace -w /workspace nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 bash -c "
    apt-get update && apt-get install -y python3 python3-pip &&
    pip3 install --upgrade pip &&
    pip3 install -r requirements.txt &&
    python3 example/POC_Seamless_M4T/text_to_text_dedicated.py"
```
