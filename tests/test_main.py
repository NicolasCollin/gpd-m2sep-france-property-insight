from src import main  # Import the main application module


# --- Unit Test for Welcome Message ---
def test_get_welcome_message():
    # Verify that the welcome message returned by the main module is correct
    assert main.get_welcome_message() == "Welcome to FPI app!"
