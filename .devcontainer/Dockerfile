ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY . .

# Expose port if needed (for Gradio)
EXPOSE 7860

# Run the app
# CMD ["uv", "run", "main"]
