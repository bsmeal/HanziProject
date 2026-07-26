import re
import unicodedata


ZHUYIN_TONE_MARKS = {
    "ˉ",  # Explicit first tone, occasionally typed
    "ˊ",  # Second tone
    "ˇ",  # Third tone
    "ˋ",  # Fourth tone
    "˙",  # Neutral tone
}

STANDARD_ZHUYIN_KEYBOARD = {
    "1": "ㄅ",
    "q": "ㄆ",
    "a": "ㄇ",
    "z": "ㄈ",

    "2": "ㄉ",
    "w": "ㄊ",
    "s": "ㄋ",
    "x": "ㄌ",

    "e": "ㄍ",
    "d": "ㄎ",
    "c": "ㄏ",

    "r": "ㄐ",
    "f": "ㄑ",
    "v": "ㄒ",

    "5": "ㄓ",
    "t": "ㄔ",
    "g": "ㄕ",
    "b": "ㄖ",

    "y": "ㄗ",
    "h": "ㄘ",
    "n": "ㄙ",

    "u": "ㄧ",
    "j": "ㄨ",
    "m": "ㄩ",

    "8": "ㄚ",
    "i": "ㄛ",
    "k": "ㄜ",
    ",": "ㄝ",

    "9": "ㄞ",
    "o": "ㄟ",
    "l": "ㄠ",
    ".": "ㄡ",

    "0": "ㄢ",
    "p": "ㄣ",
    ";": "ㄤ",
    "/": "ㄥ",
    "-": "ㄦ",
}


def contains_zhuyin(text):
    """
    Return True if the text already contains Zhuyin symbols.
    """
    return bool(
        re.search(
            r"[\u3105-\u312f\u31a0-\u31bf]",
            text,
        )
    )


def remove_zhuyin_tones(text):
    """
    Remove all Zhuyin tone marks.
    """
    normalized = text

    for tone_mark in ZHUYIN_TONE_MARKS:
        normalized = normalized.replace(
            tone_mark,
            "",
        )

    return normalized


def standard_keyboard_to_zhuyin(text):
    """
    Convert raw keys from the standard Taiwanese Zhuyin keyboard
    into Zhuyin symbols.
    """
    converted = []

    for character in text.strip().lower():
        mapped_character = STANDARD_ZHUYIN_KEYBOARD.get(
            character
        )

        if mapped_character:
            converted.append(mapped_character)

    return "".join(converted)


def normalize_pinyin_without_tone(text):
    """
    Normalize pinyin while ignoring tones.

    Examples:
        ài      -> ai
        ai4     -> ai
        XING2   -> xing
        lü      -> lv
        lu:4    -> lv
    """
    normalized = text.strip().lower()

    normalized = normalized.replace("u:", "v")
    normalized = normalized.replace("ü", "v")

    normalized = unicodedata.normalize(
        "NFD",
        normalized,
    )

    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    normalized = re.sub(
        r"[^a-zv]",
        "",
        normalized,
    )

    return normalized


def normalize_zhuyin_without_tone(text):
    """
    Normalize either actual Zhuyin symbols or raw keys from the
    standard Taiwanese Zhuyin keyboard.

    Examples:
        ㄞˋ      -> ㄞ
        ㄒㄧㄥˊ   -> ㄒㄧㄥ
        sm       -> ㄋㄩ
        2k       -> ㄉㄜ
    """
    normalized = text.strip().lower()

    contains_zhuyin = bool(
        re.search(
            r"[\u3105-\u312f\u31a0-\u31bf]",
            normalized,
        )
    )

    # If the user typed raw Latin/number keyboard keys,
    # convert them into Zhuyin first.
    if not contains_zhuyin:
        normalized = standard_keyboard_to_zhuyin(
            normalized
        )

    for tone_mark in ZHUYIN_TONE_MARKS:
        normalized = normalized.replace(
            tone_mark,
            "",
        )

    normalized = re.sub(
        r"[^\u3105-\u312f\u31a0-\u31bf]",
        "",
        normalized,
    )

    return normalized


INITIALS = {
    "b": "ㄅ",
    "p": "ㄆ",
    "m": "ㄇ",
    "f": "ㄈ",
    "d": "ㄉ",
    "t": "ㄊ",
    "n": "ㄋ",
    "l": "ㄌ",
    "g": "ㄍ",
    "k": "ㄎ",
    "h": "ㄏ",
    "j": "ㄐ",
    "q": "ㄑ",
    "x": "ㄒ",
    "zh": "ㄓ",
    "ch": "ㄔ",
    "sh": "ㄕ",
    "r": "ㄖ",
    "z": "ㄗ",
    "c": "ㄘ",
    "s": "ㄙ",
}

FINALS = {
    "a": "ㄚ",
    "o": "ㄛ",
    "e": "ㄜ",
    "ai": "ㄞ",
    "ei": "ㄟ",
    "ao": "ㄠ",
    "ou": "ㄡ",
    "an": "ㄢ",
    "en": "ㄣ",
    "ang": "ㄤ",
    "eng": "ㄥ",
    "er": "ㄦ",

    "i": "ㄧ",
    "ia": "ㄧㄚ",
    "ie": "ㄧㄝ",
    "iao": "ㄧㄠ",
    "iu": "ㄧㄡ",
    "ian": "ㄧㄢ",
    "in": "ㄧㄣ",
    "iang": "ㄧㄤ",
    "ing": "ㄧㄥ",
    "iong": "ㄩㄥ",

    "u": "ㄨ",
    "ua": "ㄨㄚ",
    "uo": "ㄨㄛ",
    "uai": "ㄨㄞ",
    "ui": "ㄨㄟ",
    "uan": "ㄨㄢ",
    "un": "ㄨㄣ",
    "uang": "ㄨㄤ",
    "ong": "ㄨㄥ",

    "v": "ㄩ",
    "ve": "ㄩㄝ",
    "van": "ㄩㄢ",
    "vn": "ㄩㄣ",
}


APICAL_VOWEL_INITIALS = {
    "zh",
    "ch",
    "sh",
    "r",
    "z",
    "c",
    "s",
}


def split_pinyin_tone(pinyin):
    """
    Split numbered pinyin into its syllable and tone.

    Examples:
        suo3 -> ("suo", 3)
        de5  -> ("de", 5)
        ai   -> ("ai", None)
    """
    normalized = pinyin.strip().lower()
    normalized = normalized.replace("u:", "v")
    normalized = normalized.replace("ü", "v")

    match = re.fullmatch(
        r"([a-zv]+)([1-5])?",
        normalized,
    )

    if not match:
        return None, None

    syllable = match.group(1)
    tone_text = match.group(2)

    tone = int(tone_text) if tone_text else None

    return syllable, tone


def separate_initial_and_final(syllable):
    """
    Separate a pinyin syllable into its initial and final.
    """
    for initial in (
        "zh",
        "ch",
        "sh",
        "b",
        "p",
        "m",
        "f",
        "d",
        "t",
        "n",
        "l",
        "g",
        "k",
        "h",
        "j",
        "q",
        "x",
        "r",
        "z",
        "c",
        "s",
    ):
        if syllable.startswith(initial):
            return initial, syllable[len(initial):]

    return "", syllable


def normalize_pinyin_final(initial, final):
    """
    Convert pinyin's abbreviated or spelling-dependent finals into
    the forms used by the Zhuyin mapping.
    """
    # Pinyin abbreviations:
    # iu = iou, ui = uei, un = uen.
    # Our FINALS table already maps the abbreviated spellings.

    # j/q/x + u actually represents ü.
    if initial in {"j", "q", "x"}:
        if final == "u":
            final = "v"
        elif final == "ue":
            final = "ve"
        elif final == "uan":
            final = "van"
        elif final == "un":
            final = "vn"

    # y and w are pinyin spelling devices rather than Zhuyin initials.
    return final


Y_FINALS = {
    "yi": "i",
    "ya": "ia",
    "ye": "ie",
    "yao": "iao",
    "you": "iu",
    "yan": "ian",
    "yin": "in",
    "yang": "iang",
    "ying": "ing",
    "yong": "iong",
    "yu": "v",
    "yue": "ve",
    "yuan": "van",
    "yun": "vn",
}

W_FINALS = {
    "wu": "u",
    "wa": "ua",
    "wo": "uo",
    "wai": "uai",
    "wei": "ui",
    "wan": "uan",
    "wen": "un",
    "wang": "uang",
    "weng": "ong",
}

TONE_MARKS = {
    1: "",
    2: "ˊ",
    3: "ˇ",
    4: "ˋ",
    5: "˙",
    None: "",
}


def pinyin_to_zhuyin(pinyin, include_tone=True):
    """
    Convert one numbered pinyin syllable to Zhuyin.

    Examples:
        ai4   -> ㄞˋ
        xing2 -> ㄒㄧㄥˊ
        suo3  -> ㄙㄨㄛˇ
    """
    syllable, tone = split_pinyin_tone(pinyin)

    if not syllable:
        return None

    if syllable in Y_FINALS:
        initial = ""
        final = Y_FINALS[syllable]

    elif syllable in W_FINALS:
        initial = ""
        final = W_FINALS[syllable]

    else:
        initial, final = separate_initial_and_final(
            syllable,
        )

        final = normalize_pinyin_final(
            initial,
            final,
        )

    initial_zhuyin = INITIALS.get(initial, "")

    # In zhi, chi, shi, ri, zi, ci, and si, the written pinyin "i"
    # has no separate ㄧ symbol in Zhuyin.
    if (
        initial in APICAL_VOWEL_INITIALS
        and final == "i"
    ):
        final_zhuyin = ""
    else:
        final_zhuyin = FINALS.get(final)

    if final_zhuyin is None:
        return None

    zhuyin = initial_zhuyin + final_zhuyin

    if include_tone:
        tone_mark = TONE_MARKS.get(tone, "")

        # Neutral tone is traditionally placed before the syllable.
        if tone == 5:
            zhuyin = tone_mark + zhuyin
        else:
            zhuyin += tone_mark

    return zhuyin


def standard_keyboard_to_zhuyin(text):
    """
    Convert raw keys from the standard Taiwanese Zhuyin keyboard
    layout into Zhuyin symbols.

    Examples:
        sm   -> ㄋㄩ
        2k6  -> ㄉㄜ
        vu;  -> ㄒㄧㄤ
    """
    converted = []

    for character in text.strip().lower():
        if character in ZHUYIN_TONE_MARKS:
            converted.append(character)
            continue

        mapped_character = STANDARD_ZHUYIN_KEYBOARD.get(
            character
        )

        if mapped_character:
            converted.append(mapped_character)

    return "".join(converted)


def get_accepted_pinyin_answers(card):
    accepted = set()

    for pronunciation in card.get("pinyin", []):
        normalized = normalize_pinyin_without_tone(
            pronunciation,
        )

        if normalized:
            accepted.add(normalized)

    return accepted


def get_accepted_zhuyin_answers(card):
    accepted = set()

    for pronunciation in card.get("pinyin", []):
        zhuyin = pinyin_to_zhuyin(
            pronunciation,
            include_tone=False,
        )

        if zhuyin:
            accepted.add(
                normalize_zhuyin_without_tone(zhuyin)
            )

    return accepted


def grade_pronunciation_answer(
    card,
    user_answer,
    input_system,
):
    """
    Grade either a pinyin or Zhuyin answer.
    """
    if input_system == "pinyin":
        normalized_answer = (
            normalize_pinyin_without_tone(
                user_answer,
            )
        )

        accepted_answers = (
            get_accepted_pinyin_answers(card)
        )

        return normalized_answer in accepted_answers

    if input_system == "zhuyin":
        normalized_answer = (
            normalize_zhuyin_without_tone(
                user_answer,
            )
        )

        accepted_answers = (
            get_accepted_zhuyin_answers(card)
        )

        return normalized_answer in accepted_answers

    raise ValueError(
        f"Unsupported input system: {input_system}"
    )


if __name__ == "__main__":
    print("contains_zhuyin('ㄋㄩ'):", contains_zhuyin("ㄋㄩ"))
    print("contains_zhuyin('sm'):", contains_zhuyin("sm"))

    print(
        "standard_keyboard_to_zhuyin('sm'):",
        standard_keyboard_to_zhuyin("sm"),
    )

    print(
        "remove_zhuyin_tones('ㄋㄩˇ'):",
        remove_zhuyin_tones("ㄋㄩˇ"),
    )

    print(
        "normalize_zhuyin_without_tone('sm'):",
        normalize_zhuyin_without_tone("sm"),
    )

    print(
        "normalize_zhuyin_without_tone('ㄋㄩˇ'):",
        normalize_zhuyin_without_tone("ㄋㄩˇ"),
    )

    print(
        "pinyin_to_zhuyin('nv3'):",
        pinyin_to_zhuyin("nv3"),
    )
