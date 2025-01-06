from dataclasses import dataclass, field
from typing import List

@dataclass
class WebsocketResultBlock:
    partials: List[str] = field(default_factory=lambda: [])
    final: str = ""

@dataclass
class WebsocketResult:
    duration: float = 0.0
    partial_blocks: List[WebsocketResultBlock] = field(default_factory=lambda: [])
    combined_transcript: str = ""
    used_model: str = "N/A"
    faulty: bool = False

@dataclass
class RestResult:
    duration: float = 0.0
    transcript: str = ""
    used_model: str = "N/A"
    faulty: bool = False

@dataclass
class BenchmarkResult:
    filename: str 
    rest: RestResult
    websocket: WebsocketResult

