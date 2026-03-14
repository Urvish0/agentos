
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_structured_logging():
    print("\n--- Phase 6.1: Structured Logging Verification ---")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Hit a simple endpoint to see request logging
        print("\n--- Step 1: Verifying API Middleware Logging ---")
        res_health = await client.get(f"{BASE_URL}/health")
        print(f"Health Check Status: {res_health.status_code}")

        # Step 2: Trigger an agent run to see context-aware logging
        print("\n--- Step 2: Verifying AgentRuntime Context Logging ---")
        agent_payload = {
            "input": "Explain the concept of entropy in one sentence.",
            "thread_id": "test-log-thread",
            "model": "llama-3.3-70b-versatile"
        }
        res_agent = await client.post(f"{BASE_URL}/agent/run", json=agent_payload)
        print(f"Agent Status: {res_agent.status_code}")
        print(f"Agent Output: {res_agent.json().get('output', '')[:50]}...")

        print("\n✅ Verification request sent! Check the backend terminal for structured logs with request_id, run_id, and thread_id.")

if __name__ == "__main__":
    asyncio.run(test_structured_logging())
