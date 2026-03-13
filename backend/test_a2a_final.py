
import httpx
import time
import json
import os
import sys
import asyncio
import structlog
from sqlmodel import Session, select

# Ensure src is in PYTHONPATH for direct tests
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from agentos.core.manager.database import engine, create_db_and_tables
from agentos.core.manager import service as agent_service
from agentos.core.manager.models import Agent, AgentCreate
from agentos.core.orchestrator.models import Task, TaskStatus
from agentos.core.runtime.runtime import AgentRuntime

BASE_URL = "http://localhost:8000"
client = httpx.Client(follow_redirects=True, timeout=30.0)

def setup_agents_direct():
    """Setup agents directly in DB for non-API tests."""
    create_db_and_tables()
    with Session(engine) as session:
        # Register Calc Bot
        if not agent_service.get_agent(session, "calc-bot"):
            agent_service.create_agent(session, AgentCreate(
                id="calc-bot",
                name="Calc Bot",
                description="Math specialist",
                system_prompt="You are a math expert. Only answer 2.",
                model="llama-3.3-70b-versatile"
            ))
        # Register Manager
        if not agent_service.get_agent(session, "math-manager"):
            agent_service.create_agent(session, AgentCreate(
                id="math-manager",
                name="Math Manager",
                description="Delegator",
                system_prompt="Use 'delegate_task' for math.",
                tools=json.dumps(["delegate_task"]),
                model="llama-3.3-70b-versatile"
            ))

async def test_direct_runtime():
    """Test A2A logic directly via Python code (fast)."""
    print("\n[1/2] Testing A2A Logic (Direct Runtime)...")
    setup_agents_direct()
    
    runtime = AgentRuntime(model="llama-3.3-70b-versatile", tools=["delegate_task"])
    structlog.contextvars.bind_contextvars(run_id="direct-test-run")
    
    try:
        run_id = "direct-test-run"
        result = await runtime.run("Ask calc-bot what is 1+1.", run_id=run_id)
        print(f"✅ Result: {result['output']}")
        
        with Session(engine) as session:
            query = select(Task).where(Task.parent_task_id == run_id)
            child = session.exec(query).first()
            if child:
                agent = session.get(Agent, child.agent_id)
                agent_info = f"'{agent.name}' ({agent.description})" if agent else f"Agent {child.agent_id}"
                print(f"✅ Success: Child task {child.id} linked to parent!")
                print(f"   ↳ Extracted by: {agent_info}")
                print(f"   ↳ Task Input: {child.input}")
            else:
                print("❌ Failure: No child task found.")
    finally:
        structlog.contextvars.clear_contextvars()

def test_system_api():
    """Test A2A via REST API and Celery (Full System)."""
    print("\n[2/2] Testing A2A Protocol (Full System API)...")
    
    try:
        # 1. Health check
        client.get(f"{BASE_URL}/health")
    except Exception:
        print("❌ Error: API server is not reachable. Is 'main.py' running?")
        return

    # 2. Register Agents via API
    client.post(f"{BASE_URL}/agents/register", json={
        "id": "calc-bot", "name": "Calc Bot", "description": "Math",
        "system_prompt": "Answer 1+1=2.", "model": "llama-3.3-70b-versatile"
    })
    client.post(f"{BASE_URL}/agents/register", json={
        "id": "math-manager", "name": "Math Manager", "description": "Boss",
        "system_prompt": "Delegate math to 'calc-bot'.", 
        "tools": "[\"delegate_task\"]", "model": "llama-3.3-70b-versatile"
    })

    # 3. Create Task
    resp = client.post(f"{BASE_URL}/tasks/create", json={
        "agent_id": "math-manager", "input": "Ask calc-bot for 1+1."
    })
    if resp.status_code not in [200, 201]:
        print(f"❌ Failed to create task: {resp.text}")
        return
        
    task_id = resp.json()["id"]
    print(f"[*] Task {task_id} submitted. Monitoring...")

    # 4. Poll for result
    start = time.time()
    while time.time() - start < 45:
        t = client.get(f"{BASE_URL}/tasks/{task_id}").json()
        if t["status"] == "completed":
            print(f"✅ Manager Response: {t['output']}")
            break
        elif t["status"] == "failed":
            print(f"❌ Task Failed: {t['error']}")
            break
        print(".", end="", flush=True)
        time.sleep(2)
    else:
        print("\n❌ Timeout.")
        return

    # 5. Check hierarchy
    tasks = client.get(f"{BASE_URL}/tasks").json()
    children = [tk for tk in tasks if tk.get("parent_task_id") == task_id]
    if children:
        print(f"✅ Success: Verified parent-child link!")
        for child in children:
            # Fetch agent name for better readability
            agent_resp = client.get(f"{BASE_URL}/agents/{child['agent_id']}")
            agent_name = child['agent_id']
            if agent_resp.status_code == 200:
                agent_name = agent_resp.json().get('name', child['agent_id'])
            
            print(f"   ↳ Child Task ID: {child['id']}")
            print(f"   ↳ Executed by: {agent_name}")
            print(f"   ↳ Task Input: {child['input']}")
            print(f"   ↳ Status: {child['status']}")
            print(f"   ↳ Result: {child['output']}")
    else:
        print("❌ Failure: Hierarchy not found in DB.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["direct", "system", "all"], default="all")
    args = parser.parse_args()

    if args.mode in ["direct", "all"]:
        asyncio.run(test_direct_runtime())
    
    if args.mode in ["system", "all"]:
        test_system_api()
