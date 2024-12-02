import logging
from typing import List
from faster_whisper.transcribe import Word
from pydub.utils import re


class LocalAgreement:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.unconfirmed: List[Word] = []
        self.confirmed: List[Word] = []

    def clear(self):
        self.unconfirmed = []
        self.confirmed = []

    def merge(self, incoming: List[Word]):
        # TODO: subtract confirmed
        if len(self.confirmed) > 0:
            incoming = [w for w in incoming if w.start > self.confirmed[-1].end - 0.1]
        common_prefix, ind = self.get_common_prefix(incoming)
        self.confirmed += common_prefix
        # Were all parts validated?
        if len(common_prefix) < len(incoming):
            self.unconfirmed = incoming[ind:]
        else:
            self.unconfirmed = []
        return self.confirmed

    def get_confirmed_text(self):
        return " ".join([x.word for x in self.confirmed])

    def __norm_word(self, word):
        text = word.lower()
        # Remove non-alphabetic characters using regular expression
        text = re.sub(r"[^a-z]", "", text)
        return text.lower().strip().strip(".,?!")

    def get_common_prefix(self, new: List[Word]):
        """Find common prefix between new words and unconfirmed"""
        self.logger.warning(f"Got: {' '.join([x.word for x in new])}")
        self.logger.warning(f"Has: {' '.join([x.word for x in self.unconfirmed])}")
        i = 0
        while (
            i < len(new)
            and i < len(self.unconfirmed)
            and self.__norm_word(new[i].word)
            == self.__norm_word(self.unconfirmed[i].word)
        ):
            i += 1
        self.logger.warning(f"Determined: {' '.join([x.word for x in new[:i]])}")
        return new[:i], i
