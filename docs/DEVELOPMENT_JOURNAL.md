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

## 🛡️ Phase 3.3: Retry and Failure Handling
**Date:** March 12, 2026
**Status:** ✅ Completed

### What we did
- Implemented **Automatic Retries** in Celery with exponential backoff (e.g., if LLM is down, wait before retrying).
- Synced **Task IDs**: The database UUID is now used as the Celery Task ID, allowing direct revocation.
- Added a **Cancellation Endpoint**: `POST /tasks/{id}/cancel` can now stop a "runaway" agent immediately.
- Improved **Persistence**: The `retry_count` is now visibly tracked in the database for every task.

### Why we did it
- **Resilience**: In the real world, APIs fail. Retries ensure that a 1-second network blip doesn't kill a complex agent reasoning task.
- **Cost & Control**: If a user realizes they sent an expensive or wrong prompt, they need a way to stop it before the agent spends all their tokens. Cancellation is our "Emergency Stop" button.
- **Observability**: Seeing a `retry_count` of 2 on a task helps developers identify unstable agents or providers immediately.

---

## 🛠️ Phase 4.1: Tool Registry & RAO Cycle
**Date:** March 12, 2026
**Status:** ✅ Completed

### What we did
- Created a **Tool Registry** system that allows us to define functions that agents can call.
- Implemented a **Reason-Act-Observe (RAO)** loop using LangGraph. Agents can now choose to call a tool, wait for the result, and then continue thinking.
- Upgraded **AgentState** to use a message reducer (`operator.add`), allowing the agent to remember the entire conversation history, including tool results.
- Verified the loop with a built-in `get_weather` tool.

### Why we did it
- **Agency**: Without tools, an agent is just a chatbot. Tools give the agent "hands" to interact with API, databases, and the internet.
- **Workflow Control**: Using LangGraph allows us to define strict state transitions, making the agent's behavior more predictable and easier to debug than a raw LLM loop.
- **Context Preservation**: Properly managing message history is critical for complex tasks. If an agent forgets why it called a tool, it gets stuck in a loop.

---

## 🌐 Phase 4.2: MCP Client Integration
**Date:** March 12, 2026
**Status:** ✅ Completed

### What we did
- Implemented **MCPManager**, a dedicated service to manage connections to external **Model Context Protocol** servers.
- Built a bridge that automatically discovers tools from MCP servers and registers them in our global `ToolRegistry`.
- Updated **AgentRuntime** to support asynchronous tool execution, which is required for MCP communication.
- Wired MCP initialization into both the **FastAPI API** and **Celery Workers**, ensuring agents have access to tools across the entire platform.
- Verified the integration using a custom local MCP server (`test_mcp_server.py`).

### Why we did it
- **Ecosystem Access**: MCP is becoming the industry standard for LLM tools. By supporting it, AgentOS can immediately use hundreds of existing tools (Postgres, Slack, GitHub, etc.) without writing custom code for each.
- **Process Isolation**: MCP servers run as separate processes (Stdio), which is more secure and stable than loading arbitrary code directly into the backend.
- **Scalability**: Supporting async tool calls ensures that the backend can handle many concurrent agent runs without blocking on slow external API responses.

---

## 🛠️ Phase 4.3: Built-in Tools Implementation
**Date:** March 12, 2026
**Status:** ✅ Completed

### What we did
- Created a `builtins` package containing core tools for every AgentOS agent.
- Implemented **Sandboxed Filesystem** tools (`read_file`, `write_file`, `list_directory`) that restrict operations to a configurable `./storage/agents` directory.
- Implemented **Python Executor** tool, allowing agents to run arbitrary Python code in a child process. This is the foundation for "self-evolving" agents that can create their own tools.
- Implemented **HTTP Request** tool using `httpx` for raw web interaction.
- Implemented **Tavily Search** tool for high-quality, agent-optimized web search.
- Configured **ToolRegistry** to automatically load and register these tools on system startup.

### Why we did it
- **Standard Library**: Every OS needs a standard library. These tools provide the "out-of-the-box" utility that makes AgentOS immediately useful for developers.
- **Safety**: By sandboxing file access, we ensure that agents (and the LLMs powering them) cannot accidentally or maliciously damage the host system or access sensitive configuration files.
- **Strategic Foundation**: The Python Executor is the first step toward the "Master Agent" concept—allowing agents to write and test their own logic dynamically.

---

## 🧠 Phase 5.1: Short-term Memory & Caching
**Date:** March 13, 2026
**Status:** ✅ Completed

### What we did
- Implemented **RedisMemory** to persist agent conversations across turns using a `thread_id`.
- Implemented **RedisCache** for LLM response caching, significantlly reducing latency and token costs for repeated prompts.
- Added **Idempotency** logic to ensure that duplicate requests or retries don't trigger redundant agent runs.
- Updated **AgentRuntime** to automatically load history at start and save turn results at completion.
- Exposed `thread_id` in the API for client-side session management.

### Why we did it
- **Continuity**: Agents need context to be truly useful. Without short-term memory, every message is a fresh start, making long workflows impossible.
- **Production Efficiency**: LLM Caching is a standard production practice. It makes the system feel much faster for common queries and saves money.
- **Reliability (Kubernetes Vision)**: Idempotency is a core principle of reliable distributed systems. As we build "Kubernetes for Agents," we must ensure that our execution logic is deterministic and safe to retry.

---

## 📚 Phase 5.2: Long-term Memory (Qdrant)
**Date:** March 13, 2026
**Status:** ✅ Completed

### What we did
- Integrated **Qdrant** as the primary vector database for long-term knowledge storage.
- Used **FastEmbed** for local, high-performance embedding generation, eliminating the need for external embedding APIs.
- Implemented `save_to_knowledge_base` and `query_knowledge_base` tools.
- Enabled agents to actively manage their own memory by storing and searching contextual snippets.

### Why we did it
- **Knowledge Persistence**: Short-term memory eventually overflows or resets. Long-term memory allows agents to build a permanent knowledge base that grows with every interaction.
- **RAG Capability**: This is the foundation for agents that can reason over private documents, past project notes, or any other large-scale data without stuffing it all into the prompt.
- **Privacy & Cost**: FastEmbed runs locally, ensuring that private knowledge remains on the machine and doesn't incur per-token embedding costs.

---

## 🔌 Phase 5.3: Memory API & Auto-RAG
**Date:** March 13, 2026
**Status:** ✅ Completed

### What we did
- Implemented REST API routes for long-term memory management (`/memory/upsert`, `/memory/search`, `/memory/points`).
- Integrated "Auto-RAG" into the `AgentRuntime` reasoning loop.
- Added `auto_rag` flag to the agent run request, enabling automatic context lookup from the vector database.
- Successfully verified that agents can answer questions using injected context without explicitly calling a tool.

### Why we did it
- **Integration Flexibility**: Exposing the knowledge base via API allows external systems (or a frontend dashboard) to populate or query agent knowledge independently.
- **Enhanced Intelligence**: Auto-RAG ensures agents are always grounded with relevant long-term knowledge from the very first message, reducing the need for multiple reasoning turns and improving response quality.
- **Efficiency**: Context injection happens before the LLM call, saving the cost and latency of a separate "tool calling" turn just to fetch knowledge.

---

## 📊 Phase 6.2: Metrics Collection (Prometheus)
**Date:** March 13, 2026
**Status:** ✅ Completed

### What we did
- Integrated **Prometheus** for real-time metrics collection using the `prometheus-client` library.
- Defined custom metrics: `agentos_tokens_total` (Counter), `agentos_execution_time_seconds` (Histogram), `agentos_tasks_total` (Counter), and `agentos_cost_usd_total` (Counter).
- Exposed a dedicated `/metrics` endpoint in the FastAPI application for scraping by Prometheus.
- Integrated metrics recording directly into the `AgentRuntime.run()` method to capture data for every agent execution.
- Implemented a basic **Cost Estimation** engine that maps token usage to USD based on provider and model.
- Configured `prometheus_client.multiprocess.MultiProcessCollector` to allow the FastAPI server to correctly report metrics generated by background Celery worker processes.

### Why we did it
- **Observability**: Logging tells you *what* happened; metrics tell you *how* it's performing over time. This is critical for identifying bottlenecks (e.g., slow LLM responses) or usage spikes.
- **Cost Control**: AI tokens are expensive. By tracking cost in real-time, we provide immediate visibility into spending, which is a prerequisite for the budget gating we plan for Phase 13.
- **Standardization**: Prometheus is the industry standard for cloud-native monitoring. By exposing metrics in this format, AgentOS can be easily plugged into existing Grafana dashboards.
- **Performance Tuning**: The execution time histogram allows us to see the distribution of response times, helping us decide when to switch models or providers for better latency.

---

## 🔍 Phase 6.3: Reasoning Traces & OpenTelemetry
**Date:** March 13, 2026
**Status:** ✅ Completed

### What we did
- Implemented **OpenTelemetry (OTel)** instrumentation for the entire backend stack.
- Configured **FastAPIInstrumentor** to automatically capture API request spans.
- Created custom **nested spans** in `AgentRuntime` to track:
    - Overall `agent_run`.
    - Every `reason_node` (LLM thinking) turn.
    - Every `action_node` (Tool execution) turn.
    - Individual tool calls (e.g., `tool_call:list_agents`).
- Synchronized **trace_id** and **span_id** across both traces and structured logs.
- Integrated `structlog` with the current OTel context.
- Added `trace_id` to the `Task` database model and schema to persist the reasoning trace ID during background Celery execution.
- Created the `GET /tasks/{task_id}/trace` endpoint to automatically expose Jaeger tracing URLs to the frontend.

### Why we did it
- **Observability-by-default**: As defined in the Vision docs, AgentOS must be "transparent." Tracing allows developers to see exactly how a high-level goal was broken down into steps.
- **Log Correlation**: In a busy system with thousands of agents, looking at flat logs is impossible. By injecting the `trace_id` into every log line, we allow developers to "grep" for a specific request ID and see every log related to that reasoning chain combined with the trace.
- **Performance Debugging**: Traces provide a visual timeline. If an agent takes 5 seconds, the trace shows exactly which step (LLM vs Tool vs Memory) was the bottleneck.

---

## 🔒 Phase 6.4: Immutable Audit Logging
**Date:** March 14, 2026
**Status:** ✅ Completed

### What we did
- Created an `AuditLogger` to record sensitive actions (e.g. agent registry changes, tool executions) to an append-only JSONL file.
- Implemented a **cryptographic hash chain**, where each log entry contains the SHA-256 hash of the previous entry.
- Created `verify_audit_chain()` to detect any tampering with the log file history.
- Instrumented `agents.py` and `runtime.py` to capture actor, action, resource, and `trace_id` for every sensitive event.

### Why we did it
- **Compliance & Security**: AI agents executing actions need a non-repudiable audit trail. By using a hash chain, we ensure that if a malicious actor modifies a past log, the chain breaks and the system detects the tampering.
- **MVP Simplicity**: For v0.1, an append-only file with a mathematical hash chain provides robust guarantees without the heavy infrastructure of a ledger database like AWS QLDB.

---

## 📊 Phase 7.1: Base Evaluation Pipeline
**Date:** March 15, 2026
**Status:** ✅ Completed

### What we did
- Defined the core **Evaluation Schema** using SQLModel, introducing `EvaluationBatch` and `EvaluationCase`.
- Implemented the `SimpleEvaluator` for heuristic-based scoring (keyword matching and response length).
- Created the **Evaluation Service** to handle sequential batch execution and agent output capture.
- Added foundational API endpoints for running single and batch evaluations.

### Why we did it
- **Consistency**: We needed a standardized way to run agents against a set of prompts and capture their success/failure.
- **Baseline for Improvement**: Simple heuristic scoring provides a "floor" for evaluation, ensuring agents meet basic criteria before applying expensive LLM-based metrics.
- **Workflow Automation**: Automating the "Run -> Score -> Save" loop saves developers hours of manual testing.

---

## 🔬 Phase 7.2: Advanced Framework Integration
**Date:** March 16, 2026
**Status:** ✅ Completed

### What we did
- Integrated **RAGAS** and **DeepEval** frameworks to support semantic metrics like `Faithfulness` and `Answer Relevancy`.
- Implemented a **Factory Pattern** for evaluators, allowing the system to scale to new frameworks easily.
- Enhanced the `AgentRuntime` to pass retrieved context snippets directly into the evaluation loop for multi-referential scoring.
- Verified semantic grounding using simulated RAG workflows.

### Why we did it
- **Beyond Keywords**: Modern RAG systems cannot be evaluated by keyword matching alone. Semantic metrics are required to detect if an answer is actually supported by the context.
- **Modular Scalability**: By using adapters for RAGAS and DeepEval, we can swap frameworks or update versions without breaking the core evaluation engine.
- **Grounding Verification**: This phase ensures that the "Retrieval" part of RAG is actually contributing to "Generation" quality.

---

## 📈 Phase 7.3: Reporting & Retrieval API
**Date:** March 16, 2026
**Status:** ✅ Completed

### What we did
- Built the **Reporting Service** (`reporting.py`) to calculate pass rates, average scores per metric, and cumulative token usage.
- Created a **Premium HTML Report** generator with modern HSL color schemes, grid layouts, and responsive tables.
- Updated the `Evaluation` model to follow LangChain's latest `usage_metadata` schema for granular cost analysis.
- Exposed detailed **Batch Retrieval** endpoints to allow browsing historical runs and downloading machine-readable (JSON) or human-readable (HTML) reports.

### Why we did it
- **Cost & Performance Visibility**: Tracking token usage across batches is a prerequisite for production deployment and budget management.
- **Stakeholder Trust**: Transparent, beautiful reports make it easier for non-technical users to understand agent performance and identify failure modes visually.
- **Analytics Foundation**: Exposing these metrics via API allows the frontend dashboard to build trend visualizations and comparison charts.

---

## 🛠️ Phase 8.1: CLI Interface (The Developer Swiss Army Knife)
**Date:** March 17, 2026
**Status:** ✅ Completed

### What we did
- Implemented a modular CLI using **Typer** and **Rich**.
- Built a centralized **API Client** (`client.py`) using `httpx` to communicate with the AgentOS Backend.
- Created three primary command groups:
    - `init`: Generates a sample `agent.yaml` for a "Day Zero" quickstart.
    - `agents`: Supports `list` (Rich table view) and `register` (YAML/JSON config upload).
    - `tasks`: Supports `run` (real-time polling loop), `status`, `cancel`, and `trace` (direct Jaeger links).
- Configured **uv** integration in `pyproject.toml` to install `agentos` as a global command in the virtual environment.
- Documented everything in a comprehensive [CLI_MANUAL.md](../docs/CLI_MANUAL.md).

### Why we did it
- **Developer Velocity**: Reading/writing raw JSON against API endpoints is slow. The CLI provides a high-level, human-friendly interface that lets developers iterate on agents in seconds.
- **Reproducibility (IaC)**: By using YAML-based registration, agents are treated as code. You can version them, share them, and deploy them to any environment using the same CLI command.
- **Transparency**: The `tasks run` command uses a Rich polling loop to show exactly what's happening. The `trace` command bridges the gap between the terminal and deep observability (Jaeger), making debugging seamless.
- **Automation Ready**: The CLI is designed to be called from bash scripts and CI/CD pipelines, fulfilling our vision of "Kubernetes for Agents" by providing a reliable administrative tool.

---

## 🐍 Phase 8.2: Python SDK (Programmatic Integration)
**Date:** March 17, 2026
**Status:** ✅ Completed

### What we did
- Designed a **Resource-based Architecture** for the SDK, grouping logic under `agents`, `tasks`, and `memory`.
- Implemented a **Dual-Mode Client** (`AgentOS`) that supports both synchronous (`httpx.Client`) and asynchronous (`httpx.AsyncClient`) workflows.
- Created high-level developer helpers, most notably `client.tasks.run_and_wait()`, which abstracts away the polling and state check complexity.
- Ensured full type hinting and Pydantic-friendly data handling across all resources.
- Verified the SDK with a comprehensive test suite covering both sync and async execution paths.

### Why we did it
- **Developer Experience (DX)**: While a CLI is great for humans, application developers need a native library. The SDK allows them to integrate AgentOS into their web apps, data pipelines, or bots with just a few lines of Python.
- **Future-Proofing (Async)**: Modern Python web frameworks (FastAPI, Starlette) are async-first. Providing native `async/await` support ensures the SDK is performant and doesn't block the event loop in high-throughput applications.
- **Complexity Abstraction**: The `run_and_wait` pattern is the most common use case for an agent. By building it into the SDK, we save every developer from writing their own `while True: sleep(1)` polling code.
- **Foundation for Phase 10**: The upcoming Next.js Dashboard and potential Python-based control planes will rely on this SDK as their primary communication layer.
385: 
386: ---
387: 
388: ## 🔌 Phase 9.1: Plugin Architecture (Extensibility)
389: **Date:** March 17, 2026
390: **Status:** ✅ Completed
391: 
392: ### What we did
393: - Implemented a modular **Plugin Manager** capable of dynamic discovery and loading from a root `plugins/` directory.
394: - Defined **Abstract Base Classes (ABCs)** for different plugin types: `ToolPlugin`, `EvaluatorPlugin`, and `MemoryPlugin`.
395: - Integrated the plugin loading sequence into the FastAPI `on_startup` lifecyle to ensure process-safe registration.
396: - Exposed a new **API Endpoint** (`GET /plugins/`) for system introspection.
397: - Added the `agentos plugins list` **CLI command** to provide a unified view of active extensions.
398: - Verified the system with a sample `WeatherPlugin` that auto-registers on backend startup.
399: 
400: ### Why we did it
401: - **Extensibility**: AI infrastructure must be open. By allowing developers to "drop-in" Python files, we enable a community-driven ecosystem of tools and evaluators.
402: - **Decoupling**: Core AgentOS logic should not know about specific external tools. Plugins provide a clean boundary where integrations are maintained separately from the engine.
403: - **Introspection**: A platform that supports plugins must provide tools to audit them. The new API and CLI commands ensure operators know exactly what's "under the hood" at any given time.
404: - **Roadmap Alignment**: This phase lays the groundwork for Phase 9.2 (Unified Plugin Registry) and the eventual goal of an AgentOS Marketplace.
