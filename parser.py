with open("data/cedict_ts.u8", encoding="utf-8") as file:
    for line in file:
        if line.startswith("#"):
            continue

        parts = line.split()

        character = parts[0]

        if len(character) == 1 and "\u4e00" <= character <= "\u9fff":
            entry = line.strip()

            pinyin_start = entry.find("[")
            pinyin_end = entry.find("]")
            pinyin = entry[pinyin_start+1:pinyin_end]

            meaning_start = entry.find("/")
            meaning_end = entry.rfind("/")
            meaning = entry[meaning_start+1:meaning_end]
            break

print(f"Character:\n{character}\n")
print(f"Pinyin:\n{pinyin}\n")
print(f"Meaning:\n{meaning}")

card = {
    "character": character,
    "pinyin": pinyin,
    "meaning": meaning
}
