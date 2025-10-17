"""
aliases.py
-----------
Provides command-line shortcut functions for common development tasks in the France Property Insight project.

These commands automate routine operations such as running pre-commit checks,
building the Docker container, type checking, auditing dependencies, and executing tests.
"""

import subprocess  # For running shell commands


def precommit() -> None:  # Run pre-commit on all files
    subprocess.run(["uv", "run", "pre-commit", "run", "--all-files"], check=False)  # Execute pre-commit


def fpibuild() -> None:  # Build FPI app with Docker
    subprocess.run(
        ["uv", "run", "docker-compose", "-f", ".devcontainer/compose.yaml", "up", "-d", "--build"],  # Docker compose up
        check=False,
    )


# docker-compose -f .devcontainer/compose.yaml up -d --build


def fpirun() -> None:
    subprocess.run(["uv", "run", "docker", "exec", "-it", "fpi-devcontainer", "uv", "run", "main"])


# docker exec -it fpi-devcontainer uv run main


def typecheck() -> None:  # Run type checking with mypy
    subprocess.run(["uv", "run", "mypy", "src"])  # Execute mypy


def audit() -> None:  # Run security audit
    subprocess.run(["uv", "run", "pip-audit", "."])  # Check vulnerabilities


def test() -> None:  # Run all tests
    subprocess.run(["uv", "run", "pytest", "--doctest-modules"])  # Execute pytest
