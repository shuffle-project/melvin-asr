from jiwer.transforms import (
    Compose,
    RemoveMultipleSpaces,
    Strip,
    ToLowerCase,
    ExpandCommonEnglishContractions,
    RemoveKaldiNonWords,
    RemoveWhiteSpace,
    ReduceToSingleSentence,
)

TRANSFORM_DEFAULT = Compose(
    [
        ToLowerCase(),
        ExpandCommonEnglishContractions(),
        RemoveKaldiNonWords(),
        RemoveWhiteSpace(replace_by_space=True),
        RemoveMultipleSpaces(),
        Strip(),
        ReduceToSingleSentence(),
    ]
)
