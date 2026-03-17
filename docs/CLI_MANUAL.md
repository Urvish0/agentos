# AgentOS CLI Manual

The `agentos` CLI is the primary developer interface for interacting with the AgentOS platform.

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.13+
- `uv` package manager
- Running AgentOS Backend (default: `http://localhost:8000`)

### 2. Installation
From the `backend` directory:
```bash
uv sync
```
This registers the `agentos` command in your environment.

### 3. Usage with `uv`
If the command is not in your path, run it via `uv`:
```bash
uv run agentos --help
```

---

## 🚀 Command Reference

### `agentos init`
Initializes a local directory for AgentOS development by creating a sample `agent.yaml`.

### `agentos agents`
Manage the Agent Registry.
- `list`: Show all registered agents.
- `register [FILE]`: Register a new agent from YAML/JSON.

### `agentos tasks`
Execute and monitor agent workflows.
- `run [AGENT_ID] --input "..."`: Launch a task and poll for completion.
- `status [TASK_ID]`: View detailed task state.
- `cancel [TASK_ID]`: Stop a running task.
- `trace [TASK_ID]`: Get the OTel/Jaeger trace link.

---

## 💡 Environment Variables
- `AGENTOS_API_URL`: Override the backend URL (default: `http://localhost:8000`).
