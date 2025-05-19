from typing import List, Optional

from pydantic import BaseModel


class Word(BaseModel):
    text: str
    start: float
    end: float
    probability: Optional[float] = None

class Segment(BaseModel):
    text: str
    start: float
    end: float
    words: List[Word]

class Transcript(BaseModel):
    text: str
    segments: List[Segment]