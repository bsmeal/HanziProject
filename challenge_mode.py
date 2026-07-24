import json
import random
from pathlib import Path

from assessment import (
    display_card_result,
    grade_pinyin_answer,
)


project_folder = Path(__file__).parent
cards_file = project_folder / "data" / "cards.json"


def load_unranked_cards(file_path):
    """
    Load cards that do not have a numerical frequency rank.

    These cards are excluded from the ranked assessment and used only
    in the separate challenge mode.
    """
    with open(file_path, encoding="utf-8") as file:
        cards = json.load(file)

    unranked_cards = []

    for card in cards:
        frequency = card.get("frequency")

        if frequency is None:
            unranked_cards.append(card)
            continue

        rank = frequency.get("rank")

        if not isinstance(rank, int):
            unranked_cards.append(card)

    return unranked_cards


def create_challenge_session():
    """
    Create the state for an endless unranked challenge session.
    """
    return {
        "used_characters": set(),
        "answers": [],
        "correct_streak": 0,
        "incorrect_streak": 0,
    }


def ask_for_pinyin():
    """
    Ask the user to enter tone-free pinyin.

    Entering q ends the challenge session.
    """
    while True:
        answer = input(
            "Enter the pinyin without a tone number "
            "(or q to quit): "
        ).strip()

        if answer:
            return answer

        print("Please enter a pinyin answer or q.")


def choose_unranked_card(cards, used_characters):
    """
    Choose a random unranked character that has not yet appeared in
    the current cycle.
    """
    available_cards = [
        card
        for card in cards
        if card["character"] not in used_characters
    ]

    if not available_cards:
        return None

    return random.choice(available_cards)


def record_challenge_answer(
    session,
    card,
    user_answer,
    correct,
):
    """
    Record a challenge answer without affecting the ranked estimate.
    """
    if correct:
        session["correct_streak"] += 1
        session["incorrect_streak"] = 0
    else:
        session["incorrect_streak"] += 1
        session["correct_streak"] = 0

    session["used_characters"].add(card["character"])

    session["answers"].append(
        {
            "question_number": len(session["answers"]) + 1,
            "character": card["character"],
            "user_answer": user_answer,
            "correct": correct,
        }
    )


def display_challenge_result(card, user_answer, correct):
    """
    Display the result using the same format as assessment mode.

    Because an unranked card has no numerical frequency rank, a
    temporary display copy is created with an 'Unranked' marker.
    """
    display_card = card.copy()

    frequency = display_card.get("frequency")

    if not isinstance(frequency, dict):
        frequency = {}

    display_card["frequency"] = frequency.copy()
    display_card["frequency"]["rank"] = "Unranked"

    display_card_result(
        card=display_card,
        user_answer=user_answer,
        correct=correct,
    )


def display_challenge_summary(session):
    """
    Display challenge results when the user quits.
    """
    total_answers = len(session["answers"])

    correct_answers = sum(
        1
        for answer in session["answers"]
        if answer["correct"]
    )

    incorrect_answers = total_answers - correct_answers

    print("\nUnranked Challenge Summary")
    print("=" * 52)
    print(f"Characters attempted: {total_answers}")
    print(f"Recognized: {correct_answers}")
    print(f"Not recognized: {incorrect_answers}")

    if total_answers:
        accuracy = correct_answers / total_answers * 100
        print(f"Accuracy: {accuracy:.1f}%")

    print()
    print(
        "These results do not affect your ranked-character "
        "knowledge estimate."
    )
    print("=" * 52)


def run_challenge_mode():
    cards = load_unranked_cards(cards_file)

    if not cards:
        print("No unranked challenge characters were found.")
        return

    session = create_challenge_session()

    print("Unranked Character Challenge Mode")
    print("=" * 52)
    print(
        "Enter any valid pinyin pronunciation for the character."
    )
    print(
        "Tone numbers and tone marks are ignored in this mode."
    )
    print(
        "These characters have no numerical frequency rank."
    )
    print(
        "Your answers here do not affect your ranked estimate."
    )
    print(
        "The session continues until you enter q."
    )

    while True:
        card = choose_unranked_card(
            cards,
            session["used_characters"],
        )

        # Once every unranked character has appeared, clear the set and
        # begin another randomized cycle.
        if card is None:
            session["used_characters"].clear()

            card = choose_unranked_card(
                cards,
                session["used_characters"],
            )

        if card is None:
            print("No unranked cards could be selected.")
            break

        question_number = len(session["answers"]) + 1

        print("\n" + "=" * 52)
        print(f"Challenge Question {question_number}")
        print(
            f"Recognized so far: "
            f"{sum(answer['correct'] for answer in session['answers'])}"
            f"/{len(session['answers'])}"
        )
        print()
        print(f"                 {card['character']}")
        print()

        user_answer = ask_for_pinyin()

        if user_answer.lower() == "q":
            break

        correct = grade_pinyin_answer(
            card,
            user_answer,
        )

        record_challenge_answer(
            session=session,
            card=card,
            user_answer=user_answer,
            correct=correct,
        )

        display_challenge_result(
            card=card,
            user_answer=user_answer,
            correct=correct,
        )

        correct_count = sum(
            answer["correct"]
            for answer in session["answers"]
        )

        print(
            f"Unranked characters recognized: "
            f"{correct_count}/{len(session['answers'])}"
        )

        if correct:
            print(
                f"Correct streak: "
                f"{session['correct_streak']}"
            )
        else:
            print(
                f"Incorrect streak: "
                f"{session['incorrect_streak']}"
            )

        input("\nPress Enter for the next character...")

    display_challenge_summary(session)


if __name__ == "__main__":
    run_challenge_mode()
