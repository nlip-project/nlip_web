import subprocess
import os


def start_server() -> None:
    """Start the FastAPI chat server."""
    subprocess.run(
        [
            "uvicorn",
            "nlip_web.webserver:app",
            "--host", "0.0.0.0",
            "--port", os.environ.get("PORT", "8010"),
            "--reload",
        ],
        check=True,
    )
