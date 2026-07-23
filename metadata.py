import json
from pathlib import Path


def load_metadata(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def add_hsk_level(cards, hsk_data):
    for card in cards:
        character = card["character"]
        card["hsk"] = hsk_data.get(character)

    return cards


def load_frequency_data(file_path):
    frequency_data = {}

    text = Path(file_path).read_text(
        encoding="utf-8",
        errors="replace",
    )

    for line in text.splitlines():
        parts = line.strip().split("\t")

        if len(parts) != 10:
            continue

        character = parts[0]
        rank_text = parts[1]

        if len(character) != 1 or not rank_text.isdigit():
            continue

        frequency_data[character] = {
            "rank": int(parts[1]),
            "strokes": int(parts[3]),
            "count": int(parts[4]),
            "percentage": float(parts[5].rstrip("%")),
            "cumulative_count": int(parts[6]),
            "cumulative_percentage": float(parts[7].rstrip("%")),
            "document_count": int(parts[8]),
            "document_percentage": float(parts[9].rstrip("%")),
            "source": "CUHK Taiwan 1980s-1990s",
        }

    return frequency_data


def add_frequency_data(cards, frequency_data):
    for card in cards:
        character = card["character"]
        card["frequency"] = frequency_data.get(character)

    return cards
