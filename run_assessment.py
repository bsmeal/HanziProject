from pathlib import Path

from assessment import (
    choose_next_rank,
    create_session,
    display_card_result,
    display_session_summary,
    find_card_near_rank,
    get_ranked_cards,
    grade_pinyin_answer,
    load_cards,
    record_answer,
)


project_folder = Path(__file__).parent
cards_file = project_folder / "data" / "cards.json"


def ask_for_pinyin():
    """
    Ask the user to enter tone-free pinyin.

    Entering q ends the session.
    """
    while True:
        answer = input(
            "Enter the pinyin without a tone number "
            "(or q to quit): "
        ).strip()

        if answer:
            return answer

        print("Please enter a pinyin answer or q.")


def run_assessment():
    cards = load_cards(cards_file)
    ranked_cards = get_ranked_cards(cards)

    if not ranked_cards:
        print("No ranked cards were found.")
        return

    max_rank = max(
        card["frequency"]["rank"]
        for card in ranked_cards
    )

    session = create_session()

    print("Taiwan Mandarin Character Recognition Mode")
    print("=" * 52)
    print(
        "Enter any valid pinyin pronunciation for the character."
    )
    print(
        "Tone numbers and tone marks are ignored in this mode."
    )
    print(
        "The session continues until you enter q."
    )

    while True:
        target_rank = choose_next_rank(
            session,
            max_rank,
        )

        card = find_card_near_rank(
            ranked_cards,
            target_rank,
            session["used_characters"],
        )

        # This will normally take thousands of questions, but it keeps
        # the mode technically endless by allowing cards to be reused
        # after every ranked character has appeared once.
        if card is None:
            session["used_characters"].clear()

            card = find_card_near_rank(
                ranked_cards,
                target_rank,
                session["used_characters"],
            )

        if card is None:
            print("No ranked cards could be selected.")
            break

        question_number = len(session["answers"]) + 1
        actual_rank = card["frequency"]["rank"]

        print("\n" + "=" * 52)
        print(f"Question {question_number}")
        print(
            f"Current estimate: "
            f"{round(session['estimated_rank']):,}"
        )
        print(f"Tested frequency rank: {actual_rank:,}")
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

        record_answer(
            session=session,
            card=card,
            user_answer=user_answer,
            correct=correct,
            max_rank=max_rank,
        )

        display_card_result(
            card=card,
            user_answer=user_answer,
            correct=correct,
        )

        print(
            f"Updated estimate: "
            f"{round(session['estimated_rank']):,}"
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

    display_session_summary(session)


if __name__ == "__main__":
    run_assessment()
