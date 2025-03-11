# Translation, Alignment, SM4T

**As seen in the [POC](../../../example/POC_Seamless_M4T/)**

## Model Choice

**Argos translate** is a very small, languagepair based, model. But unfortunately are the results not very good.

**SM4T-v2-large** is a multimodal model, which supports more functionalities than needed and is thus a lot larger, but the results are very good and that is the priority.  
This model also opens the possibility to distillation and finetuning if the quality is wanted but the size is an issue.  

The model has a limited token size of 256, which is important to note and requires a segmentation prior to the tokenization.  
This is done via RecursiveCharacterTextSplitter from langchain.  
There are better segmentations but for ROI this is the best choice.

More information in the example [Readme](../../../example/POC_Seamless_M4T/README.md)

**DeepL** has usually the best performance, but we weren't able to find information on their models and if they opensourced them somewhere. We are pretty sure they are using an LLM.

## Alignment

The alignment for the translated text to the word timestamps of the original text is done via percentile based alignment.  
The whole text is looked at, and for every word it is calculated which of the translated word fits best the percentage position.

Not based on translated segments because that would be more overhead.
There are more ways to improve the aligment, but again, the ROI is hereby the best.

### Alignment by segments

It makes use of translation of segments and then aligning the segments by itself to keep the overall segmentations aligned. This is the easiest way to do this. Everything else would need more advanced algorithms with special treatment for quirks of every language.

The issue with segments as mentioned [here](../../../example/POC_Seamless_M4T/README.md) is, that a lot of context is being lost. We do get a really good alignment, but we lose out on grammar, translation quality etc. It requires a big overhead to fix all this. Especially since computational linguistics is a complex field itself.

=> Therefore the config has been added to either do full or translated segmentation, trading of between subtitle alignment accuracy and correct grammar.

### Special character languages

The aligment bases it's calculation on whitespace separation.  
For example chinese translation comes in blocks which are separated by `,`  
Since we are not versed in the language, we aren't sure how to handle this properly. Due to the RecursiveSegmentation used for the tokenizer, it is guaranteed that the language has some splitting that is used.

## Parallel models

We tested a setup with the rest runner and the Translation set to run on cuda:0  
We did multiple iterations on different file sizes, first starting a transcription and 
waiting for the file upload until the server starts the transcription and then start a translation.  
Due to the sequential behaviour of the runner, both tasks aren't run in parallel.  
But both models are readily available at the same time.  

**faster-whisper large-v3-turbo & SM4T-v2-large**
Works on RTX 4080 16GB VRAM
The average VRAM usage were about 9.7GB
VRAM spiked out to about 13GB, so a 12GB card would be too small.
