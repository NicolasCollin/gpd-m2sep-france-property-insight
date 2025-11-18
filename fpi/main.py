import os

import gradio as gr
import uvicorn

# main.py
from fastapi import FastAPI

from fpi.interface.menu import app_menu
from fpi.utils.api import app as api_app


# new main with FastAPI
def main() -> None:
    port = 7860
    host = "0.0.0.0" if os.getenv("RUNNING_IN_DOCKER") == "1" else "127.0.0.1"

    print("Welcome to FPI!\nPress `Ctrl + C` in the terminal if you want to stop the app")
    print(f"Gradio interface will be available at http://{host}:{port}/")
    print(f"FastAPI docs will be available at http://{host}:{port}/api/docs")

    # Create FastAPI app
    fastapi_app = FastAPI(title="FPI Unified App")

    # Mount your backend API
    fastapi_app.mount("/api", api_app)

    # Create Gradio interface
    gradio_app = app_menu()

    # Mount Gradio at root '/'
    gr.mount_gradio_app(fastapi_app, gradio_app, path="/")

    # Docker adjustments
    if os.getenv("RUNNING_IN_DOCKER") == "1":
        # Share=True equivalent for public access via Gradio tunnel
        uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")
        print("Running inside Docker: Gradio exposed publicly via 0.0.0.0")
    else:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="info")


def old_main() -> None:
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
