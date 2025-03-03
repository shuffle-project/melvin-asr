import logging
from typing import Final, List
from faster_whisper.transcribe import Word
from pydub.utils import re


class LocalAgreement:
    SENTENCE_TERMINATION_CHARATERS: Final = ['.', '?', '!']
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.unconfirmed: List[Word] = []
        self.confirmed: List[Word] = []
        self.confirmed_contains_sentence_end = False

    def clear(self) -> None:
        self.unconfirmed = []
        self.confirmed = []
        self.confirmed_contains_sentence_end = False

    def flush_confirmed(self, word_count=None) -> List[Word]:
        if word_count is None:
            word_count = len(self.confirmed)
        flushed = self.confirmed[:word_count]
        self.confirmed = self.confirmed[word_count:]
        self.confirmed_contains_sentence_end = any([symbol in self.confirmed for symbol in self.SENTENCE_TERMINATION_CHARATERS])
        return  flushed

    def flush_at_sentence_end(self) -> List[Word]:
        # Get highest index of allowed termination symbol
        i = len(self.confirmed) - 1
        ind = None
        # TODO: Can this be optimized?
        while i >= 0:
            if any([
                symbol in self.confirmed[i].word for symbol in self.SENTENCE_TERMINATION_CHARATERS
            ]):
                ind = i
                break
            i -= 1
        if ind is None:
            return []
        return self.flush_confirmed(ind + 1)

    def merge(self, incoming: List[Word]) -> List[Word]:
        if len(self.confirmed) > 0:
            incoming = [w for w in incoming if w.start > self.confirmed[-1].end - 0.1]
        common_prefix, ind = self.get_common_prefix(incoming)

        if len(common_prefix) > 0 and not self.confirmed_contains_sentence_end:
            common_prefix_text = " ".join([w.word for w in common_prefix])
            self.confirmed_contains_sentence_end = any([symbol in common_prefix_text for symbol in self.SENTENCE_TERMINATION_CHARATERS])

        self.confirmed += common_prefix
        # Were all parts validated?
        if len(common_prefix) < len(incoming):
            self.unconfirmed = incoming[ind:]
        else:
            self.unconfirmed = []
        return self.confirmed

    def get_confirmed_text(self, cutoff_timestamp = 0.0) -> str:
        return " ".join([
            x.word 
            for x in self.confirmed
            if x.end > cutoff_timestamp + 0.01
        ])

    def get_confirmed_length(self) -> int:
        return len(self.confirmed)

    def contains_has_sentence_end(self) -> bool:
        return self.confirmed_contains_sentence_end

    def __norm_word(self, word) -> str:
        text = word.lower()
        # Remove non-alphabetic characters using regular expression
        text = re.sub(r"[^a-z]", "", text)
        return text.lower().strip().strip(".,?!")

    def get_common_prefix(self, new: List[Word]) -> tuple[List[Word], int]:
        """Find common prefix between new words and unconfirmed"""
        i = 0
        while (
            i < len(new)
            and i < len(self.unconfirmed)
            and self.__norm_word(new[i].word)
            == self.__norm_word(self.unconfirmed[i].word)
        ):
            i += 1
        return new[:i], i
