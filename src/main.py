from src.interface.menu import app_menu


def get_welcome_message() -> str:
    """
    Return the welcome message displayed when the application starts.

    Returns:
        str: A welcome message for the FPI app.
    """
    return "Welcome to FPI app!"


def main():
    """
    Welcome user, initialize and launch the main application.

    This function creates the Gradio app menu and starts the interface.
    """
    welcome_message: str = get_welcome_message()
    print(welcome_message)

    app = app_menu()
    app.launch()


# Runs main function when this file is called directly.
if __name__ == "__main__":
    main()
