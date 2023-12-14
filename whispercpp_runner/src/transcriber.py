from binding.transcribe_to_json import transcribe_to_json
from src.helper.logger import Logger, Color


class Transcriber:

    def __init__(
        self,
        main_path,
        model_path,
        audio_file_path,
        output_file,
        settings,
        debug=True,
    ):
        self.log = Logger("Transcriber", True, Color.MAGENTA)

        self.main_path = main_path
        self.model_path = model_path
        self.audio_file_path = audio_file_path
        self.output_file = output_file
        self.debug = debug
        self.settings = settings

    def transcribe(self):
        threads=4
        processors=1
        offset_t=0
        offset_n=0
        duration=0
        max_context=-1
        max_len=0
        split_on_word=False
        best_of=2
        beam_size=-1
        word_thold=0.01
        entropy_thold=2.40
        logprob_thold=-1.00
        debug_mode=False
        translate=False
        diarize=False
        tinydiarize=False
        no_fallback=False
        no_timestamps=False
        language="auto"
        prompt=False
        ov_e_device="CPU",

        # if "threads" in self.settings:
        #     threads = self.settings["threads"]
        # if "processors" in self.settings:
        #     processors = self.settings["processors"]
        if "offset_t" in self.settings:
            offset_t = self.settings["offset_t"]
            self.log.print_log(f"offset_t: {offset_t}")
        if "offset_n" in self.settings:
            offset_n = self.settings["offset_n"]
            self.log.print_log(f"offset_n: {offset_n}")
        if "duration" in self.settings:
            duration = self.settings["duration"]
            self.log.print_log(f"duration: {duration}")
        if "max_context" in self.settings:
            max_context = self.settings["max_context"]
            self.log.print_log(f"max_context: {max_context}")
        if "max_len" in self.settings:
            max_len = self.settings["max_len"]
            self.log.print_log(f"max_len: {max_len}")
        if "split_on_word" in self.settings:
            split_on_word = self.settings["split_on_word"]
            self.log.print_log(f"split_on_word: {split_on_word}")
        if "best_of" in self.settings:
            best_of = self.settings["best_of"]
            self.log.print_log(f"best_of: {best_of}")
        if "beam_size" in self.settings:
            beam_size = self.settings["beam_size"]
            self.log.print_log(f"beam_size: {beam_size}")
        if "word_thold" in self.settings:
            word_thold = self.settings["word_thold"]
            self.log.print_log(f"word_thold: {word_thold}")
        if "entropy_thold" in self.settings:
            entropy_thold = self.settings["entropy_thold"]
            self.log.print_log(f"entropy_thold: {entropy_thold}")
        if "logprob_thold" in self.settings:
            logprob_thold = self.settings["logprob_thold"]
            self.log.print_log(f"logprob_thold: {logprob_thold}")
        if "debug_mode" in self.settings:
            debug_mode = self.settings["debug_mode"]
            self.log.print_log(f"debug_mode: {debug_mode}")
        if "translate" in self.settings:
            translate = self.settings["translate"]
            self.log.print_log(f"translate: {translate}")
        if "diarize" in self.settings:
            diarize = self.settings["diarize"]
            self.log.print_log(f"diarize: {diarize}")
        if "tinydiarize" in self.settings:
            tinydiarize = self.settings["tinydiarize"]
            self.log.print_log(f"tinydiarize: {tinydiarize}")
        if "no_fallback" in self.settings:
            no_fallback = self.settings["no_fallback"]
            self.log.print_log(f"no_fallback: {no_fallback}")
        if "no_timestamps" in self.settings:
            no_timestamps = self.settings["no_timestamps"]
            self.log.print_log(f"no_timestamps: {no_timestamps}")
        if "language" in self.settings:
            language = self.settings["language"]
            self.log.print_log(f"language: {language}")
        if "prompt" in self.settings:
            prompt = self.settings["prompt"]
            self.log.print_log(f"prompt: {prompt}")
        if "ov_e_device" in self.settings:
            ov_e_device = self.settings["ov_e_device"]
            self.log.print_log(f"ov_e_device: {ov_e_device}")

            
        transcribe_to_json(
            main_path=self.main_path,
            model_path=self.model_path,
            audio_file_path=self.audio_file_path,
            output_file=self.output_file,
            debug=self.debug,
            threads=threads,
            processors=processors,
            offset_t=offset_t,
            offset_n=offset_n,
            duration=duration,
            max_context=max_context,
            max_len=max_len,
            split_on_word=split_on_word,
            best_of=best_of,
            beam_size=beam_size,
            word_thold=word_thold,
            entropy_thold=entropy_thold,
            logprob_thold=logprob_thold,
            debug_mode=debug_mode,
            translate=translate,
            diarize=diarize,
            tinydiarize=tinydiarize,
            no_fallback=no_fallback,
            no_timestamps=no_timestamps,
            language=language,
            prompt=prompt,
            ov_e_device=ov_e_device,
        )
