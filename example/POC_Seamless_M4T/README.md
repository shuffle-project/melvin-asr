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
| T2TT | 8             | 7/10                | Segmentiert: 10% langsamer, Kontext Probleme                   |


## Attempts

**Live Transcription**
cloudn't get live transcription running with SeamlessM4T

