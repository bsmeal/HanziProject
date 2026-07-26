import json
import math
import random

from pronunciation import pinyin_to_zhuyin


def load_cards(file_path):
    """
    Load all character cards from cards.json
    """
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def get_ranked_cards(cards):
    """
    Returns only cards that have a valid numerical frequency rank

    Null-frequency cards remain excluded because they belong in the
    separate unranked challenge mode
    """
    ranked_cards = []

    for card in cards:
        frequency = card.get("frequency")

        if not frequency:
            continue

        rank = frequency.get("rank")

        if not isinstance(rank, int):
            continue

        ranked_cards.append(card)

    ranked_cards.sort(
        key=lambda card: card["frequency"]["rank"]
    )

    return ranked_cards


def create_session():
    """
    Creates the state for an endless assessment session
    """
    return {
        "estimated_rank": 1.0,
        "used_characters": set(),
        "answers": [],
        "correct_streak": 0,
        "incorrect_streak": 0,
        "last_answer_correct": None,
    }


def update_estimate(session, tested_rank, correct, max_rank):
    """
    Updates the user's estimated ranked-character knowledge

    This uses an Elo-like adaptive calculation

    Important behavior:

    - Correct on an unusually rare character:
        large increase

    - Correct on a very common character:
        small increase

    - Wrong on a common character:
        large decrease

    - Wrong on a very obscure character:
        small decrease

    This matches the intended meaning of the frequency scale
    """
    current_estimate = session["estimated_rank"]

    # The scale grows with the estimate so movement remains meaningful
    # at both low and high frequency ranks
    scale = max(50.0, current_estimate * 0.15)

    # Estimates the probability that the user should know the tested card
    exponent = (tested_rank - current_estimate) / scale

    # Avoids extremely large values being passed into math.exp()
    exponent = max(-60, min(60, exponent))

    expected_probability = 1 / (1 + math.exp(exponent))
    actual_result = 1.0 if correct else 0.0

    learning_rate = scale * 0.9

    adjustment = learning_rate * (
        actual_result - expected_probability
    )

    new_estimate = current_estimate + adjustment

    session["estimated_rank"] = max(
        1.0,
        min(new_estimate, float(max_rank)),
    )


def choose_next_rank(session, max_rank):
    """
    Choose a target near the user's current estimated knowledge.

    Correct answers push the next target somewhat farther into rarity.
    Incorrect answers pull it back toward more common characters.

    Random variation prevents the test from following one completely
    predictable path.
    """
    estimate = session["estimated_rank"]

    # The exploration range grows as the user's estimated knowledge grows
    exploration_window = max(20, int(estimate * 0.12))

    if session["last_answer_correct"] is True:
        forward_amount = max(
            10,
            exploration_window // 2,
        )

        # Rewards consistent correct answers without allowing explosive doubling
        streak_bonus = min(
            session["correct_streak"] * 3,
            exploration_window,
        )

        center = estimate + forward_amount + streak_bonus

    elif session["last_answer_correct"] is False:
        backward_amount = max(
            5,
            exploration_window // 3,
        )

        center = estimate - backward_amount

    else:
        # The first question starts at rank 1.
        return 1

    jitter = random.randint(
        -(exploration_window // 2),
        exploration_window // 2,
    )

    target_rank = round(center + jitter)

    return max(1, min(target_rank, max_rank))


def find_card_near_rank(ranked_cards, target_rank, used_characters):
    """
    Find an unused character whose frequency rank is nearest to the
    requested target.

    If every ranked character has been used, the calling code can clear
    used_characters and continue playing.
    """
    available_cards = [
        card
        for card in ranked_cards
        if card["character"] not in used_characters
    ]

    if not available_cards:
        return None

    return min(
        available_cards,
        key=lambda card: abs(
            card["frequency"]["rank"] - target_rank
        ),
    )


def record_answer(session, card, user_answer, correct, max_rank):
    """
    Store an answer and update all session information.
    """
    rank = card["frequency"]["rank"]

    if correct:
        session["correct_streak"] += 1
        session["incorrect_streak"] = 0
    else:
        session["incorrect_streak"] += 1
        session["correct_streak"] = 0

    update_estimate(
        session=session,
        tested_rank=rank,
        correct=correct,
        max_rank=max_rank,
    )

    session["last_answer_correct"] = correct
    session["used_characters"].add(card["character"])

    session["answers"].append(
        {
            "question_number": len(session["answers"]) + 1,
            "character": card["character"],
            "rank": rank,
            "user_answer": user_answer,
            "correct": correct,
            "estimated_rank": round(
                session["estimated_rank"]
            ),
        }
    )


def get_zhuyin_readings(card):
    """
    Convert every pinyin reading on a card into tone-marked Zhuyin.

    Duplicate readings are removed while preserving their order.
    """
    zhuyin_readings = []

    for pronunciation in card.get("pinyin", []):
        zhuyin = pinyin_to_zhuyin(
            pronunciation,
            include_tone=True,
        )

        if zhuyin and zhuyin not in zhuyin_readings:
            zhuyin_readings.append(zhuyin)

    return zhuyin_readings


def display_vocabulary(card):
    """
    Display up to three vocabulary words containing the character.
    """
    vocabulary_entries = card.get(
        "vocabulary",
        [],
    )

    if not vocabulary_entries:
        return

    print("Vocabulary:")

    for entry in vocabulary_entries[:3]:
        word = entry.get("word", "")
        pinyin = entry.get("pinyin", "")
        zhuyin = entry.get("zhuyin", "")
        meaning = entry.get("meaning", "")

        pronunciation_parts = []

        if pinyin:
            pronunciation_parts.append(pinyin)

        if zhuyin:
            pronunciation_parts.append(zhuyin)

        pronunciation_text = " | ".join(
            pronunciation_parts
        )

        if pronunciation_text and meaning:
            print(
                f"  - {word} "
                f"({pronunciation_text}): "
                f"{meaning}"
            )
        elif pronunciation_text:
            print(
                f"  - {word} "
                f"({pronunciation_text})"
            )
        elif meaning:
            print(f"  - {word}: {meaning}")
        else:
            print(f"  - {word}")


def display_examples(card):
    """
    Display the example sentences stored for a character.
    """
    examples = card.get("examples", [])

    if not examples:
        return

    print("Examples:")

    for example in examples:
        traditional = example.get(
            "traditional",
            "",
        )
        pinyin = example.get(
            "pinyin",
            "",
        )
        zhuyin = example.get(
            "zhuyin",
            "",
        )
        english = example.get(
            "english",
            "",
        )

        if traditional:
            print(f"  {traditional}")

        if pinyin:
            print(f"  Pinyin: {pinyin}")

        if zhuyin:
            print(f"  Zhuyin: {zhuyin}")

        if english:
            print(f"  English: {english}")


def display_historical_citations(card):
    """
    Display historical citations for rare or historical characters.
    """
    citations = card.get(
        "historical_citations",
        [],
    )

    if not citations:
        return

    print("Historical citations:")

    for citation in citations:
        work = citation.get("work", "")
        author = citation.get("author", "")
        dynasty = citation.get("dynasty", "")
        period = citation.get("period", "")
        quotation = citation.get("quotation", "")
        modern_form = citation.get(
            "modern_form",
            "",
        )
        note = citation.get("note", "")
        source = citation.get("source", "")

        heading_parts = [
            part
            for part in (
                work,
                author,
                dynasty,
                period,
            )
            if part
        ]

        if heading_parts:
            print(
                f"  - {' | '.join(heading_parts)}"
            )

        if quotation:
            print(f"    Citation: {quotation}")

        if modern_form:
            print(
                f"    Modern form: {modern_form}"
            )

        if note:
            print(f"    Note: {note}")

        if source:
            print(f"    Source: {source}")


def display_card_result(card, user_answer, correct):
    """
    Display whether the user was correct, followed by all available
    information for the character.
    """
    if correct:
        print("\nCORRECT!")
    else:
        print("\nINCORRECT")

    print("=" * 52)
    print(f"Character: {card['character']}")
    print(f"Your answer: {user_answer}")
    print(
        f"Pinyin: {', '.join(card.get('pinyin', []))}"
    )

    zhuyin_readings = get_zhuyin_readings(card)

    if zhuyin_readings:
        print(
            f"Zhuyin: {', '.join(zhuyin_readings)}"
        )

    rank = card.get("frequency", {}).get("rank")

    if isinstance(rank, int):
        print(f"Frequency rank: {rank:,}")
    else:
        print("Frequency rank: Unranked")

    frequency = card.get("frequency", {})

    if frequency.get("count") is not None:
        print(f"Corpus count: {frequency['count']:,}")

    if frequency.get("strokes") is not None:
        print(f"Strokes: {frequency['strokes']}")

    tocfl = card.get("tocfl")

    if tocfl is not None:
        print(f"TOCFL: {tocfl}")

    hsk = card.get("hsk")

    if hsk is not None:
        print(f"HSK: {hsk}")

    print("Meanings:")

    for meaning in card.get("meanings", []):
        print(f"  - {meaning}")

    if card.get("vocabulary"):
        print()
        display_vocabulary(card)

    if card.get("examples"):
        print()
        display_examples(card)

    if card.get("historical_citations"):
        print()
        display_historical_citations(card)

    print("=" * 52)


def display_session_summary(session):
    """
    Display the current session result when the user quits.
    """
    total_answers = len(session["answers"])

    correct_answers = sum(
        1
        for answer in session["answers"]
        if answer["correct"]
    )

    incorrect_answers = total_answers - correct_answers

    print("\nSession summary")
    print("=" * 52)
    print(
        f"Estimated ranked character knowledge: "
        f"{round(session['estimated_rank']):,}"
    )
    print(f"Characters attempted: {total_answers}")
    print(f"Correct: {correct_answers}")
    print(f"Incorrect: {incorrect_answers}")

    if total_answers:
        accuracy = correct_answers / total_answers * 100
        print(f"Accuracy: {accuracy:.1f}%")

    print("=" * 52)
