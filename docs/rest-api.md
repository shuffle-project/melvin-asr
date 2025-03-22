
# REST

## Transcription Settings

Software Configuration Options
This documentation provides an overview of specific configuration options available in the software, along with their default values and purposes.

### Configuration Parameters

```text
- **language**: `str | None` (Default: `None`)  
  The language code (e.g., "en", "fr") of the spoken language in the audio. If not provided, the language is detected in the first 30 seconds of the audio.

- **task**: `str` (Default: `"transcribe"`)  
  The task to execute, options are "transcribe" or "translate".

- **beam_size**: `int` (Default: `5`)  
  Beam size used for decoding.

- **best_of**: `int` (Default: `5`)  
  Number of candidates considered when sampling with non-zero temperature.

- **patience**: `float` (Default: `1.0`)  
  Beam search patience factor.

- **length_penalty**: `float` (Default: `1.0`)  
  Exponential length penalty constant.

- **repetition_penalty**: `float` (Default: `1.0`)  
  Penalty applied to the score of previously generated tokens.

- **no_repeat_ngram_size**: `int` (Default: `0`)  
  Size of ngrams to prevent repetition (set 0 to disable).

- **temperature**: `float | List[float] | Tuple[float, ...]` (Default: `[0, 0.2, 0.4, 0.6, 0.8, 1]`)  
  Temperature for sampling. A tuple of temperatures is used successively upon failures.

- **compression_ratio_threshold**: `float | None` (Default: `2.4`)  
  Threshold for treating a sample as failed based on gzip compression ratio.

- **log_prob_threshold**: `float | None` (Default: `-1`)  
  Threshold for treating a sample as failed based on average log probability over sampled tokens.

- **no_speech_threshold**: `float | None` (Default: `0.6`)  
  Threshold for considering a segment silent based on no_speech probability and log_prob_threshold.

- **condition_on_previous_text**: `bool` (Default: `True`)  
  Determines whether the previous output is used as a prompt for the next window.

- **prompt_reset_on_temperature**: `float` (Default: `0.5`)  
  Resets prompt if temperature is above this value.

- **initial_prompt**: `str | Iterable[int] | None` (Default: `None`)  
  Optional initial text or token ids for the first window.

- **prefix**: `str | None` (Default: `None`)  
  Optional text prefix for the first window.

- **suppress_blank**: `bool` (Default: `True`)  
  Suppress blank outputs at the beginning of the sampling.

- **suppress_tokens**: `List[int] | None` (Default: `[-1]`)  
  List of token IDs to suppress.

- **without_timestamps**: `bool` (Default: `False`)  
  Option to sample only text tokens, excluding timestamps.

- **max_initial_timestamp**: `float` (Default: `1`)  
  Maximum initial timestamp allowed.

- **word_timestamps**: `bool` (Default: `False`)  
  Extract word-level timestamps using cross-attention pattern and dynamic time warping.

- **prepend_punctuations**: `str` (Default: `"'“¿([{-"`)  
  Punctuations to merge with the next word when `word_timestamps` is enabled.

- **append_punctuations**: `str` (Default: `"'”.。,，!！?？:：”)]}、"`)  
  Punctuations to merge with the previous word when `word_timestamps` is enabled.

- **vad_filter**: `bool` (Default: `False`)  
  Enable voice activity detection to filter non-speech parts using the Silero VAD model.

- **vad_parameters**: `dict | VadOptions | None` (Default: `None`)  
  Parameters for the Silero VAD model.
```

! Not all of these Settings have been tested for our setup, please refer to <https://github.com/SYSTRAN/faster-whisper> for more information
