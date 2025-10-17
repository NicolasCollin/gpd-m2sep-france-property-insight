from src.interface.menu import app_menu


def get_welcome_message() -> str:
    return "Welcome to FPI app!"


def main():
    app = app_menu()
    app.launch()


if __name__ == "__main__":
    main()
