# https://docs.docker.com/go/dockerfile-reference/

ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies.
COPY pyproject.toml uv.lock ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD uv run main
