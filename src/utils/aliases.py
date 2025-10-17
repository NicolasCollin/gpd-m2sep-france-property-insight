import subprocess  # For running shell commands


def precommit() -> None:  # Run pre-commit on all files
    subprocess.run(["uv", "run", "pre-commit", "run", "--all-files"], check=False)  # Execute pre-commit


def fpi() -> None:  # Build and run FPI app with Docker
    subprocess.run(
        ["uv", "run", "docker", "compose", "-f", ".devcontainer/compose.yaml", "up", "--build"],  # Docker compose up
        check=False,
    )


def typecheck() -> None:  # Run type checking with mypy
    subprocess.run(["uv", "run", "mypy", "src"])  # Execute mypy


def audit() -> None:  # Run security audit
    subprocess.run(["uv", "run", "pip-audit", "."])  # Check vulnerabilities


def test() -> None:  # Run all tests
    subprocess.run(["uv", "run", "pytest", "--doctest-modules"])  # Execute pytest
