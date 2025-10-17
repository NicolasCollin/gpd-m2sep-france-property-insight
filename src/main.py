import os

from src.interface.menu import app_menu


def get_welcome_message() -> str:
    """
    Return the welcome message displayed when the application starts.

    Returns:
        str: A welcome message for the FPI app.
    """
    return "Welcome to FPI app!"


def amain():
    """
    Welcome user, initialize and launch the main application.

    This function creates the Gradio app menu and starts the interface.
    """
    welcome_message: str = get_welcome_message()
    print(welcome_message)

    app = app_menu()
    app.launch()
    # app.launch(share=True, server_name="0.0.0.0", server_port=7860)


def main():
    """
    Welcome user, initialize and launch the main application.

    Detects if running inside Docker to adjust Gradio launch parameters.
    """
    welcome_message = get_welcome_message()
    print(welcome_message)

    app = app_menu()

    # Detect Docker environment via env variable
    if os.getenv("RUNNING_IN_DOCKER") == "1":
        app.launch(share=True, server_name="0.0.0.0", server_port=7860)
    else:
        app.launch()


# Runs main function when this file is called directly.
if __name__ == "__main__":
    main()
