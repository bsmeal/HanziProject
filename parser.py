import json
from pathlib import Path

from metadata import (
    load_metadata,
    add_hsk_level,
    load_frequency_data,
    add_frequency_data,
)


project_folder = Path(__file__).parent

data_file = project_folder / "data" / "cedict_ts.u8"
output_file = project_folder / "data" / "cards.json"
hsk_file = project_folder / "data" / "hsk.json"
frequency_file = project_folder / "data" / "cuhk_taiwan_frequency.txt"

# Use a dictionary so every character has only one card.
cards = {}

print(f"Processing file: {data_file}")

with open(data_file, encoding="utf-8") as f:
    for line in f:
        # Skip comments and empty lines.
        if line.startswith("#") or not line.strip():
            continue

        parts = line.split(maxsplit=1)

        if len(parts) < 2:
            continue

        character = parts[0]

        # Only keep entries containing one Hanzi character.
        if len(character) != 1 or not ("\u4e00" <= character <= "\u9fff"):
            continue

        entry = line.strip()

        # Extract Pinyin from [ ].
        pinyin_start = entry.find("[")
        pinyin_end = entry.find("]")

        if pinyin_start == -1 or pinyin_end == -1:
            continue

        pinyin = entry[pinyin_start + 1:pinyin_end].strip()

        if not pinyin:
            continue

        # Extract meanings from / ... /.
        meaning_start = entry.find("/")
        meaning_end = entry.rfind("/")

        if meaning_start == -1 or meaning_end == -1:
            continue

        meaning_text = entry[meaning_start + 1:meaning_end]

        meanings = meaning_text.split("/")
        meanings = [meaning.strip() for meaning in meanings]
        meanings = [meaning for meaning in meanings if meaning]

        filtered_meanings = []

        for meaning in meanings:
            if meaning.lower().startswith("surname"):
                continue

            filtered_meanings.append(meaning)

        if character not in cards:
            cards[character] = {
                "character": character,
                "pinyin": [],
                "meanings": [],
            }

        cards[character]["pinyin"].append(pinyin)
        cards[character]["meanings"].extend(filtered_meanings)

print(f"Successfully parsed {len(cards)} cards.")

# Convert the dictionary into a list for JSON.
cards = list(cards.values())

# Remove duplicate pronunciations and meanings.
for card in cards:
    card["pinyin"] = list(dict.fromkeys(card["pinyin"]))
    card["meanings"] = list(dict.fromkeys(card["meanings"]))

# Load and apply HSK metadata.
# hsk_data = load_metadata(hsk_file)
# cards = add_hsk_level(cards, hsk_data)

# Load and apply Taiwanese frequency metadata.
frequency_data = load_frequency_data(frequency_file)
cards = add_frequency_data(cards, frequency_data)

# Save the completed cards.
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=4)

print(f"Saved {len(cards)} cards to '{output_file}'")
