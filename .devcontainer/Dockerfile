ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/

# Expose port if needed (for Streamlit later)
EXPOSE 8000

# Run interactive terminal app directly
CMD ["/app/.venv/bin/python", "src/main.py"]
