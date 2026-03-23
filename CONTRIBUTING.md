# Contributing to AgentOS

Welcome to AgentOS! We are thrilled that you want to contribute to the open-source platform for deploying and orchestrating AI agents.

## 🛠️ Development Setup

AgentOS uses modern Python tooling.

### Prerequisites

1. **Python 3.13+**
2. **`uv`** (Astral's fast Python package installer and resolver)
3. **Docker Desktop** (for infrastructure)
4. **Node.js 20+** (if working on the Dashboard)

### Starting the Environment

1. Fork the repository and clone it locally.
2. Spin up the infrastructure components (Postgres, Redis, Qdrant):
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
3. Sync the backend Python environment using `uv`:
   ```bash
   cd backend
   uv sync
   ```
4. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```
   *Note: Add at least your `GROQ_API_KEY` for baseline testing.*

## 📐 Code Style & Standards

We enforce strict validation to maintain the stability of the core runtime.

- **Formatting**: We use `ruff format` and `black`.
- **Linting**: We use `ruff check`.
- **Type Checking**: We use `mypy`. Enforce strict typing in `core/` modules.
- **Testing**: All new features must include `pytest` coverage in the `tests/` directory.

Run checks locally before committing:
```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/agentos
uv run pytest
```

## 🌳 Branching & Pull Requests

1. Create a feature branch off `main` (`git checkout -b feature/your-feature-name`).
2. Write clear, incremental commits.
3. Test your functionality locally, including API, celery, and database interactions.
4. Submit a Pull Request. Ensure your PR description links to any relevant GitHub issues and clearly explains the changes.

## 🧩 Modifying the Architecture

AgentOS is heavily documented. If your change affects the core runtime loop, memory handling, or tool structures, you **must** update the relevant Markdown files in `docs/architecture/` first.

Thank you for helping us build the future of agent infrastructure!
