from src.helper.config import CONFIG
from src.rest.rest_transcriber import Transcriber
from pytest import raises

def test_gpu_check():
    invalid_gpu_config = CONFIG["rest_runner"][0].copy()
    invalid_gpu_config["device"] = "cuda"

    invalid_gpu_config["compute_type"] = "float16"
    # This could in theory be valid...however it is very unlikely
    invalid_gpu_config["device_index"] = 100

    with raises(Exception, match="CUDA failed with error CUDA driver version is insufficient for CUDA runtime version"):
        Transcriber(invalid_gpu_config)

def test_preferred_model():
    testable = Transcriber(CONFIG["rest_runner"][0])
    assert testable.get_preferred_model() == CONFIG["rest_runner"][0].get("models", ["False"])[-1]
