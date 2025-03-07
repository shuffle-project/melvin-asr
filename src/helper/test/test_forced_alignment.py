import os
import pytest
from src.helper.forced_alignment import align_ground_truth
from src.helper.model_handler import ModelHandler
from faster_whisper import WhisperModel

EXAMPLE_AUDIO_FILE_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example.wav"
)
EXAMPLE_AUDIO_FILE_GROUND_TRUTH = "And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country."

@pytest.fixture()
def model():
    """Load a model and delete after test. THIS CREATED A (NEEDED) DEPENDENCY TO THE MODEL HANDLER TEST"""
    handler = ModelHandler()
    handler.setup_model("tiny")
    model = WhisperModel(
            handler.get_model_path("tiny"),
            local_files_only=True,
            device="cpu",
            compute_type="int8",
            device_index=0,
            num_workers=1,
            cpu_threads=4,
    )

    yield model

def test_forced_alignment(model):
    res = align_ground_truth(
        model=model,
        ground_truth=EXAMPLE_AUDIO_FILE_GROUND_TRUTH,
        audio_path=EXAMPLE_AUDIO_FILE_PATH
    )

    # 1 segment
    assert len(res) == 1
    assert len(res[0].words) == len(EXAMPLE_AUDIO_FILE_GROUND_TRUTH.split()) + 1

    for i in range(1,len(res[0].words)):
        assert res[0].words[i-1].end <= res[0].words[i].start
