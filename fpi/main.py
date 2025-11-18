import os
import webbrowser

import gradio as gr
import uvicorn
from fastapi import FastAPI

from fpi.interface.menu import app_menu
from fpi.utils.api import app as api_app


def launch_app(host: str, port: int) -> None:
    """
    Create and run the FastAPI app with Gradio UI mounted.

    Args:
        host (str): Host to bind the server to.
        port (int): Port to bind the server to.
    """
    fastapi_app = FastAPI(title="FPI Unified App")

    # Mount backend API
    fastapi_app.mount("/api", api_app)

    # Create Gradio app
    gradio_app = app_menu()

    # Mount Gradio UI at root
    gr.mount_gradio_app(fastapi_app, gradio_app, path="/")

    if os.getenv("RUNNING_IN_DOCKER") == "1":
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
        print("Running inside Docker: Gradio exposed publicly via 0.0.0.0")
    else:
        custom_url = f"http://{host}:{port}/?view=settings&__theme=light"
        webbrowser.open(custom_url)
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


def main() -> None:
    """
    Entry point for the FPI application.
    Sets host and port depending on environment, prints info, and launches the server.
    """
    port = 7860
    host = "0.0.0.0" if os.getenv("RUNNING_IN_DOCKER") == "1" else "127.0.0.1"
    custom_url = f"http://{host}:{port}/?view=settings&__theme=light"

    print("Welcome to FPI!")
    print("Press `Ctrl + C` in the terminal if you want to stop the app")
    print(f"Gradio interface will be available at: {custom_url}")
    print(f"FastAPI docs will be available at http://{host}:{port}/api/docs")

    launch_app(host, port)


if __name__ == "__main__":
    main()
