# Parallel Transcription

We used multiple WhisperModel classes (The Class provided by faster-whisper package) with multithreading in our code to transcribe audio files in parallel. In parallel means transcribing multiple files at the same time using one docker container. With a proof of concept (POC), we aim to find the best option to transcribe multiple files in parallel for CPU and Cuda workloads.

For CPU, we need to determine whether to use a single WhisperModel class from the faster-whisper package in the code or multiple instances. Additionally, we want to test two parameters of the WhisperModel class: the “num_workers” option, which may be a valid choice for parallel transcription, when using one instance and the “cpu_threads” argument, to see how it affects transcription performance.

For GPU, we need to determine whether to use a single WhisperModel class in the code or multiple instances as well. Besides that, we want to see how the performance will work out when transcribing multiple files on one GPU at a time.

The points we want to analyze are outlined below:

See the scripts in the directory `/example/POC_parallel_transcription` and the data for better understanding.

## CPU

### Data

To make the decision based on data, we created PDF files of our findings in the `./data` folder. Please have a look for deeper insights.

### How is the performance of one WhisperModel instance compared to multiple instances

The performance seems pretty close - in case the other parameters are also matching.

1. One WhisperModel instance, using 1 Thread and having 2 num_workers as argument, using 2 cores - the transcription time is ~15 sec.
1. Two WhisperModel instances, using 1 Thread and having 1 num_workers as argument, using 2 cores - the transcription time is ~16 sec.

Conclusion: The option num_workers seems to do the same as multiple instances.

See `./data` for more data.

### Does the num_workers option enable multiples transcription processes in parallel?

Yes, even without the options set to a number > 1, it is possible to use one WhisperModel instance to run multiple transcription processes in parallel.
The performance seems to improve if a reasonable amount of workers is passed as argument. Best solution seems to pass the same num_workers as files are transcribed in parallel.

See `https://github.com/SYSTRAN/faster-whisper/issues/100`for more information.

### Is faster_whisper queueing the file for transcription or are they running in "real" parallel?

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

### Is the CPU-Thread option working?

Yes, the "cpu_treads" argument is limiting the cores used in all tests. As obvious in the `./data`, there is another reasonable number of threads for each processor that works best. E.g. the M2 chip is working best on 1 or 2 core, while the Epyc is working best on 8 or 16 threads.

The argmuent does limit the usage for one worker, multiple workers are each using the amout of cores that are passed as argument.

When working with multiple instances of the WhisperModel class, the argmuent does limit the usage of one instance.

## GPU

### Is the Model running on multiple GPU-devices?

Yes, there is the "device_index" option to pass multiple Cuda cards at the same time as an array.

### Is it possible to run multiple workers (e.g. 6) on multiple GPUs (e.g. 3) ?

It is possible to run multiple transcriptions in parallel on one GPU. The performance will be reasonably slower and the process does happen at the same time.

### How do Multiple WhisperModel instances perform compared to one instance?

When comparing the numbers, we used the scripts in this folder ending with “gpu.” Since this was not a scientific research study, the numbers are derived from a small sample.

In short: It does not make a significant difference. We tried instantiating a class for each file, for each GPU, and one for all files and all GPUs together. All transcription times were generated using comparable audio files and settings.

When comparing one model for 3 GPUs and 3 files to transcribe, with one model per GPU (3 models), the times look like:

23.3, 23.5, 24.1 seconds for multi-model compared to 18.1, 24.6, 28.0 seconds (times for each transcription process of each file, large model).

When comparing one model for 1 GPU and 3 files to transcribe, with one model per file (3 models) on one GPU, the times look like:

8.6, 8.8, 9.1 seconds for multi-model compared to 8.6, 8.1, 8.8 seconds (times for each transcription process of each file, tiny model).

After all, we decided that the differences were too close to see a real benefit from one of the methods. Therefore, going with one model only seems like a reasonable choice because it requires less work.

## More learnings

- When working with multiple WhisperModel instances, the initialization must happen with a sligth time between one another or a race condition will throw an error.
- It does not matter if you are instanciation multiple WhisperModel classes or one, the model is only one time in the RAM. Only tested for CPU!
- As the multi and one WhisperModel instance approach are working pretty similar, it seems like we do not need to handle this part of the transcription process ourselfs. Working with once instance seems the easier and evenly "good" way. There is no way to use one model for CPU and GPU.
- It is important to set the "cpu_treads" argument correctly, for the best case, of each CPU. This should be a config setting for the service. E.g. M2-CPU is 2 Threads and a 128 core CPU is 8 threads.
- Setting the "num_workers" argmuent to the amount of parallel transcription we want to run, seems like a good way of doing things. The results are always one of the best. Setting more workers does not affect the time it takes, but blocks more CPU power. Using less does affect the time it takes.

## Arguments faster-whisper WhisperModel

> Args:
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
> local_files_only: If True, avoid downloading the file and return the path to the
> local cached file if it exists.
