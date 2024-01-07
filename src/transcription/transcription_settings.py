#   - audio: Path to the input file (or a file-like object), or the audio waveform.
#   - language: The language spoken in the audio. It should be a language code such
#     as "en" or "fr". If not set, the language will be detected in the first 30 seconds of audio.
#   - task: Task to execute (transcribe or translate).
#   - beam_size: Beam size to use for decoding.
#   - best_of: Number of candidates when sampling with non-zero temperature.
#   - patience: Beam search patience factor.
#   - length_penalty: Exponential length penalty constant.
#   - repetition_penalty: Penalty applied to the score of previously generated tokens
#     (set > 1 to penalize).
#   - no_repeat_ngram_size: Prevent repetitions of ngrams with this size (set 0 to disable).
#   - temperature: Temperature for sampling. It can be a tuple of temperatures,
#     which will be successively used upon failures according to either compression_ratio_threshold or log_prob_threshold.
#   - compression_ratio_threshold: If the gzip compression ratio is above this value,
#     treat as failed.
#   - log_prob_threshold: If the average log probability over sampled tokens is
#     below this value, treat as failed.
#   - no_speech_threshold: If the no_speech probability is higher than this value AND
#     the average log probability over sampled tokens is below log_prob_threshold, consider the segment as silent.
#   - condition_on_previous_text: If True, the previous output of the model is provided
#     as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop, such as repetition looping or timestamps going out of sync.
#   - prompt_reset_on_temperature: Resets prompt if temperature is above this value.
#     Arg has effect only if condition_on_previous_text is True.
#   - initial_prompt: Optional text string or iterable of token ids to provide as a
#     prompt for the first window.
#   - prefix: Optional text to provide as a prefix for the first window.
#   - suppress_blank: Suppress blank outputs at the beginning of the sampling.
#   - suppress_tokens: List of token IDs to suppress. -1 will suppress a default set
#     of symbols as defined in the model config.json file.
#   - without_timestamps: Only sample text tokens.
#   - max_initial_timestamp: The initial timestamp cannot be later than this.
#   - word_timestamps: Extract word-level timestamps using the cross-attention pattern
#     and dynamic time warping, and include the timestamps for each word in each segment.
#   - prepend_punctuations: If word_timestamps is True, merge these punctuation symbols
#     with the next word
#   - append_punctuations: If word_timestamps is True, merge these punctuation symbols
#     with the previous word
#   - vad_filter: Enable the voice activity detection (VAD) to filter out parts of the audio
#     without speech. This step is using the Silero VAD model
#     https://github.com/snakers4/silero-vad.
#   - vad_parameters: Dictionary of Silero VAD parameters or VadOptions class (see available
#     parameters and default values in the class VadOptions).

language: str | None = None,
    task: str = "transcribe",
    beam_size: int = 5,
    best_of: int = 5,
    patience: float = 1,
    length_penalty: float = 1,
    repetition_penalty: float = 1,
    no_repeat_ngram_size: int = 0,
    temperature: float | List[float] | Tuple[float, ...] = [0, 0.2, 0.4, 0.6, 0.8, 1],
    compression_ratio_threshold: float | None = 2.4,
    log_prob_threshold: float | None = -1,
    no_speech_threshold: float | None = 0.6,
    condition_on_previous_text: bool = True,
    prompt_reset_on_temperature: float = 0.5,
    initial_prompt: str | Iterable[int] | None = None,
    prefix: str | None = None,
    suppress_blank: bool = True,
    suppress_tokens: List[int] | None = [-1],
    without_timestamps: bool = False,
    max_initial_timestamp: float = 1,
    word_timestamps: bool = False,
    prepend_punctuations: str = "\"'“¿([{-",
    append_punctuations: str = "\"'.。,，!！?？:：”)]}、",
    vad_filter: bool = False,
    vad_parameters: dict | VadOptions | None = None