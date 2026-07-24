import json
import random
from pathlib import Path


project_folder = Path(__file__).parent
cards_file = project_folder / "data" / "cards.json"


def load_unranked_cards(file_path):
    """
    Load cards that have no usable frequency rank.
    """
    with open(file_path, encoding="utf-8") as file:
        cards = json.load(file)

    unranked_cards = []

    for card in cards:
        frequency = card.get("frequency")

        if frequency is None:
            unranked_cards.append(card)
            continue

        if frequency.get("rank") is None:
            unranked_cards.append(card)

    return unranked_cards


def display_answer(card):
    print("\nAnswer")
    print("-" * 40)
    print(f"Character: {card['character']}")
    print(f"Pinyin: {', '.join(card.get('pinyin', []))}")

    print("Meanings:")

    for meaning in card.get("meanings", []):
        print(f"  - {meaning}")

    print("-" * 40)


def run_challenge_mode():
    cards = load_unranked_cards(cards_file)

    if not cards:
        print("No unranked challenge characters were found.")
        return

    random.shuffle(cards)

    recognized = 0
    attempted = 0

    print("Unranked Character Challenge")
    print("=" * 40)
    print(
        "These characters are not included in the ranked frequency "
        "assessment."
    )
    print(
        "Correct or incorrect answers here do not change your "
        "ranked-character estimate."
    )

    for card in cards:
        print("\n" + "=" * 40)
        print(f"Challenge character: {card['character']}")

        input("Press Enter to reveal the answer...")

        display_answer(card)

        while True:
            answer = input(
                "Did you recognize it? "
                "(y = yes, n = no, q = quit): "
            ).strip().lower()

            if answer in {"y", "n", "q"}:
                break

            print("Please enter y, n, or q.")

        if answer == "q":
            break

        attempted += 1

        if answer == "y":
            recognized += 1

        print(
            f"Unranked characters recognized: "
            f"{recognized}/{attempted}"
        )

    print("\nChallenge summary")
    print("=" * 40)
    print(f"Attempted: {attempted}")
    print(f"Recognized: {recognized}")
    print(f"Not recognized: {attempted - recognized}")


if __name__ == "__main__":
    run_challenge_mode()
