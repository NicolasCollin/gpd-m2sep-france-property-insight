import subprocess


def precommit() -> None:
    """uv run precommit shortcut to run on all files"""
    subprocess.run(["uv", "run", "pre-commit", "run", "--all-files"], check=False)


def fpibuild() -> None:
    """uv run fpibuild shortcut to build and run fpi app with Docker"""
    subprocess.run(
        [
            "uv",
            "run",
            "docker",
            "compose",
            "-f",
            ".devcontainer/compose.yaml",
            "run",
            "--rm",
            "-it",
            "server",
        ],
        check=False,
    )
