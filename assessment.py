import json
import math
import random
import re
import unicodedata


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


def normalize_pinyin(text):
    """
    Normalizes pinyin for tone-free recognition mode

    Examples:
        ai4     -> ai
        ài      -> ai
        XING2   -> xing
        lu:4    -> lv
        lü4     -> lv
        lv4     -> lv

    Tone numbers, tone marks, spaces, and punctuation are ignored
    """
    normalized = text.strip().lower()

    # Normalizes the common ways of writing ü
    normalized = normalized.replace("u:", "v")
    normalized = normalized.replace("ü", "v")

    # Separates accented letters from their tone marks
    normalized = unicodedata.normalize("NFD", normalized)

    # Removes accent marks
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    # Keeps only letters. This removes tone numbers and punctuation
    normalized = re.sub(r"[^a-zv]", "", normalized)

    return normalized


def get_accepted_pinyin(card):
    """
    Returns the normalized set of accepted pronunciations for a card
    """
    accepted_answers = set()

    for pronunciation in card.get("pinyin", []):
        normalized = normalize_pinyin(pronunciation)

        if normalized:
            accepted_answers.add(normalized)

    return accepted_answers


def grade_pinyin_answer(card, user_answer):
    """
    Returns True when the user's tone-free pinyin matches any accepted
    pronunciation for the character
    """
    normalized_answer = normalize_pinyin(user_answer)
    accepted_answers = get_accepted_pinyin(card)

    return normalized_answer in accepted_answers


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
            "normalized_answer": normalize_pinyin(user_answer),
            "accepted_answers": sorted(get_accepted_pinyin(card)),
            "correct": correct,
            "estimated_rank": round(session["estimated_rank"]),
        }
    )


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
    print(
        f"Frequency rank: "
        f"{card['frequency']['rank']:,}"
    )

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
