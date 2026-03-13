# AgentOS: Command Reference 🚀

This document lists all the essential commands for running and developing AgentOS.

## 🐳 Infrastructure (Docker)
Run these from the root directory to start the database, redis, and vector store.

**Start all services:**
```bash
docker compose -f docker/docker-compose.yml up -d
```

**Stop all services:**
```bash
docker compose -f docker/docker-compose.yml down
```

---

## ⚙️ Backend (FastAPI)
Run these from the `backend/` directory.

**Start the API Server:**
```bash
uv run python main.py
```

**Run Celery Worker (Windows/Solo):**
```bash
$env:PYTHONPATH="src"; uv run celery -A agentos.core.orchestrator.celery_app worker --loglevel=info -P solo
```

**Run Celery Worker (Linux/macOS):**
```bash
PYTHONPATH=src uv run celery -A agentos.core.orchestrator.celery_app worker --loglevel=info
```

---

## 🖥️ Dashboard (Frontend)
Run these from the `dashboard/` directory.

**Install Dependencies:**
```bash
npm install
```

**Start Development Server:**
```bash
npm run dev
```

---

## 🧪 Verification & Testing
Run these from the `backend/` directory.

**Test Tools (Built-ins):**
```bash
$env:PYTHONPATH="src"; uv run python test_builtins.py
```

**Test Memory (Redis Threads):**
```bash
$env:PYTHONPATH="src"; uv run python test_memory.py
```

**Test Long-term Memory (Qdrant RAG):**
```bash
$env:PYTHONPATH="src"; uv run python test_vector.py
```

**Test MCP Integration:**
```bash
$env:PYTHONPATH="src"; uv run python test_mcp_integration.py
```

**API Manual Test (Bash/curl):**
```bash
curl -X POST http://127.0.0.1:8000/agent/run \
     -H "Content-Type: application/json" \
     -d '{
          "input": "My name is Urvish. Remember this!",
          "thread_id": "session-123",
          "tools": ["write_file"]
         }'
```
