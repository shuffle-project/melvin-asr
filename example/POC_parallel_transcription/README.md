# Parallel Transcription

Currently we are using multiple WhisperModel classes in our code to transcribe audio files in parallel, in this POC we want to test if the option "num_workers" is an valid option for parallel transcription.

Also we want to make sure that the performance is as good as 2 models, or event better.
Points we want to analyse are formulated below:

## Does num_workers enable multiples transcription processes in parallel?

### Is it possible to transcribe in parallel or is it only queueing the file for transcription?

<https://github.com/SYSTRAN/faster-whisper/issues/100>

### How is the performance compared to multiple Models

Multithread access to one model cpu compared to multiple models in multithreading on the same system.

## Is the CPU-Thread option working?

Currently we did not see, that only 4 threads are used, we want to test that.

## Is the Model running on multiple GPU-devices?

### Is it possible to run multiple workers (e.g. 6) on multiple GPUs (e.g. 3)

## Arguments faster-whisper WhisperModel

>Args:
> model_size_or_path: Size of the model to use (tiny, tiny.en, base, base.en,
> small, small.en, medium, medium.en, large-v1, large-v2, large-v3, or large), a path to a
> converted model directory, or a CTranslate2-converted Whisper model ID from the HF Hub.
> When a size or a model ID is configured, the converted model is downloaded
> from the Hugging Face Hub.
>
> device: Device to use for computation ("cpu", "cuda", "auto").
>
> device_index: Device ID to use.
> The model can also be loaded on multiple GPUs by passing a list of IDs
> (e.g. [0, 1, 2, 3]). In that case, multiple transcriptions can run in parallel
> when transcribe() is called from multiple Python threads (see also num_workers).
>
> compute_type: Type to use for computation.
> See <https://opennmt.net/CTranslate2/quantization.html>.
>
> cpu_threads: Number of threads to use when running on CPU (4 by default).
> A non zero value overrides the OMP_NUM_THREADS environment variable.
>
> num_workers: When transcribe() is called from multiple Python threads,
> having multiple workers enables true parallelism when running the model
> (concurrent calls to self.model.generate() will run in parallel).
> This can improve the global throughput at the cost of increased memory usage.
>
> download_root: Directory where the models should be saved. If not set, the models
> are saved in the standard Hugging Face cache directory.
> local_files_only:  If True, avoid downloading the file and return the path to the
> local cached file if it exists.
