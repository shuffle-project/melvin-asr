# From https://huggingface.co/facebook/seamless-m4t-v2-large#supported-languages
POSSIBLE_LANGUAGES = [
    "afr",
    "amh",
    "arb",
    "ary",
    "arz",
    "asm",
    "azj",
    "bel",
    "ben",
    "bos",
    "bul",
    "cat",
    "ceb",
    "ces",
    "ckb",
    "cmn",
    "cmn_Hant",
    "cym",
    "dan",
    "deu",
    "ell",
    "eng",
    "est",
    "eus",
    "fin",
    "fra",
    "fuv",
    "gaz",
    "gle",
    "glg",
    "guj",
    "heb",
    "hin",
    "hrv",
    "hun",
    "hye",
    "ibo",
    "ind",
    "isl",
    "ita",
    "jav",
    "jpn",
    "kan",
    "kat",
    "kaz",
    "khk",
    "khm",
    "kir",
    "kor",
    "lao",
    "lit",
    "lug",
    "luo",
    "lvs",
    "mai",
    "mal",
    "mar",
    "mkd",
    "mlt",
    "mni",
    "mya",
    "nld",
    "nno",
    "nob",
    "npi",
    "nya",
    "ory",
    "pan",
    "pbt",
    "pes",
    "pol",
    "por",
    "ron",
    "rus",
    "slk",
    "slv",
    "sna",
    "snd",
    "som",
    "spa",
    "srp",
    "swe",
    "swh",
    "tam",
    "tel",
    "tgk",
    "tgl",
    "tha",
    "tur",
    "ukr",
    "urd",
    "uzn",
    "vie",
    "yor",
    "yue",
    "zsm",
    "zul",
]

LANGUAGE_MAP = {
    "af": "afr",
    "am": "amh",
    "ar": "arb",
    "as": "asm",
    "az": "azj",
    "ba": "bak",
    "be": "bel",
    "bg": "bul",
    "bn": "ben",
    "bo": "bod",
    "br": "bre",
    "bs": "bos",
    "ca": "cat",
    "cs": "ces",
    "cy": "cym",
    "da": "dan",
    "de": "deu",
    "el": "ell",
    "en": "eng",
    "es": "spa",
    "et": "est",
    "eu": "eus",
    "fa": "pes",
    "fi": "fin",
    "fo": "fao",
    "fr": "fra",
    "gl": "glg",
    "gu": "guj",
    "ha": "hau",
    "haw": "haw",
    "he": "heb",
    "hi": "hin",
    "hr": "hrv",
    "ht": "hat",
    "hu": "hun",
    "hy": "hye",
    "id": "ind",
    "is": "isl",
    "it": "ita",
    "ja": "jpn",
    "jw": "jav",
    "ka": "kat",
    "kk": "kaz",
    "km": "khm",
    "kn": "kan",
    "ko": "kor",
    "la": "lat",
    "lb": "ltz",
    "ln": "lin",
    "lo": "lao",
    "lt": "lit",
    "lv": "lvs",
    "mg": "mlg",
    "mi": "mri",
    "mk": "mkd",
    "ml": "mal",
    "mn": "khk",
    "mr": "mar",
    "ms": "zsm",
    "mt": "mlt",
    "my": "mya",
    "ne": "npi",
    "nl": "nld",
    "nn": "nno",
    "no": "nob",
    "oc": "oci",
    "pa": "pan",
    "pl": "pol",
    "ps": "pbt",
    "pt": "por",
    "ro": "ron",
    "ru": "rus",
    "sa": "san",
    "sd": "snd",
    "si": "sin",
    "sk": "slk",
    "sl": "slv",
    "sn": "sna",
    "so": "som",
    "sq": "sqi",
    "sr": "srp",
    "su": "sun",
    "sv": "swe",
    "sw": "swh",
    "ta": "tam",
    "te": "tel",
    "tg": "tgk",
    "th": "tha",
    "tk": "tuk",
    "tl": "tgl",
    "tr": "tur",
    "tt": "tat",
    "uk": "ukr",
    "ur": "urd",
    "uz": "uzn",
    "vi": "vie",
    "yi": "yid",
    "yo": "yor",
    "zh": "cmn_Hant",
    "cn": "cmn",
    "afr": "afr",
    "amh": "amh",
    "arb": "arb",
    "ary": "ary",
    "arz": "arz",
    "asm": "asm",
    "azj": "azj",
    "bel": "bel",
    "ben": "ben",
    "bos": "bos",
    "bul": "bul",
    "cat": "cat",
    "ceb": "ceb",
    "ces": "ces",
    "ckb": "ckb",
    "cmn": "cmn",
    "cym": "cym",
    "dan": "dan",
    "deu": "deu",
    "ell": "ell",
    "eng": "eng",
    "est": "est",
    "eus": "eus",
    "fin": "fin",
    "fra": "fra",
    "fuv": "fuv",
    "gaz": "gaz",
    "gle": "gle",
    "glg": "glg",
    "guj": "guj",
    "heb": "heb",
    "hin": "hin",
    "hrv": "hrv",
    "hun": "hun",
    "hye": "hye",
    "ibo": "ibo",
    "ind": "ind",
    "isl": "isl",
    "ita": "ita",
    "jav": "jav",
    "jpn": "jpn",
    "kan": "kan",
    "kat": "kat",
    "kaz": "kaz",
    "khk": "khk",
    "khm": "khm",
    "kir": "kir",
    "kor": "kor",
    "lao": "lao",
    "lit": "lit",
    "lug": "lug",
    "luo": "luo",
    "lvs": "lvs",
    "mai": "mai",
    "mal": "mal",
    "mar": "mar",
    "mkd": "mkd",
    "mlt": "mlt",
    "mni": "mni",
    "mya": "mya",
    "nld": "nld",
    "nno": "nno",
    "nob": "nob",
    "npi": "npi",
    "nya": "nya",
    "ory": "ory",
    "pan": "pan",
    "pbt": "pbt",
    "pes": "pes",
    "pol": "pol",
    "por": "por",
    "ron": "ron",
    "rus": "rus",
    "slk": "slk",
    "slv": "slv",
    "sna": "sna",
    "snd": "snd",
    "som": "som",
    "spa": "spa",
    "srp": "srp",
    "swe": "swe",
    "swh": "swh",
    "tam": "tam",
    "tel": "tel",
    "tgk": "tgk",
    "tgl": "tgl",
    "tha": "tha",
    "tur": "tur",
    "ukr": "ukr",
    "urd": "urd",
    "uzn": "uzn",
    "vie": "vie",
    "yor": "yor",
    "yue": "yue",
    "zsm": "zsm",
    "zul": "zul",
}
