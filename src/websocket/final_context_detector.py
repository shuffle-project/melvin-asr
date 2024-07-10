# This class is used to handle the context detection for the final transcriptions.
# We are sending the context (audio bytes) of the lastly created final to the transcription together with the recent audio bytes.
# This way, the transcription can be more accurate and context
# This class is used to handle the context detection, so the already known text is removed after the transcription.
import re


class FinalContextDetector:
    # type of result & last_final_result:
    # {
    #   "conf": conf,
    #   "start": start + overall_transcribed_seconds,
    #   "end": end + overall_transcribed_seconds,
    #   "word": word,
    # }[]
    # returns type {"result": result, "text": text}
    def remove_first_final_words(
        self, last_final_result: object, result: dict, length_of_finals_in_sec: int
    ) -> object:
        print("last_final_result: ", last_final_result)
        if (last_final_result is None) or (len(last_final_result) == 0):
            return result
        last_final_word = last_final_result[-1]["word"]
        last_final_timestamp = last_final_result[-1]["end"]
        print("last_final_word: ", last_final_word)
        print("last_final_timestamp: ", last_final_timestamp)

        last_recent_result_timestamp = result[-1]["end"]
        expected_timestamp_first_recent_result_word = (
            last_recent_result_timestamp - length_of_finals_in_sec
        )

        for i in range(len(result)):
            if result[i]["start"] >= expected_timestamp_first_recent_result_word:
                result = result[:i]
                break

        return result

    def common_prefix(self, a: list[str], b: list[str]) -> list[str]:
        i = 0
        while (
            i < len(a)
            and i < len(b)
            and self.canonicalize_word(a[i]) == self.canonicalize_word(b[i])
        ):
            i += 1
        return a[:i]

    def canonicalize_word(self, text: str) -> str:
        text = text.lower()
        # Remove non-alphabetic characters using regular expression
        text = re.sub(r"[^a-z]", "", text)
        return text.lower().strip().strip(".,?!")
