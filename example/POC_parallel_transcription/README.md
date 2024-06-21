# Parallel Transcription

Currently we are using multiple WhisperModel classes multithreading in our code to transcribe audio files in parallel, in this POC we want to test if the option "num_workers" is an valid option for parallel transcription. We also want to see how the "cpu_threads" argument does change the way the transcription performs.

Looking at this topic, we want to make sure that the performance of one instance is as good as two or more model instances (Instances of the class WhisperModel of the faster-whisper package), or event better.
Points we want to analyse are formulated below:

See the scripts `transcribe_multi_model.py` & `transcribe_one_model.py` for better understanding.

## Data

To make the decision based on data, we created PDF files of our findings in the `./data` folder. Please have a look for deeper insights.

## Does num_workers enable multiples transcription processes in parallel?

Yes, even without the options set to a number > 1, it is possible to use one WhisperModel instance to run multiple transcription processes in parallel.
The performance seems to improve if a reasonable amount of workers is passed as argument.
See `https://github.com/SYSTRAN/faster-whisper/issues/100`for more information.

### Is it only queueing the file for transcription?

The files are transcribed in parallel, this is the output of the `transcribe_one_model.py` script.
The time it takes makes it obvious.

```bash
Submitting scholz_in_kurz.wav, Executor counter: 1
Transcribing scholz_in_kurz.wav
Submitting scholz_in_kurz.wav, Executor counter: 2
Transcribing scholz_in_kurz.wav
counter 2 took 14.0474 seconds to execute.
counter 1 took 17.9560 seconds to execute.
```

### How is the performance compared to multiple Models

When taking a close look, the performance seems pretty close - in case the other parameters are also matching.

1. One WhisperModel instance, using 1 Thread and having 2 num_workers as argument, using 2 cores - the transcription time is ~15 sec.
1. Two WhisperModel instances, using 1 Thread and having 1 num_workers as argument, using 2 cores - the transcription time is ~16 sec.

See `./data` for more data.

## Is the CPU-Thread option working?

Yes, the "cpu_treads" argument is limiting the cores used in all tests. As obvious in the `./data`, there is another reasonable number of threads for each processor that works best. E.g. the M2 chip is working best on 1 or 2 core, while the Epyc is working best on 8 or 16 threads.

The argmuent does limit the usage for one worker, multiple workers are each using the amout of cores that are passed as argument.

When working with multiple instances of the WhisperModel class, the argmuent does limit the usage of one instance.

## Is the Model running on multiple GPU-devices?

??

### Is it possible to run multiple workers (e.g. 6) on multiple GPUs (e.g. 3)

??

## More learnings

- When working with multiple WhisperModel instances, the initialization must happen with a sligth time between one another or a race condition will throw an error.
- It does not matter if you are instanciation multiple WhisperModel classes or one, the model is only one time in the RAM.
- As the multi and one WhisperModel instance approach are working pretty similar, it seems like we do not need to handle this part of the transcription process ourselfs. Working with once instance seems the easier and evenly "good" way.
- It is important to set the "cpu_treads" argument correctly, for the best case, of each CPU. This should be a config setting for ASR-API.
- Setting the "num_workers" argmuent to the amount of parallel transcription we want to run, seems like a good way of doing things. The results are always one of the best. Setting more workers does not affect the time it takes, but blocks more CPU power. Using less does affect the time it takes.

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
