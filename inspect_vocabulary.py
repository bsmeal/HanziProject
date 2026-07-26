import json
from pathlib import Path


project_folder = Path(__file__).parent

vocabulary_file = (
    project_folder
    / "data"
    / "vocabulary_candidates.json"
)


def load_vocabulary():
    with open(
        vocabulary_file,
        encoding="utf-8",
    ) as file:
        return json.load(file)


def show_vocabulary(character, vocabulary_data):
    entries = vocabulary_data.get(
        character,
        [],
    )

    if not entries:
        print(
            f"No vocabulary candidates found for "
            f"{character}."
        )
        return

    print(
        f"\nVocabulary candidates for {character}"
    )
    print("=" * 52)

    for number, entry in enumerate(
        entries,
        start=1,
    ):
        meanings = "; ".join(
            entry.get("meanings", [])
        )

        print(
            f"{number}. {entry['word']}"
        )
        print(
            f"   Pinyin: {entry.get('pinyin', '')}"
        )
        print(
            f"   Zhuyin: {entry.get('zhuyin', '')}"
        )
        print(
            f"   Meanings: {meanings}"
        )
        print()


def main():
    vocabulary_data = load_vocabulary()

    while True:
        character = input(
            "Enter a character "
            "(or q to quit): "
        ).strip()

        if character.lower() == "q":
            break

        if len(character) != 1:
            print(
                "Please enter exactly one character."
            )
            continue

        show_vocabulary(
            character,
            vocabulary_data,
        )


if __name__ == "__main__":
    main()
