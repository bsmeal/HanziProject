import json
from collections import defaultdict
from pathlib import Path
from core.pronunciation import pinyin_to_zhuyin


project_folder = Path(__file__).parent

cedict_file = (
    project_folder
    / "data"
    / "cedict_ts.u8"
)

output_file = (
    project_folder
    / "data"
    / "vocabulary_candidates.json"
)


def parse_cedict_entry(line):
    """
    Parse one CC-CEDICT line.

    Returns a dictionary for a multi-character Traditional Chinese
    vocabulary word, or None when the line is unusable.
    """
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    pinyin_start = line.find("[")
    pinyin_end = line.find("]")

    meaning_start = line.find("/")
    meaning_end = line.rfind("/")

    if (
        pinyin_start == -1
        or pinyin_end == -1
        or meaning_start == -1
        or meaning_end == -1
    ):
        return None

    before_pinyin = line[:pinyin_start].strip()
    word_parts = before_pinyin.split()

    if len(word_parts) < 2:
        return None

    traditional = word_parts[0]

    # We only want vocabulary words, not single-character entries.
    if len(traditional) < 2:
        return None

    # Keep only entries composed entirely of CJK characters.
    if not all(
        "\u3400" <= character <= "\u9fff"
        for character in traditional
    ):
        return None

    pinyin = line[
        pinyin_start + 1:pinyin_end
    ].strip()

    meaning_text = line[
        meaning_start + 1:meaning_end
    ]

    meanings = [
        meaning.strip()
        for meaning in meaning_text.split("/")
        if meaning.strip()
    ]

    filtered_meanings = []

    for meaning in meanings:
        lowercase_meaning = meaning.lower()

        if lowercase_meaning.startswith("surname"):
            continue

        if lowercase_meaning.startswith("see "):
            continue

        if lowercase_meaning.startswith("variant of"):
            continue

        filtered_meanings.append(meaning)

    if not filtered_meanings:
        return None

    return {
        "word": traditional,
        "pinyin": pinyin,
        "zhuyin": phrase_pinyin_to_zhuyin(
            pinyin
        ),
        "meanings": filtered_meanings,
    }


def phrase_pinyin_to_zhuyin(pinyin):
    """
    Convert space-separated numbered pinyin into a Zhuyin phrase.

    Example:
        ai4 qing2 -> ㄞˋ ㄑㄧㄥˊ
    """
    zhuyin_syllables = []

    for syllable in pinyin.split():
        zhuyin = pinyin_to_zhuyin(
            syllable,
            include_tone=True,
        )

        if zhuyin is None:
            return ""

        zhuyin_syllables.append(zhuyin)

    return " ".join(zhuyin_syllables)


def build_vocabulary_index(cedict_path):
    """
    Build a mapping from each character to all multi-character
    vocabulary entries containing that character.
    """
    vocabulary_index = defaultdict(list)
    seen_entries = set()

    with open(
        cedict_path,
        encoding="utf-8",
    ) as file:
        for line in file:
            entry = parse_cedict_entry(line)

            if entry is None:
                continue

            word = entry["word"]

            entry_key = (
                word,
                entry["pinyin"],
            )

            if entry_key in seen_entries:
                continue

            seen_entries.add(entry_key)

            # set(word) prevents the same word being added twice when a
            # character appears more than once inside it.
            for character in set(word):
                vocabulary_index[character].append(
                    entry
                )

    return vocabulary_index


def save_vocabulary_index(
    vocabulary_index,
    file_path,
):
    """
    Save vocabulary candidates as JSON.
    """
    serializable_data = dict(
        sorted(vocabulary_index.items())
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            serializable_data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def main():
    print(
        f"Building vocabulary candidates from: "
        f"{cedict_file}"
    )

    vocabulary_index = build_vocabulary_index(
        cedict_file
    )

    save_vocabulary_index(
        vocabulary_index,
        output_file,
    )

    print(
        f"Created vocabulary candidates for "
        f"{len(vocabulary_index):,} characters."
    )

    print(
        f"Saved vocabulary data to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()
