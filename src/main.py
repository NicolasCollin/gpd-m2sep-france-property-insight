from src.interface.menu import app_menu  # Import the main menu interface

# --- Application Entry Point ---
def get_welcome_message() -> str:
    # Define the welcome message displayed when the app starts
    return "Welcome to FPI app!"

def main():
    # Initialize and launch the main application through the menu
    app = app_menu()
    app.launch()

# Run the application if executed directly
if __name__ == "__main__":
    main()
