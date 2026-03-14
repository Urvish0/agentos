# AgentOS: Master Development Roadmap

> **Purpose**: This is the single-source-of-truth roadmap for building AgentOS. It is designed to be read by **any LLM or developer** joining the project at any phase. Each phase has clear inputs, outputs, and dependencies so work can be resumed from any checkpoint.

---

## 🧠 Context for LLMs

> [!IMPORTANT]
> **Read these docs FIRST** before writing any code. They define the architecture, requirements, and design patterns for the entire system.

| Document | Path | Purpose |
|:---|:---|:---|
| **Vision** | `docs/architecture/VISION.md` | Strategic goals and core philosophy |
| **ARS** | `docs/architecture/ARS.md` | Architecture requirements, features, and integration strategy |
| **Journal** | `docs/DEVELOPMENT_JOURNAL.md` | **Learning Log: What we built & Why** |
| **URS** | `docs/architecture/URS.md` | User personas, stories, and journeys |
| **SRS** | `docs/architecture/SRS.md` | Functional and non-functional system requirements with acceptance criteria |
| **System Architecture** | `docs/architecture/SYSTEM_ARCHUTECTURE.md` | High-level component diagram, data flows, and deployment architecture |
| **Component Design** | `docs/architecture/COMPONENT_DESIGN.md` | Low-level design of each module (API Gateway, Runtime, Memory, etc.) |
| **Repo Architecture** | `docs/architecture/REPO_ARCHITECTURE.md` | Directory structure and package layout |
| **MVP Definition** | `docs/architecture/MVP_DEFINITION.md` | Scope of v0.1 — what's in and what's out |
| **Implementation Plan** | `docs/architecture/IMPLEMENTATION_PLAN.md` | Phased engineering blueprint |
| **Dev Roadmap** | `docs/architecture/DEVELOPMENT_ROADMAP.md` | Step-by-step development phases |

### Project Tech Stack

| Layer | Technology | Notes |
|:---|:---|:---|
| **Backend Language** | Python 3.13+ | All core modules |
| **API Framework** | FastAPI | Async, high-performance |
| **Agent Framework** | LangGraph | Core reasoning loop |
| **Task Queue** | Celery + Redis | Async task orchestration |
| **Database** | PostgreSQL | Agent registry, task history |
| **Vector DB** | Qdrant | Long-term agent memory |
| **Cache/Memory** | Redis | Short-term memory, session state |
| **Observability** | structlog, OpenTelemetry | Logging and tracing |
| **Dashboard** | Next.js 16 (React 19, TypeScript, Tailwind 4) | Web UI |
| **Package Manager** | `uv` (backend), `npm` (dashboard) | |
| **Containerization** | Docker Compose | Local development services |

### Repository Structure

```text
agentos/
├── backend/
│   ├── main.py                    # Uvicorn entry point
│   ├── pyproject.toml             # Python dependencies
│   └── src/agentos/
│       ├── api/                   # FastAPI app factory, routes, schemas, middleware
│       ├── core/
│       │   ├── runtime/           # LangGraph execution engine
│       │   ├── orchestrator/      # Task scheduling & lifecycle
│       │   ├── manager/           # Agent registry & metadata
│       │   ├── memory/            # Short-term (Redis) + Long-term (Qdrant)
│       │   ├── tools/             # MCP integration layer
│       │   └── plugins/           # Plugin infrastructure
│       ├── services/              # Evaluation, observability, cost monitoring
│       ├── cli/                   # CLI interface
│       ├── sdk/                   # Python SDK
│       └── plugins/               # External plugin packages
├── dashboard/                     # Next.js web UI
├── docker/                        # docker-compose.yml for Postgres, Redis, Qdrant
├── docs/architecture/             # All design documents
├── tests/                         # Unit, integration, system tests
├── scripts/                       # Dev setup, deployment helpers
└── examples/                      # Sample agents (research, coding, resume)
```

---

## ✅ Current Status

- [x] **Phase 1** — Project Initialization (COMPLETED)
- [x] **Phase 2.1** — Agent Runtime Engine (COMPLETED)
- [x] **Phase 2.2** — Agent Manager Registry (COMPLETED)
- [x] **Phase 2.3** — API Routes — Agents (COMPLETED)
- [x] **Phase 2.4** — Runtime Configuration System (COMPLETED)
- [x] **Phase 3.1** — Task Lifecycle Model (COMPLETED)
- [x] **Phase 3.2** — Task Queue Integration (COMPLETED)
- [x] **Phase 3.3** — Retry and Failure Handling (COMPLETED)
- [x] **Phase 4** — Tool Integration Layer (MCP) (COMPLETED)
- [x] **Phase 5** — Memory Infrastructure (COMPLETED)
- [x] **Phase 6** — Observability System (COMPLETED)

---

## 📋 Phase 1 — Project Initialization ✅

> **Status**: COMPLETED | **Depends on**: Nothing

### What Was Done
- [x] **1.1 Repository Setup**: GitHub repo, `.gitignore`, LICENSE, README
- [x] **1.2 Python Environment**: `uv` initialized, `pyproject.toml` configured with core deps
- [x] **1.3 Dashboard Setup**: Next.js 16 initialized with Tailwind CSS 4
- [x] **1.4 Development Tooling**: Ruff, Black, Pytest, MyPy configured
- [x] **1.5 Infrastructure**: Docker Compose (Postgres, Redis, Qdrant), `.env.example`
- [x] **1.6 Backend Boilerplate**: FastAPI app factory (`api/app.py`), LangGraph runtime shell (`core/runtime/runtime.py`), uvicorn entry point (`main.py`)
- [x] **1.7 Module Structure**: All `__init__.py` files created for proper imports

### Key Files
- `backend/main.py` — Entry point with `sys.path` fix for `src/` layout
- `backend/src/agentos/api/app.py` — FastAPI factory with `/health` endpoint
- `backend/src/agentos/core/runtime/runtime.py` — LangGraph `AgentState` + `AgentRuntime` skeleton
- `docker/docker-compose.yml` — Postgres 16, Redis 7, Qdrant
- `.env.example` — All environment variable templates

---

## 📋 Phase 2 — Core Runtime Infrastructure

> **Status**: IN PROGRESS | **Depends on**: Phase 1

### Objective
Implement the fundamental agent execution engine that runs agent workflows using LangGraph.

### Sub-Phases

#### 2.1 Agent Runtime Engine ✅
- [x] Implement the LangGraph reasoning loop in `core/runtime/runtime.py` (`reason → respond → END`)
- [x] Create `AgentState` with core fields: `input`, `system_prompt`, `reasoning_steps`, `messages`, `output`
- [x] Add LLM interface abstraction (`core/runtime/llm.py`) — Groq provider
- [x] Add `POST /agent/run` API endpoint with token tracking
- [x] Robust `.env` loading and error handling

**Key Files**: `core/runtime/runtime.py`, `core/runtime/llm.py`, `api/app.py`

#### 2.2 Agent Manager (Registry) ✅
- [x] Create Pydantic models for Agent metadata (`AgentCreate`, `AgentUpdate`, `AgentResponse`)
- [x] Implement agent CRUD operations (register, get, list, update, delete)
- [x] Set up SQLModel with PostgreSQL for agent storage
- [x] Add agent versioning support (`version` field, updatable via PUT)

**Key Files**: `core/manager/models.py`, `core/manager/service.py`, `core/manager/database.py`

#### 2.3 API Routes — Agents ✅
- [x] `POST /agents/register` — Register a new agent
- [x] `GET /agents` — List all agents
- [x] `GET /agents/{agent_id}` — Get agent details
- [x] `PUT /agents/{agent_id}` — Update agent
- [x] `DELETE /agents/{agent_id}` — Delete agent
- [x] Request/response schemas in `core/manager/models.py`

**Key Files**: `api/routes/agents.py`

#### 2.4 Runtime Configuration System ✅
- [x] Create a configuration loader using Pydantic Settings (`core/runtime/config.py`)
- [x] Define runtime config schema (provider, timeout, retry, model, temperature, max_tokens)
- [x] Wire configuration into runtime engine, database, and app factory
- [x] Add multi-provider LLM support (Groq, OpenAI, Anthropic) with registry pattern
- [x] Support streaming output via `POST /agent/run/stream` (SSE)

**Key Files**: `core/runtime/config.py`, `core/runtime/llm.py`, `api/app.py`

### Deliverables
- A working agent that can be registered via API and execute a simple reasoning task
- Agent metadata persisted in PostgreSQL

### Verification
- Register an agent via `POST /agents/register`
- Execute a task and see reasoning traces in logs
- Retrieve agent info via `GET /agents/{agent_id}`

---

## 📋 Phase 3 — Task Orchestration System

> **Status**: IN PROGRESS | **Depends on**: Phase 2

### Objective
Introduce task scheduling, lifecycle management, and async execution via Celery + Redis.

### Sub-Phases

#### 3.1 Task Lifecycle Model ✅
- [x] Define task states: `Created → Queued → Running → Paused → Completed / Failed / Cancelled`
- [x] Create SQLModel/Pydantic models for Task (`Task`, `TaskCreate`, `TaskUpdate`, `TaskResponse`)
- [x] Implement state machine transitions with validation (`VALID_TRANSITIONS` dict)
- [x] Persist task state in PostgreSQL
- [x] CRUD service with state enforcement (`orchestrator/service.py`)
- [x] API routes: `POST /tasks/create`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}/status`, `DELETE /tasks/{id}`

**Key Files**: `core/orchestrator/models.py`, `core/orchestrator/service.py`, `api/routes/tasks.py`

#### 3.2 Task Queue Integration (Celery + Redis) ✅
- [x] Configure Celery with Redis as broker (`core/orchestrator/celery_app.py`)
- [x] Create Celery tasks that invoke the Agent Runtime (`core/orchestrator/tasks.py`)
- [x] Update task submission API to automatically enqueue: `POST /tasks/create`
- [x] Implement task status tracking via background updates

**Key Files**: `core/orchestrator/tasks.py`, `core/orchestrator/celery_app.py`

#### 3.3 Retry and Failure Handling ✅
- [x] Implement automatic Celery retries with exponential backoff
- [x] Add task cancellation endpoint (`POST /tasks/{id}/cancel`)
- [x] Sync Database Task IDs with Celery Task IDs for precise control
- [x] Persistence of `retry_count` and failure logs in PostgreSQL

**Key Files**: `core/orchestrator/tasks.py`, `api/routes/tasks.py`

### Deliverables
- Tasks can be submitted, queued, executed asynchronously, and tracked
- Failed tasks are retried automatically

### Verification
- Submit a task via API, verify it appears in queue
- Verify task transitions through lifecycle states
- Kill a worker mid-task, verify retry kicks in

---

## 📋 Phase 4 — Tool Integration Layer (MCP)

> **Status**: IN PROGRESS | **Depends on**: Phase 2

### Objective
Enable agents to call external tools via a standardized interface using MCP.

### Sub-Phases

#### 4.1 Tool Registry ✅
- [x] Define tool interface (name, description, parameters, handler)
- [x] Implement tool registration and discovery
- [x] Create a tool catalog accessible by the runtime
- [x] Expand `AgentState` with `messages`, `run_id`, `tools_available` fields
- [x] Implement full `reason → act → observe` cycle as LangGraph nodes

**Key Files**: `backend/src/agentos/core/tools/registry.py`

#### 4.2 MCP Client Integration ✅
- [x] Implement MCP client for connecting to MCP servers via Stdio
- [x] Handle server initialization and tool discovery
- [x] Map MCP tool definitions to registry format
- [x] Integrated with API and Celery startup

**Key Files**: `backend/src/agentos/core/tools/mcp_manager.py`

#### 4.3 Built-in Tools ✅
- [x] Web search tool (Tavily integration)
- [x] Filesystem access tool (Sandboxed)
- [x] HTTP request tool (httpx)
- [x] Python Execution tool (for data/tool creation)

**Key Files**: `backend/src/agentos/core/tools/builtins/`

#### 4.4 Agent-to-Agent (A2A) Protocol ✅
- [x] Design and implement internal A2A communication spec (`delegate_task`)
- [x] Enable agents to "hand off" or delegate sub-tasks to other registered agents
- [x] Maintain conversation context and hierarchy across multi-agent handoffs
- [x] Implement agent discovery tool (`list_agents`)

**Key Files**: `backend/src/agentos/core/tools/a2a.py`

### Deliverables
- Agents can discover and invoke registered tools during execution
- At least 2-3 built-in tools working

---

## 📋 Phase 5 — Memory Infrastructure ✅
- [x] **5.1 Short-Term Memory (Redis)**: Chat context persistence & caching.
- [x] **5.2 Long-Term Memory (Qdrant)**: Vector storage & semantic retrieval.
- [x] **5.3 Memory API & Auto-RAG**: REST endpoints & auto-context injection.

> **Status**: COMPLETED | **Depends on**: Phase 2

### Objective
Give agents short-term working memory and long-term vector-based knowledge retrieval.

### Sub-Phases

#### 5.1 Short-Term Memory (Redis) ✅
- [x] Implement session-scoped memory store using Redis (threads)
- [x] Support read/write of conversation context
- [x] Implement LLM caching to reduce costs and latency
- [x] Add idempotency checks for reliable task execution
- [x] Auto-expire stale sessions

**Key Files**: `backend/src/agentos/core/memory/short_term.py`

#### 5.2 Long-Term Memory (Qdrant) ✅
- [x] Integrate Qdrant client for vector storage (using modern `query_points` API)
- [x] Implement embedding generation (FastEmbed local BGE model)
- [x] Support storing and retrieving documents by semantic similarity
- [x] Create builtin memory tools: `save_to_knowledge_base`, `query_knowledge_base`

**Key Files**: `backend/src/agentos/core/memory/vector.py`

#### 5.3 Memory API & Auto-RAG ✅
- [x] `POST /memory/upsert` — Store a memory entry via REST
- [x] `POST /memory/search` — Query by semantic similarity via REST
- [x] Wire memory into the agent runtime (Auto-RAG: auto-retrieve context before reasoning)
- [x] Implement `auto_rag` flag in Agent Runtime API

**Key Files**: `backend/src/agentos/api/routes/memory.py`, `backend/src/agentos/core/runtime/runtime.py`

### Deliverables
- Agents automatically retrieve relevant context from memory before reasoning
- Memories persist across sessions

---

## 📋 Phase 6 — Observability System
- [x] **Phase 6.1**: Structured Logging (JSON)
- [x] Phase 6.2: Metrics Collection (Prometheus) ✅
- [x] Phase 6.3: Reasoning Traces & OpenTelemetry ✅

> **Status**: IN PROGRESS | **Depends on**: Phase 2

### Objective
Provide full transparency into agent behavior via structured logging, traces, and metrics.

### Sub-Phases

#### 6.1 Structured Logging ✅
- [x] Configure `structlog` for JSON-formatted logs
- [x] Log every reasoning step: input, LLM call, tool call, output
- [x] Add correlation IDs (task_id, agent_id, run_id) to all log entries
- [x] Implement request/response logging middleware for API

**Key Files**: `backend/src/agentos/services/observability/logging.py`, `backend/src/agentos/api/app.py`

#### 6.2 Metrics Collection (Prometheus) ✅
- [x] Install and configure `prometheus-client`
- [x] Track: token usage (counter), execution time (histogram), task success/failure (counter), cost estimation
- [x] Expose metrics via a `/metrics` API endpoint (Prometheus format)
- [x] Integrate with `AgentRuntime` to record metrics on every run

**Key Files**: `backend/src/agentos/services/observability/metrics.py`, `backend/src/agentos/api/app.py`

#### 6.3 Reasoning Traces & OpenTelemetry ✅
- [x] Instrument code with OpenTelemetry for distributed tracing
- [x] Capture full reasoning trace (Thought → Action → Observation) per task
- [x] Store traces in database or dedicated trace store (Jaegar/Tempo/Langfuse)
- [x] Expose via API: `GET /tasks/{task_id}/trace` (via injected trace header)

**Key Files**: `backend/src/agentos/services/observability/traces.py`

#### 6.4 Immutable Audit Logging (Compliance) ✅
- [x] Implement append-only audit log for sensitive actions (e.g. file writes, API calls)
- [x] Store audit logs in a tamper-evident/read-only storage layer
- [x] Include user/agent attribution and timestamps for every entry

**Key Files**: `backend/src/agentos/services/observability/audit.py`

### Deliverables
- Every agent decision is logged and queryable
- Prometheus-compatible metrics endpoint

---

## 📋 Phase 7 — Evaluation Framework

> **Status**: NOT STARTED | **Depends on**: Phase 2, Phase 6

### Objective
Measure and validate agent performance using automated evaluation frameworks.

### Sub-Phases

#### 7.1 Evaluation Pipeline
- [ ] Define evaluation workflow: input → agent run → score
- [ ] Support batch evaluation mode (run agent against test dataset)

#### 7.2 Framework Integration
- [ ] Integrate RAGAS for RAG evaluation metrics
- [ ] Integrate DeepEval for general LLM evaluation
- [ ] Support custom evaluation metrics

#### 7.3 Evaluation Reports
- [ ] Generate structured evaluation reports (JSON/HTML)
- [ ] Store evaluation results in database
- [ ] Expose via API: `GET /evaluations/{eval_id}`

**Key Files**: `backend/src/agentos/services/evaluation/`

### Deliverables
- Users can run agents against test datasets and receive quality scores

---

## 📋 Phase 8 — Developer Interfaces (CLI + SDK)

> **Status**: NOT STARTED | **Depends on**: Phases 2-7

### Objective
Provide developer-friendly interfaces for interacting with AgentOS.

### Sub-Phases

#### 8.1 CLI Interface
- [ ] Implement `agentos init` — Initialize a new agent project
- [ ] Implement `agentos register-agent` — Register from config file
- [ ] Implement `agentos run-task` — Submit and monitor a task
- [ ] Implement `agentos list-agents` — List registered agents
- [ ] Implement `agentos inspect-task` — View task details and trace
- [ ] Use `click` or `typer` for CLI framework

**Key Files**: `backend/src/agentos/cli/`

#### 8.2 Python SDK
- [ ] Create a client library wrapping the REST API
- [ ] Support: agent registration, task submission, memory operations
- [ ] Publish-ready package structure

**Key Files**: `backend/src/agentos/sdk/python/`

### Deliverables
- Developers can manage the full agent lifecycle from the terminal

---

## 📋 Phase 9 — Plugin Ecosystem

> **Status**: NOT STARTED | **Depends on**: Phases 2-4

### Objective
Enable extensibility through a plugin architecture.

### Sub-Phases

#### 9.1 Plugin Architecture
- [ ] Define plugin interface (abstract base class)
- [ ] Implement plugin loader (file-based discovery)
- [ ] Support plugin types: tools, memory backends, evaluation metrics, agent templates

#### 9.2 Plugin Registry
- [ ] Implement plugin registration and lifecycle management
- [ ] Add `agentos install-plugin` CLI command

**Key Files**: `backend/src/agentos/core/plugins/`, `backend/src/agentos/plugins/`

### Deliverables
- Developers can drop a plugin into `plugins/` and it auto-registers

---

## 📋 Phase 10 — Dashboard & Web UI

> **Status**: NOT STARTED | **Depends on**: Phases 2-6

### Objective
Build a web dashboard for monitoring and managing agents visually.

### Sub-Phases

#### 10.1 Agent Registry View
- [ ] List all registered agents with metadata
- [ ] Agent detail page with version history

#### 10.2 Task Monitoring
- [ ] Real-time task status dashboard
- [ ] Task detail with reasoning trace visualization

#### 10.3 Metrics & Observability
- [ ] Token usage charts
- [ ] Task success/failure rate graphs
- [ ] System health indicators

#### 10.4 Visual Workflow Designer (Drag-and-Drop)
- [ ] Implement interactive canvas for multi-agent composition
- [ ] Drag-and-drop agent/tool blocks to define pipelines
- [ ] Generate YAML/JSON workflow definitions from visual graph

**Key Files**: `dashboard/components/designer/`

---

## 📋 Phase 11 — Documentation & Examples

> **Status**: NOT STARTED | **Depends on**: Phases 2-8

### Sub-Phases
- [ ] Write installation guide and quickstart tutorial
- [ ] Create example agents: Research Agent, Coding Agent, Resume Agent
- [ ] Add API reference documentation
- [ ] Add `CONTRIBUTING.md` with detailed contribution guidelines

**Key Files**: `docs/`, `examples/`

---

## 📋 Phase 12 — Open Source Release Preparation
- [ ] **Phase 12.1**: Final Quality Audit & Bug Squashing
- [ ] **Phase 12.2**: CI/CD Pipelines (GitHub Actions)
- [ ] **Phase 12.3**: Packaging & PyPI Release

> **Status**: NOT STARTED | **Depends on**: All previous phases

#### 12.1 Final Quality Audit
- [ ] Finalize README with badges, screenshots, and quickstart
- [ ] Perform security scan of Docker images and dependencies
- [ ] Optimize response times for all API endpoints

#### 12.2 CI/CD Pipelines
- [ ] Set up GitHub Actions for linting (Ruff), testing (Pytest), and building
- [ ] Automate Docker image builds on release tags
- [ ] Implement automated documentation generation

#### 12.3 Packaging & Release
- [ ] Prepare `pyproject.toml` for PyPI publishing (package as `agentos`)
- [ ] Create GitHub Release v0.1.0 with changelog
- [ ] Publish Docker images to Docker Hub

---

## 📋 Phase 13 — Governance & Human-in-the-loop (HITL)
- [ ] **Phase 13.1**: Intent Gating & Policy Engine (Guardrails)
- [ ] **Phase 13.2**: HITL Checkpoints (Pause/Resume with Approval)
- [ ] **Phase 13.3**: Budget Gating & Rate Limiting

> **Status**: NOT STARTED | **Depends on**: Phases 3, 6

### Objective
Ensure agents operate safely within enterprise guardrails and support human oversight.

#### 13.1 Governance & Policy Engine
- [ ] Define policy language for tool/data access (e.g. "Agent X cannot call tool Y")
- [ ] Implement mid-run "intent gating" (check action against policy before execution)
- [ ] Add support for PII redaction and sensitive data filtering

#### 13.2 HITL Checkpoints
- [ ] Enable `agent.pause()` capability with state persistence
- [ ] Implement approval gating for high-impact tools (e.g. "Ask human before sending $1000")
- [ ] API for human review: `POST /tasks/{id}/approve` or `POST /tasks/{id}/modify`

#### 13.3 Budget Gating
- [ ] Real-time cost calculation per task
- [ ] Automatic task kill/pause if budget exceeds threshold
- [ ] Set global/per-agent spending limits

---

## 📋 Phase 14 — Deployment/Cloud-Native (v1.0)
- [ ] **Phase 14.1**: Production Containerization (Multi-stage Docker)
- [ ] **Phase 14.2**: Kubernetes Helm Charts & Resource Limits
- [ ] **Phase 14.3**: Database Migrations & High Availability (HA)

---

## 📋 Future Roadmap (Beyond MVP)
- [ ] **Multi-Tenancy**: Isolated namespaces/spaces for teams/orgs
- [ ] **Agent Marketplace**: Community index and one-click installs
- [ ] **A2A (External)**: Cross-platform agent communication protocol
- [ ] **LangSmith/Langfuse Cloud Integration**

---

## 🔑 Key Design Decisions

| Decision | Choice | Rationale |
|:---|:---|:---|
| **Agent Framework** | LangGraph | Supports stateful, multi-step reasoning with checkpoints |
| **Task Queue** | Celery + Redis | Battle-tested, supports retries, rate limiting, monitoring |
| **Database** | PostgreSQL | Reliable, supports JSON fields for flexible agent configs |
| **Vector DB** | Qdrant | Open-source, high-performance, first-class Python SDK |
| **API Framework** | FastAPI | Async-native, auto-generated docs, Pydantic validation |
| **Dashboard** | Next.js | Modern React, SSR, TypeScript-native |
| **Docker for deps only** | Local Python + Docker services | Fastest dev loop — no container rebuilds for code changes |

---

## 📝 Notes for Future LLMs

1. **Always read the architecture docs first** — they are the ground truth for design decisions.
2. **Follow the `src/` layout** — all backend code lives under `backend/src/agentos/`. The `main.py` adds `src/` to `sys.path`.
3. **Use `uv` for Python deps** — run `uv sync` and `uv run python main.py` from the `backend/` directory.
4. **Docker is for services only** — run Postgres/Redis/Qdrant via `docker compose -f docker/docker-compose.yml up -d`. Python code runs directly.
5. **Check `uv.lock` for corruption** — the lockfile previously had a stray character (`ī`) on line 69 that caused parse errors. Always verify with `uv sync` after changes.
6. **Module resolution** — the `src/` layout requires `__init__.py` files in every package directory. The user has already created these.
7. **Phase dependencies matter** — Phase 2 (Core Runtime) is the foundation. Phases 3-7 can be partially parallelized after Phase 2 is complete.
8. **MVP scope** — see `MVP_DEFINITION.md`. Do NOT implement marketplace, visual workflow builder, enterprise RBAC, or hosted platform until post-MVP.
