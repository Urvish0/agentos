# AgentOS 🤖
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-3130/)

Open-source infrastructure platform for deploying, orchestrating, monitoring, and evaluating AI agents.

AgentOS provides a robust, stateful execution environment for LLM agents built with LangGraph, orchestrated via Celery, and managed through a high-performance FastAPI backend.

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.13+
- `uv` (Fast Python package manager)
- Docker (for Postgres, Redis, Qdrant)

### 2. Infrastructure Setup
Spin up the required background services:
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. Backend Setup
Install dependencies and run the backend:
```bash
cd backend
uv sync
cp .env.example .env  # Add your LLM API keys (GROQ_API_KEY, TAVILY_API_KEY)
uv run python main.py
```
*The API is now running at `http://localhost:8000`.*

### 4. Dashboard Setup (Optional)
Run the Next.js UI:
```bash
cd dashboard
npm install
npm run build
npm start
```

### 5. Run Your First Task
With the backend running, use the CLI to run tasks:
```bash
cd backend
# View registered agents
agentos agents list

# Run a task
agentos tasks run researcher --input "What are the latest developments in quantum computing?"
```
*(For full SDK examples, check the `examples/` directory).*

## 📚 Documentation
- [Architecture Vision & Design](docs/architecture/VISION.md)
- [API Reference](docs/API_REFERENCE.md)
- [CLI Manual](docs/CLI_MANUAL.md)

## 🤝 Contributing
Please see our [Contributing Guidelines](CONTRIBUTING.md) to get started!
