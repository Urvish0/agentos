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
| **Development Roadmap** | `docs/architecture/DEVELOPMENT_ROADMAP.md` | Step-by-step development phases |

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

> **Status**: NOT STARTED | **Depends on**: Phase 1

### Objective
Implement the fundamental agent execution engine that runs agent workflows using LangGraph.

### Sub-Phases

#### 2.1 Agent Runtime Engine
- [ ] Implement the LangGraph reasoning loop in `core/runtime/runtime.py`
- [ ] Create `AgentState` with proper fields: `input`, `chat_history`, `plan`, `tools_called`, `output`
- [ ] Implement the `reason` → `act` → `observe` cycle as LangGraph nodes
- [ ] Add LLM interface abstraction (support OpenAI, Anthropic, Google models)
- [ ] Support streaming output from the reasoning loop

**Key File**: `backend/src/agentos/core/runtime/runtime.py`

#### 2.2 Agent Manager (Registry)
- [ ] Create Pydantic models for Agent metadata (`AgentSchema`)
- [ ] Implement agent CRUD operations (register, get, list, update, delete)
- [ ] Set up SQLAlchemy/SQLModel with PostgreSQL for agent storage
- [ ] Add agent versioning support

**Key Files**: `backend/src/agentos/core/manager/`

#### 2.3 API Routes — Agents
- [ ] `POST /agents/register` — Register a new agent
- [ ] `GET /agents` — List all agents
- [ ] `GET /agents/{agent_id}` — Get agent details
- [ ] `PUT /agents/{agent_id}` — Update agent
- [ ] `DELETE /agents/{agent_id}` — Delete agent
- [ ] Add request/response schemas in `api/schemas/`

**Key Files**: `backend/src/agentos/api/routes/`, `backend/src/agentos/api/schemas/`

#### 2.4 Runtime Configuration System
- [ ] Create a configuration loader (from `.env`, YAML, or CLI args)
- [ ] Define runtime config schema (model provider, timeout, retry policy, etc.)
- [ ] Wire configuration into the runtime engine

**Key Files**: `backend/src/agentos/core/runtime/config.py`

### Deliverables
- A working agent that can be registered via API and execute a simple reasoning task
- Agent metadata persisted in PostgreSQL

### Verification
- Register an agent via `POST /agents/register`
- Execute a task and see reasoning traces in logs
- Retrieve agent info via `GET /agents/{agent_id}`

---

## 📋 Phase 3 — Task Orchestration System

> **Status**: NOT STARTED | **Depends on**: Phase 2

### Objective
Introduce task scheduling, lifecycle management, and async execution via Celery + Redis.

### Sub-Phases

#### 3.1 Task Lifecycle Model
- [ ] Define task states: `Created → Queued → Running → Paused → Completed / Failed`
- [ ] Create Pydantic models for Task (`TaskSchema`)
- [ ] Implement state machine transitions with validation
- [ ] Persist task state in PostgreSQL

**Key Files**: `backend/src/agentos/core/orchestrator/models.py`

#### 3.2 Task Queue Integration (Celery + Redis)
- [ ] Configure Celery with Redis as broker
- [ ] Create Celery tasks that invoke the Agent Runtime
- [ ] Implement task submission API: `POST /tasks/create`
- [ ] Implement task status API: `GET /tasks/{task_id}`
- [ ] Add task listing: `GET /tasks`

**Key Files**: `backend/src/agentos/core/orchestrator/tasks.py`, `backend/src/agentos/core/orchestrator/celery_app.py`

#### 3.3 Retry and Failure Handling
- [ ] Implement configurable retry policies (max retries, backoff)
- [ ] Add failure recovery (save checkpoint state before crash)
- [ ] Implement task cancellation: `POST /tasks/{task_id}/cancel`

**Key Files**: `backend/src/agentos/core/orchestrator/retry.py`

### Deliverables
- Tasks can be submitted, queued, executed asynchronously, and tracked
- Failed tasks are retried automatically

### Verification
- Submit a task via API, verify it appears in queue
- Verify task transitions through lifecycle states
- Kill a worker mid-task, verify retry kicks in

---

## 📋 Phase 4 — Tool Integration Layer (MCP)

> **Status**: NOT STARTED | **Depends on**: Phase 2

### Objective
Enable agents to call external tools via a standardized interface using MCP.

### Sub-Phases

#### 4.1 Tool Registry
- [ ] Define tool interface (name, description, parameters, handler)
- [ ] Implement tool registration and discovery
- [ ] Create a tool catalog accessible by the runtime

**Key Files**: `backend/src/agentos/core/tools/registry.py`

#### 4.2 MCP Client Integration
- [ ] Implement MCP client for connecting to MCP servers
- [ ] Support tool invocation through MCP protocol
- [ ] Add security sandboxing for tool execution

**Key Files**: `backend/src/agentos/core/tools/mcp_client.py`

#### 4.3 Built-in Tools
- [ ] Web search tool
- [ ] Filesystem access tool
- [ ] HTTP request tool
- [ ] (Optional) GitHub integration tool

**Key Files**: `backend/src/agentos/core/tools/builtins/`

### Deliverables
- Agents can discover and invoke registered tools during execution
- At least 2-3 built-in tools working

---

## 📋 Phase 5 — Memory Infrastructure

> **Status**: NOT STARTED | **Depends on**: Phase 2

### Objective
Give agents short-term working memory and long-term vector-based knowledge retrieval.

### Sub-Phases

#### 5.1 Short-Term Memory (Redis)
- [ ] Implement session-scoped memory store using Redis
- [ ] Support read/write of conversation context
- [ ] Auto-expire stale sessions

**Key Files**: `backend/src/agentos/core/memory/short_term.py`

#### 5.2 Long-Term Memory (Qdrant)
- [ ] Integrate Qdrant client for vector storage
- [ ] Implement embedding generation (use a lightweight model or API)
- [ ] Support storing and retrieving documents by semantic similarity

**Key Files**: `backend/src/agentos/core/memory/long_term.py`

#### 5.3 Memory API
- [ ] `POST /memory/store` — Store a memory entry
- [ ] `POST /memory/query` — Query by semantic similarity
- [ ] Wire memory into the agent runtime (auto-retrieve context before reasoning)

**Key Files**: `backend/src/agentos/core/memory/api.py`

### Deliverables
- Agents automatically retrieve relevant context from memory before reasoning
- Memories persist across sessions

---

## 📋 Phase 6 — Observability System

> **Status**: NOT STARTED | **Depends on**: Phase 2

### Objective
Provide full transparency into agent behavior via structured logging, traces, and metrics.

### Sub-Phases

#### 6.1 Structured Logging
- [ ] Configure `structlog` for JSON-formatted logs
- [ ] Log every reasoning step: input, LLM call, tool call, output
- [ ] Add correlation IDs (task_id, agent_id) to all log entries

**Key Files**: `backend/src/agentos/services/observability/logging.py`

#### 6.2 Metrics Collection
- [ ] Track: token usage, execution time, task success/failure rate, cost estimation
- [ ] Expose metrics via a `/metrics` endpoint (Prometheus format)

**Key Files**: `backend/src/agentos/services/observability/metrics.py`

#### 6.3 Reasoning Traces
- [ ] Capture full reasoning trace (Thought → Action → Observation) per task
- [ ] Store traces in database for later inspection
- [ ] Expose via API: `GET /tasks/{task_id}/trace`

**Key Files**: `backend/src/agentos/services/observability/traces.py`

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

**Key Files**: `dashboard/`

### Deliverables
- A working web UI for monitoring agents and tasks

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

> **Status**: NOT STARTED | **Depends on**: All phases

### Sub-Phases
- [ ] Finalize README with badges, screenshots, and quickstart
- [ ] Set up GitHub Actions CI/CD (lint, test, build)
- [ ] Prepare Docker images for distribution
- [ ] Create GitHub Release v0.1.0
- [ ] Publish to PyPI as `agentos`

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
