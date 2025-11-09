import os

import gradio as gr

from fpi.interface.menu import app_menu


def main() -> None:
    """
    Welcome user, initialize and launch the main application.

    Detects if running inside Docker to adjust Gradio launch parameters.
    """
    print("Welcome to FPI!\nPress `Ctrl + C` in the terminal if you want to stop the app")

    app: gr.Blocks = app_menu()

    # Detect Docker environment via env variable
    if os.getenv("RUNNING_IN_DOCKER") == "1":
        app.launch(share=True, server_name="0.0.0.0", server_port=7860, debug=True, allowed_paths=["/docs"])
    else:
        app.launch(allowed_paths=["/docs"])


if __name__ == "__main__":
    main()
