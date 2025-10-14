from src import main


def test_get_welcome_message():
    assert main.get_welcome_message() == "Welcome to FPI app!"
