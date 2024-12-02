# Local Agreement for Streaming

Local agreement is a strategy for determining the longest common prefix for n audio chunks during sequence to sequence speech recognition. See also the [corresponding paper](https://www.isca-archive.org/interspeech_2020/liu20s_interspeech.pdf). At the core of Local agreement is the idea that if a "hypothesis" i.e. a transcription of a sequence is validated/reinforced by additonal subsequent inputs it is unlikely to change (or need to be changed) and therefore can be considered promising.

However this approach automatically also results in a system that can only give a definite for the audio chunk n once the audio chunk n+1 has been transcribed. Before the transcription n+1 the conditions that would make the transcription of n "promising" are not met.


