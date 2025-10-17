import subprocess


def precommit() -> None:
    """uv run precommit shortcut to run on all files"""
    subprocess.run(["uv", "run", "pre-commit", "run", "--all-files"], check=False)


def fpi() -> None:
    """uv run fpi shortcut to build and run fpi app with Docker"""
    subprocess.run(
        ["uv", "run", "docker", "compose", "-f", ".devcontainer/compose.yaml", "up", "--build"],
        check=False,
    )


def typecheck() -> None:
    """uv run typecheck to run mypy tests"""
    subprocess.run(["uv", "run", "mypy", "src"])


def audit() -> None:
    """uv run audit to run pip-audit vuln checks"""
    subprocess.run(["uv", "run", "pip-audit", "."])


def test() -> None:
    """uv run test to run our tests"""
    subprocess.run(["uv", "run", "pytest", "--doctest-modules"])
