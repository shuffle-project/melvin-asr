# This class is used to handle the context detection for the final transcriptions.
# We are sending the context (audio bytes) of the lastly created final to the transcription together with the recent audio bytes.
# This way, the transcription can be more accurate and context
# This class is used to handle the context detection, so the already known text is removed after the transcription.
import re


class FinalContextDetector:
    # returns type & type of last_final_result & type_of_result {"result": result, "text": text}
    # type of result:
    # {
    #   "conf": conf,
    #   "start": start + overall_transcribed_seconds,
    #   "end": end + overall_transcribed_seconds,
    #   "word": word,
    # }[]
    def remove_first_final_words(
        self,
        last_final_result: object,
        result_object: object,
        length_of_finals_in_sec: int,
    ) -> object:
        if (last_final_result is None) or (len(last_final_result["result"]) == 0):
            return result_object

        result_words = result_object["result"]

        print("result before it has been cut: ", result_words)
        print("result before it has been cut text: ", result_object["text"])
        last_recent_result_timestamp = result_words[-1]["end"]
        last_recent_result_timestamp = round(
            last_recent_result_timestamp + 0.49
        )  # rounding up helps to find the last recent final word

        expected_timestamp_first_recent_result_word = (
            last_recent_result_timestamp - length_of_finals_in_sec
        )

        print(
            "expected_timestamp_first_recent_result_word: ",
            expected_timestamp_first_recent_result_word,
        )

        new_result_words = []
        for i in range(len(result_words)):
            if result_words[i]["start"] >= expected_timestamp_first_recent_result_word:
                print("result where cut is made: ", result_words[i])
                new_result_words = result_words[i:]
                break

        print("result_words after it has been cut: ", new_result_words)
        print(
            "result after_words it has been cut text: ",
            " ".join([x["word"] for x in new_result_words]),
        )
        print("last_result: ", last_final_result)
        print("last_result text: ", last_final_result["text"])

        return {
            "result": result_words,
            "text": " ".join([x["word"] for x in result_words]),
        }

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
