import os
import sys
import json
import asyncio
from typing import Dict, Any

# Ensure src is in PYTHONPATH
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from sqlalchemy.orm import Session
from agentos.core.manager.database import engine, create_db_and_tables
from agentos.core.manager.models import AgentCreate
from agentos.api.routes.agents import register_agent
from agentos.core.runtime.runtime import AgentRuntime
from agentos.services.observability.audit import audit_logger

async def test_audit_logging():
    print("🚀 Starting Phase 6.4 Audit Logging Verification...")
    
    # 1. Initialize local DB (just in case)
    create_db_and_tables()
    
    # Clean up old log if it exists to start fresh
    if audit_logger.file_path.exists():
        os.remove(audit_logger.file_path)
        # Re-initialize genesis block
        audit_logger._ensure_file_exists()
        print("🗑️ Block 0: Cleared old audit log + created Genesis Block")

    # 2. Trigger an API action (Register Agent)
    with Session(engine) as session:
        agent_data = AgentCreate(
            name="Audit Test Agent",
            description="Agent for testing audit logs",
            model="llama-3.3-70b-versatile",
            provider="groq",
            system_prompt="You are a helpful agent.",
            tools='["list_agents"]'
        )
        print("👤 Block 1: Registering new agent to trigger API audit trail...")
        # Since router endpoints usually inject session, we pass it manually
        register_agent(agent_data, session)
        
    # 3. Trigger a Runtime action (Tool Execution)
    print("🤖 Block 2: Running Agent task with Tool to trigger Runtime audit trail...")
    runtime = AgentRuntime(
        model="llama-3.3-70b-versatile",
        provider="groq",
        tools=["list_agents"]
    )
    # The LLM decision takes a moment
    await runtime.run("Please use the tool to list all available agents.")
    
    # 4. Verify the Ledger Chain
    print("\n🔐 Verifying Cryptographic Audit Chain Integrity...")
    try:
        is_valid = audit_logger.verify_audit_chain()
        if is_valid:
            print("✅ Chain is VALID! No tampering detected.")
            with open(audit_logger.file_path, 'r') as f:
                lines = f.readlines()
                print(f"📦 Total Blocks (including Genesis): {len(lines)}")
                
                print("\n📄 Latest Log Entry Snippet:")
                latest_entry = json.loads(lines[-1])
                print(json.dumps(latest_entry, indent=2))
    except Exception as e:
        print(f"❌ Chain is INVALID: {e}")
        return

    # 5. Simulate Tampering
    print("\n🕵️‍♂️ Simulating an attacker modifying the JSONL file retroactively...")
    with open(audit_logger.file_path, 'r') as f:
        lines = f.readlines()
        
    # Modify the first actual entry (index 1, since 0 is genesis)
    tampered_entry = json.loads(lines[1])
    tampered_entry["details"]["name"] = "Hacked Agent Name" # Malicious change
    
    # Put the hash back so it's a valid JSON string (even with the wrong hash)
    # Actually, we don't recalculate the hash - the attacker forgot!
    lines[1] = json.dumps(tampered_entry) + "\n"
    
    with open(audit_logger.file_path, 'w') as f:
        f.writelines(lines)
        
    print("🔐 Re-verifying Tampered Audit Chain...")
    try:
        audit_logger.verify_audit_chain()
        print("❌ CRITICAL BUG: Tampering was not detected!")
    except Exception as e:
        print(f"✅ Tampering SUCCESSFULLY DETECTED!")
        print(f"   Exception thrown: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test_audit_logging())
