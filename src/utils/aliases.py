import subprocess


def precommit() -> None:
    """toml shortcut to run pre-commit on all files"""
    subprocess.run(["uv", "run", "pre-commit", "run", "--all-files"], check=False)
