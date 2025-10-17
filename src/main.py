from src.interface.menu import app_menu  # Import the main menu interface


# --- Application Entry Point ---
def get_welcome_message() -> str:
    """
    Return the welcome message displayed when the application starts.

    Returns:
        str: A welcome message for the FPI app.
    """
    return "Welcome to FPI app!"


def main():
    """
    Initialize and launch the main application.

    This function creates the Gradio app menu and starts the interface.
    """
    app = app_menu()
    app.launch()


# Run the application if executed directly
if __name__ == "__main__":
    main()
