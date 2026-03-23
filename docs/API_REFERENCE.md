# AgentOS API Reference

AgentOS provides both a REST API via FastAPI and a robust Python SDK for seamless integration into your own Python applications.

## Python SDK (`AgentOS`)

The `AgentOS` client is the primary way to interact with the system programmatically. 

### Initialization
```python
from agentos.sdk.client import AgentOS

# Synchronous client
client = AgentOS(base_url="http://localhost:8000")

# Asynchronous client
async with AgentOS(async_mode=True) as client:
    agents = await client.agents.list()
```

### `client.agents` (Agent Management)
- `client.agents.list()`: Returns a list of all registered agents.
- `client.agents.register(agent_data: dict)`: Registers a new agent.
- `client.agents.get(agent_id: str)`: Retrieves metadata for a specific agent.
- `client.agents.delete(agent_id: str)`: Removes an agent from the registry.

### `client.tasks` (Task Orchestration)
- `client.tasks.create(agent_id: str, input: str)`: Submits a new task to the specified agent. Returns a Task ID.
- `client.tasks.get(task_id: str)`: Gets the current status and output of a task.
- `client.tasks.cancel(task_id: str)`: Cancels a running or queued task.

*(For detailed schema definitions, see `backend/src/agentos/core/manager/models.py` and `backend/src/agentos/core/orchestrator/models.py`)*

## REST API (Swagger / OpenAPI)

When the AgentOS backend is running, an automatic OpenAPI interactive documentation page is available.
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Agents (`/agents`)
- `POST /agents/register`: Register a new agent template.
- `GET /agents`: List registered agents.
- `GET /agents/{agent_id}`: Get agent details.
- `PUT /agents/{agent_id}`: Update an agent.
- `DELETE /agents/{agent_id}`: Delete an agent.

#### Tasks (`/tasks`)
- `POST /tasks/create`: Submit a task for execution (returns task metadata).
- `GET /tasks`: List recent tasks.
- `GET /tasks/{task_id}`: Get task status (Queued, Running, Completed, Failed).
- `PATCH /tasks/{task_id}/status`: Internal updates to task state.
- `POST /tasks/{task_id}/cancel`: Request cancellation.

#### Memory (`/memory`)
- `POST /memory/upsert`: Embed and store text in the vector database (Qdrant).
- `POST /memory/search`: Retrieve nearest neighbors based on semantic similarity.

#### Observability & Setup
- `GET /health`: System health check.
- `GET /metrics`: Prometheus-compatible metrics endpoint.
- `GET /plugins`: List available plugins.
