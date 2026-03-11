# AgentOS: Development Journal & Learning Log

> **Note to self and fellow learners**: This document tracks the evolution of AgentOS. For every phase, we explain **what** we built and **why** we chose that specific path. 

---

## 🏗️ Phase 1: Project Initialization
**Date:** March 10, 2026
**Status:** ✅ Completed

### What we did
- Initialized a monorepo structure with `backend` (Python/FastAPI) and `dashboard` (Next.js).
- Set up `uv` for lightning-fast Python dependency management.
- Configured Docker Compose with PostgreSQL (metadata), Redis (queue/memory), and Qdrant (vectors).
- Created a robust FastAPI app factory and a `main.py` entry point.

### Why we did it
- **Monorepo**: Keeping backend and frontend in one place makes it easier to keep them in sync as features grow.
- **UV**: Standard `pip` and `requirements.txt` are slow and can lead to "dependency hell." `uv` is the modern standard for reproducibility and speed.
- **Docker for Deps**: We chose to run databases in Docker but code locally. This gives us the best of both worlds: a clean, consistent database environment without the slow "rebuild container/copy code" loop during development.
- **FastAPI Factory**: Using a factory function (`create_app`) allows us to easily create different app instances for testing vs. production.

---

## 🧠 Phase 2.1: Agent Runtime Engine (The Brain)
**Date:** March 11, 2026
**Status:** ✅ Completed

### What we did
- Integrated **Groq** via `langchain-groq` for ultra-fast open-source LLM inference.
- Implemented the core engine using **LangGraph**.
- Built an LLM abstraction layer (`llm.py`) and a stateful execution loop (`runtime.py`).
- Added a `POST /agent/run` endpoint to trigger the brain.

### Why we did it
- **Groq**: We want AgentOS to be fast. Groq's LPU (Language Processing Unit) offers the lowest latency for Llama 3 and Mixtral, making agents feel "snappy" and real-time.
- **LangGraph**: Traditional AI chains (like standard LangChain) are linear. Agents, however, need to "loop" — they think, act, and observe. LangGraph is a state machine that handles these cyclic reasoning loops perfectly.
- **LLM Abstraction**: In the AI world, today's best model is tomorrow's legacy. By building an abstraction (`get_llm`), we can swap Groq for OpenAI, Anthropic, or even a local Llama model in 5 minutes without touching the core runtime logic.
- **Traceability**: We designed the `AgentState` to record every "thought." This isn't just for debugging; it’s for building trust. Users need to see *how* an agent reached a conclusion.

---

## 📂 Phase 2.2 & 2.3: Agent Manager (Registry & API)
**Date:** March 11, 2026
**Status:** ✅ Completed

### What we did
- Set up **SQLModel** (SQLAlchemy + Pydantic) for PostgreSQL-backed storage.
- Created a robust Agent model with versioning and configuration fields.
- Implemented a Service Layer (`service.py`) for all CRUD (Create, Read, Update, Delete) operations.
- Built RESTful API endpoints in `api/routes/agents.py`.
- Fixed a silent bug in the Docker healthcheck for PostgreSQL.

### Why we did it
- **SQLModel**: We chose SQLModel because it combines the power of SQLAlchemy (for database operations) with Pydantic (for data validation). This means we write our data models **once** and they work for both the database and the API.
- **Service Layer Pattern**: Instead of putting database code directly in our API routes, we put it in `service.py`. This makes the code cleaner, easier to test, and reusable (the CLI we build later can use the same services).
- **Versioning**: By adding a `version` field to agents from the start, we ensure that as agents evolve, their configurations can be tracked and managed professionally.
- **Healthcheck Fix**: A noisy error in Docker logs (`database "agentos" does not exist`) was caused by the healthcheck command defaulting to the username. Specifying `-d agentos_db` fixed the diagnostic spam, ensuring we have a clean development environment.

---

## ⚙️ Phase 2.4: Runtime Configuration System
**Date:** March 11, 2026
**Status:** ✅ Completed

### What we did
- Created a **centralized Pydantic Settings** config (`config.py`) that loads all settings from `.env`.
- Refactored `llm.py` with a **multi-provider registry** supporting Groq, OpenAI, and Anthropic.
- Added a `POST /agent/run/stream` endpoint for **Server-Sent Events (SSE)** streaming.
- Wired config into `main.py`, `database.py`, and `app.py` — eliminating all scattered `os.getenv` calls.

### Why we did it
- **Pydantic Settings**: Instead of having `os.getenv("GROQ_API_KEY")` scattered across 5 different files, we now have one `config` object. Import it anywhere, and you get type-safe, validated settings. If a critical key is missing, the app fails **at startup** instead of crashing mid-request.
- **Multi-Provider Registry**: We used a **Dictionary of Functions** pattern. Each provider (groq, openai, anthropic) maps to a factory function. To add a new provider, you just add one entry to the dict — no `if/elif` chains.
- **Lazy Imports**: OpenAI and Anthropic use `from langchain_openai import ...` **inside** their factory functions, not at the top of the file. This means the app doesn't crash if you haven't installed `langchain-openai` — it only fails when you actually try to use it.
- **SSE Streaming**: Instead of waiting 3-5 seconds for the full response, users can see tokens arrive in real-time. This uses `async for chunk in self.llm.astream(messages)` — LangChain's built-in streaming. The API wraps it as Server-Sent Events, the web standard for real-time data.

---

## 📋 Phase 3.1: Task Lifecycle Model
**Date:** March 11, 2026
**Status:** ✅ Completed

### What we did
- Defined a **7-state Task Lifecycle**: `created`, `queued`, `running`, `paused`, `completed`, `failed`, and `cancelled`.
- Implemented a **Strict State Machine** in `orchestrator/models.py` with validated transitions.
- Created a **Service Layer** (`service.py`) that rejects illegal operations (e.g., trying to run a completed task).
- Added a full set of **Task API Routes** for lifecycle management.

### Why we did it
- **State Machine Foundation**: In an asynchronous system (where Celery workers will be running tasks), you cannot allow "race conditions" where two processes try to move a task to different states. A strict state machine ensures the task history is always logical.
- **Separation of Concerns**: Just like with agents, we separated the Task Database logic into a service layer. This allows our background workers to update task status using the same validated logic that the API uses.

---

## ⚡ Phase 3.2: Task Queue Integration (Celery + Redis)
**Date:** March 11, 2026
**Status:** ✅ Completed

### What we did
- Initialized **Celery** as our asynchronous task runner.
- Configured **Redis** as the message broker (to hold tasks) and the results backend.
- Created `run_agent_task` — a background worker function that executes agents without blocking the API.
- Re-wired `POST /tasks/create` so it automatically triggers background execution.

### Why we did it
- **Non-Blocking APIs**: AI agents can take seconds or even minutes to think. If we ran them directly in the API call, the browser/client would time out. By using Celery, the API returns a Task ID **immediately** (in milliseconds), and the agent works in the background.
- **Worker Isolation**: Background tasks run in separate "Worker" processes. This means if an agent crashes or consumes too much memory, it won't crash the main API server.
- **Persistence & Visibility**: Because the worker updates the same PostgreSQL `task` table, the user can refresh their dashboard and see the status change from `queued` to `running` to `completed` in real-time.

---
