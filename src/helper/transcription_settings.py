""" Function to handle settings for the transcription with faster-whisper. """

# The settings are used to configure the transcription process by faster-whisper:

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

from src.helper.config import CONFIG


class TranscriptionSettings:
    """Settings for the transcription module."""

    def __init__(self):
        self.default_settings: dict = {
            "language": None,
            "task": "transcribe",
            "beam_size": 5,
            "best_of": 5,
            "patience": 1.0,
            "length_penalty": 1.0,
            "repetition_penalty": 1.0,
            "no_repeat_ngram_size": 0,
            "temperature": [0, 0.2, 0.4, 0.6, 0.8, 1],
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": True,
            "prompt_reset_on_temperature": 0.5,
            "initial_prompt": None,
            "prefix": None,
            "suppress_blank": True,
            "suppress_tokens": [-1],
            "without_timestamps": False,
            "max_initial_timestamp": 1,
            "word_timestamps": True,
            "prepend_punctuations": "\"'“¿([{-",
            "append_punctuations": "\"'.。,，!！?？:：”)]}、",
            "vad_filter": True,
            "vad_parameters": None,
        }
        self.apply_config_defaults()

    def get_and_update_settings(self, settings: dict = None) -> dict:
        """Returns the updated configuration."""

        if settings is None:
            return self.default_settings

        updated_config = self.default_settings.copy()
        for key, value in settings.items():
            if key in updated_config:
                updated_config[key] = value

        return updated_config

    def apply_config_defaults(self) -> None:
        """Apply the default settings from global config."""
        config = CONFIG["transcription_default"]
        for key, value in self.default_settings.items():
            if key in config:
                self.default_settings[key] = config[key]
