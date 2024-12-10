# Benchmarking tool

Simple benchmarking tool for the melvin asr backend. 

   Note: This includes a simple dataset (`small`) but the bigger dataset is not included. Download it from the link (not included for now) and use the `./data/prepare.py` script to transform it accordingly.

## Quick start

```sh
pip install -r requirements.txt
```

For details on how to run see:

```sh
python ./benchmark.py --help
```

Running the benchmark depending on your settings and size of dataset might take a while.

## Notes

When using the `--scale-percentage` parameter keep in mind that results of this are only compareable to datasets that are read in the same order.
