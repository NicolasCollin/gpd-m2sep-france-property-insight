from src.interface.menu import app_menu  # Import menu


def get_welcome_message() -> str:
    return "Welcome to FPI app!"  # Welcome message


def main():
    app = app_menu()  # Create app
    app.launch()  # Run app


if __name__ == "__main__":
    main()  # Entry point
