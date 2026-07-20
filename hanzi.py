def main():
    while True:
        print("1. Start calculating your Hanzi knowledge")
        print("2. Browse flashcards")
        print("3. Exit")

        choice = int(input("Select an option: "))

        if choice == "1":
            calculate_hanzi_knowledge()
        elif choice == "2":
            browse_flashcards()
        else:
            print("Goodbye!")
            break
