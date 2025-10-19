"""
aliases.py
-----------
Command-line shortcut functions for France Property Insight (FPI) project.
Designed to be used with `uv run <script>` defined in pyproject.toml.
"""

import shlex
import subprocess
from typing import Optional


def run_command(command: str, check: bool = False) -> None:
    """Run a shell command given as a single string, splitting safely."""
    print(f"Running: {command}")
    subprocess.run(shlex.split(command), check=check)


def precommit() -> None:
    """Run pre-commit hooks on all files."""
    run_command("uv run pre-commit run --all-files")


def fpibuild() -> None:
    """Build and start the Docker container for FPI."""
    run_command("uv run docker-compose -f .devcontainer/compose.yaml up -d --build")


def fpirun() -> None:
    """Run the FPI app inside the Docker container."""
    run_command("uv run docker exec -it fpi-devcontainer uv run main")


def typecheck(extra_args: Optional[str] = None) -> None:
    """Run static type checking with mypy."""
    cmd = "uv run mypy src"
    if extra_args:
        cmd += f" {extra_args}"
    run_command(cmd)


def audit() -> None:
    """Run a security audit with pip-audit."""
    run_command("uv run pip-audit .")


def test(extra_args: Optional[str] = None) -> None:
    """Run all tests with pytest, including doctests."""
    cmd = "uv run pytest --doctest-modules"
    if extra_args:
        cmd += f" {extra_args}"
    run_command(cmd)


def run_behave() -> None:
    subprocess.run(["behave", "tests/behave/features"], check=True)


def ci() -> None:
    """
    Run a sequence of project commands in order to simulate our GitLab CI pipeline:
    precommit, typecheck, audit, test, run_behave.
    """
    precommit()
    typecheck()
    audit()
    test()
    run_behave()
