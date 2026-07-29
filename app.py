import os
from pathlib import Path

from flask import (
    Flask,
    render_template,
    session,
)

from core.assessment import (
    choose_next_rank,
    find_card_near_rank,
    get_ranked_cards,
    load_cards,
)


app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "development-secret-key",
)

project_folder = Path(__file__).parent
cards_file = project_folder / "data" / "cards.json"

cards = load_cards(cards_file)
ranked_cards = get_ranked_cards(cards)


@app.route("/")
def home():
    return render_template(
        "index.html",
    )


@app.route("/setup")
def setup():
    return render_template(
        "setup.html",
    )


@app.route("/assessment")
def assessment():
    return render_template(
        "assessment.html",
    )


@app.route("/api/card/<int:target_rank>")
def get_card(target_rank):
    card = find_card_near_rank(
        ranked_cards=ranked_cards,
        target_rank=target_rank,
        used_characters=set(),
    )

    if card is None:
        return {
            "error": "No ranked card could be found.",
        }, 404

    return card


@app.route("/api/assessment/start", methods=["POST"])
def start_assessment():
    session.clear()

    session["estimated_rank"] = 1.0
    session["correct_streak"] = 0
    session["incorrect_streak"] = 0
    session["last_answer_correct"] = None
    session["used_characters"] = []
    session["current_character"] = None

    return {
        "message": "Assessment session started.",
        "estimated_rank": session["estimated_rank"],
    }


@app.route("/api/assessment/next")
def next_assessment_card():
    if "estimated_rank" not in session:
        return {
            "error": "No assessment session has been started.",
        }, 400

    max_rank = max(
        card["frequency"]["rank"]
        for card in ranked_cards
    )

    assessment_state = {
        "estimated_rank": session["estimated_rank"],
        "correct_streak": session["correct_streak"],
        "incorrect_streak": session["incorrect_streak"],
        "last_answer_correct": session["last_answer_correct"],
    }

    target_rank = choose_next_rank(
        session=assessment_state,
        max_rank=max_rank,
    )

    used_characters = set(
        session.get("used_characters", [])
    )

    card = find_card_near_rank(
        ranked_cards=ranked_cards,
        target_rank=target_rank,
        used_characters=used_characters,
    )

    if card is None:
        return {
            "error": "No ranked card could be selected.",
        }, 404

    session["current_character"] = card["character"]
    session["current_rank"] = card["frequency"]["rank"]

    recent_characters = session.get(
        "used_characters",
        [],
    )

    recent_characters.append(card["character"])

    # Keep only recent cards so the browser cookie stays small.
    session["used_characters"] = recent_characters[-20:]

    return {
        "character": card["character"],
        "frequency_rank": card["frequency"]["rank"],
        "estimated_rank": round(
            session["estimated_rank"]
        ),
    }
