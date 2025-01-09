from dataclasses import dataclass, field
from typing import List

@dataclass
class WebsocketResultBlock:
    partials: List[str] = field(default_factory=lambda: [])
    final: str = ""

@dataclass
class WebsocketResult:
    scale: str = ""
    duration: float = 0.0
    partial_blocks: List[WebsocketResultBlock] = field(default_factory=lambda: [])
    combined_transcript: str = ""
    used_model: str = "N/A"
    faulty: bool = False
    def __post_init__(self):
        if len(self.partial_blocks) == 0:
            return
        if isinstance(self.partial_blocks[0], dict):
            self.partial_blocks = [ WebsocketResultBlock(**x) for x in self.partial_blocks]

@dataclass
class RestResult:
    scale: str = ""
    duration: float = 0.0
    transcript: str = ""
    used_model: str = "N/A"
    faulty: bool = False

@dataclass
class BenchmarkResult:
    filename: str
    rest: RestResult
    websocket: WebsocketResult
    scale: str
    def __post_init__(self):
        if isinstance(self.rest, dict):
            self.rest = RestResult(**self.rest)
            self.rest.scale = self.scale
        if isinstance(self.websocket, dict):
            self.websocket = WebsocketResult(**self.websocket)
            self.websocket.scale = self.scale

@dataclass
class RestEvalResult:
    file_id: str
    duration: float
    wer: float

@dataclass
class WebsocketEvalResult:
    file_id: str
    duration: float
    wer: float
    average_levenshtein_distance: float

