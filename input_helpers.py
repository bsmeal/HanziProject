def choose_input_system():
    """
    Ask the user whether they want to answer with pinyin or Zhuyin.
    """
    while True:
        print("\nChoose an input system:")
        print("1. Pinyin")
        print("2. Zhuyin / Bopomofo")

        choice = input("> ").strip()

        if choice == "1":
            return "pinyin"

        if choice == "2":
            return "zhuyin"

        print("Please enter 1 or 2.")


def ask_for_pronunciation(input_system):
    """
    Ask for a pronunciation according to the selected input system.
    """
    if input_system == "pinyin":
        prompt = (
            "Enter the pinyin without a tone "
            "(or q to quit): "
        )
    elif input_system == "zhuyin":
        prompt = (
            "Enter the Zhuyin without a tone mark "
            "(or q to quit): "
        )
    else:
        raise ValueError(
            f"Unsupported input system: {input_system}"
        )

    while True:
        answer = input(prompt).strip()

        if answer:
            return answer

        print("Please enter an answer or q.")


def display_input_instructions(input_system):
    """
    Display instructions that match the selected input system.
    """
    if input_system == "pinyin":
        print(
            "Enter any valid pinyin pronunciation for the character."
        )
    elif input_system == "zhuyin":
        print(
            "Enter any valid Zhuyin pronunciation for the character."
        )
    else:
        raise ValueError(
            f"Unsupported input system: {input_system}"
        )

    print(
        "Tone numbers and tone marks are ignored in this mode."
    )
