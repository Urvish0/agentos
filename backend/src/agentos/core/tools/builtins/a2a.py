
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import structlog
from sqlmodel import Session

from agentos.core.manager.database import engine
from agentos.core.manager import service as agent_service
from agentos.core.orchestrator import service as task_service
from agentos.core.orchestrator.models import TaskCreate, TaskStatus

logger = structlog.get_logger()

class DelegateTaskArgs(BaseModel):
    agent_id: str = Field(..., description="The ID of the agent to delegate the task to")
    input_text: str = Field(..., description="The instructions or goal for the sub-agent")

class ListAgentsArgs(BaseModel):
    pass

async def list_agents() -> str:
    """
    Returns a list of all available agents that can be delegated to.
    Useful for discovering specialized agents.
    """
    with Session(engine) as session:
        agents = agent_service.list_agents(session)
        if not agents:
            return "No agents registered in the system."
        
        lines = ["Available Agents:"]
        for a in agents:
            lines.append(f"- ID: {a.id} | Name: {a.name} | Description: {a.description}")
        return "\n".join(lines)

async def delegate_task(agent_id: str, input_text: str) -> str:
    """
    Delegates a sub-task to another agent and waits for the result.
    This allows for hierarchical agent cooperation.
    
    Args:
        agent_id (str): The ID of the target agent.
        input_text (str): The goal or instructions for the agent.
    """
    # 1. Get current context for parent_task_id if available
    ctx = structlog.contextvars.get_contextvars()
    logger.info("A2A Tool Context", context=ctx)
    parent_task_id = ctx.get("run_id") 
    
    logger.info("Delegating task", to_agent=agent_id, parent_task=parent_task_id)

    with Session(engine) as session:
        # 2. Verify agent exists
        agent = agent_service.get_agent(session, agent_id)
        if not agent:
            available = await list_agents()
            return f"Error: Agent '{agent_id}' not found. {available}"

        # 3. Create a child task in the database for traceability
        task_data = TaskCreate(
            agent_id=agent_id,
            input=input_text
        )
        child_task = task_service.create_task(session, task_data)
        child_task.parent_task_id = parent_task_id
        session.add(child_task)
        session.commit()
        session.refresh(child_task)

        try:
            # 4. Initialize and run the sub-agent
            import json
            tools_list = []
            if agent.tools:
                try:
                    tools_list = json.loads(agent.tools)
                except:
                    logger.warning("Failed to parse sub-agent tools", agent_id=agent_id)

            # Move child task to RUNNING
            task_service.update_task_status(session, child_task.id, TaskStatus.RUNNING.value)

            from agentos.core.runtime.runtime import AgentRuntime
            sub_runtime = AgentRuntime(
                model=agent.model,
                system_prompt=agent.system_prompt,
                tools=tools_list,
                thread_id=ctx.get("thread_id")
            )

            result = await sub_runtime.run(input_text, run_id=child_task.id)

            # 5. Update child task completion
            task_service.update_task_status(
                session,
                child_task.id,
                TaskStatus.COMPLETED.value,
                output=result.get("output", "")
            )
            
            # Update metrics
            child_task.model = result.get("model", "")
            child_task.total_tokens = result.get("total_tokens", 0)
            child_task.execution_time_ms = result.get("execution_time_ms", 0.0)
            session.add(child_task)
            session.commit()

            return f"Delegation successful. Result from agent '{agent_id}':\n\n{result.get('output')}"

        except Exception as e:
            logger.error("Delegated task failed", agent_id=agent_id, error=str(e))
            task_service.update_task_status(
                session,
                child_task.id,
                TaskStatus.FAILED.value,
                error=str(e)
            )
            return f"Error: Delegated task to agent '{agent_id}' failed: {str(e)}"
