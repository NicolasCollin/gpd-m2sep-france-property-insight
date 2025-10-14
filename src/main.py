def get_welcome_message() -> str:
    return "Welcome to FPI app!"


def main() -> None:
    welcome: str = get_welcome_message()
    print(welcome)
    colour: str = input("what is your favourite colour ?\n")
    print(f"Nice, my favourite colours is also {colour}.")


if __name__ == "__main__":
    main()
