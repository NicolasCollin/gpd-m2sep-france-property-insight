def get_welcome_message() -> str:
    return "Welcome to FPI app!"


def main() -> None:
    welcome: str = get_welcome_message()
    print(welcome)


if __name__ == "__main__":
    main()
