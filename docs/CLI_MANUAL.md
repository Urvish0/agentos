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

### 📋 Task Monitoring
- `agentos tasks run [AGENT_ID] --input "your prompt"`: Run a task (interactive).
- `agentos tasks status [TASK_ID]`: Check detailed status.
- `agentos tasks cancel [TASK_ID]`: Stop a running task.
- `agentos tasks trace [TASK_ID]`: Get the OTel/Jaeger trace link.

### Plugins

Manage the AgentOS extension ecosystem.

*   `agentos plugins list`: Show all registered and loaded plugins.
*   `agentos plugins enable [NAME]`: Enable a previously disabled plugin.
*   `agentos plugins disable [NAME]`: Disable an active plugin (prevents loading on restart).
*   `agentos plugins install [PATH]`: Install a new plugin from a local `.py` file path.

Example:
```bash
agentos plugins disable weather_tool
agentos plugins install ./my_custom_plugin.py
```

---

## 💡 Environment Variables
- `AGENTOS_API_URL`: Override the backend URL (default: `http://localhost:8000`).
