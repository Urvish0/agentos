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

## 📂 Phase 2.2: Agent Manager (Registry)
**Date:** TBD
**Status:** ⏳ Next Up

### What we're doing
- Implementing SQLAlchemy/SQLModel to store agent configurations in PostgreSQL.
- Building CRUD (Create, Read, Update, Delete) APIs for agents.

### Why we're doing it
- A brain needs a "personality" and a "memory of who it is." The Registry allows us to define specific agent types (e.g., "The Python Expert" with a specific system prompt and model) and save them to a database so they can be reused and shared across the platform.

---
