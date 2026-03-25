# Stage 1: Build virtual environment
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies into a robust virtual environment
COPY pyproject.toml uv.lock ./
RUN uv venv /opt/venv && \
    VIRTUAL_ENV=/opt/venv uv sync --no-dev --no-install-project

# Copy code and install project
COPY src/ ./src/
COPY main.py ./
RUN VIRTUAL_ENV=/opt/venv uv pip install -e .

# Stage 2: Runtime image
FROM python:3.13-slim
WORKDIR /app

# Copy the venv and source
COPY --from=builder /opt/venv /opt/venv
COPY src/ /app/src/
COPY main.py /app/main.py

# Put virtualenv in path
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
RUN mkdir -p $PROMETHEUS_MULTIPROC_DIR

EXPOSE 8000

# Default command: FastAPI server
CMD ["python", "main.py"]
