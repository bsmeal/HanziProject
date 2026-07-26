import json


def load_language_data(file_path):
    """
    Load vocabulary, example sentences, and historical citations
    from language_data.json.

    Return an empty dictionary if the file does not exist so the
    parser can still run without enrichment data.
    """
    if not file_path.exists():
        print(f"Language data file not found: {file_path}")
        print(
            "Continuing without vocabulary, examples, "
            "or historical citations."
        )
        return {}

    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def add_language_data(cards, language_data):
    """
    Attach vocabulary, examples, and historical citations to cards.

    Vocabulary is limited to three entries per character.
    """
    for card in cards:
        character = card["character"]
        character_data = language_data.get(character, {})

        card["vocabulary"] = character_data.get(
            "vocabulary",
            [],
        )[:3]

        card["examples"] = character_data.get(
            "examples",
            [],
        )

        card["historical_citations"] = character_data.get(
            "historical_citations",
            [],
        )

    return cards
