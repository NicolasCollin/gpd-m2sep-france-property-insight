import os

from src.interface.menu import app_menu


def get_welcome_message() -> str:
    """
    Get the welcome message displayed when the application starts.

    Returns:
        str: A welcome message for the FPI app.
    """
    return "Welcome to FPI app!"


def main() -> None:
    """
    Welcome user, initialize and launch the main application.

    Detects if running inside Docker to adjust Gradio launch parameters.
    """
    welcome_message: str = get_welcome_message()
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
