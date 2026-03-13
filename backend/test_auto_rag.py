
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_memory_api_and_auto_rag():
    print("\n--- Phase 5.3: Memory API & Auto-RAG Test ---")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Upsert knowledge via API
        print("\n--- Step 1: Upserting knowledge via API ---")
        upsert_payload = {
            "text": "The AgentOS headquarter is located in the Silicon Valley of India: Bengaluru.",
            "metadata": {"type": "fact", "importance": "high"}
        }
        res_upsert = await client.post(f"{BASE_URL}/memory/upsert", json=upsert_payload)
        print(f"Upsert Status: {res_upsert.status_code}")
        print(f"Upsert Response: {res_upsert.json()}")

        # Step 2: Search knowledge via API
        print("\n--- Step 2: Searching knowledge via API ---")
        search_payload = {"query": "Where is AgentOS headquarters?"}
        res_search = await client.post(f"{BASE_URL}/memory/search", json=search_payload)
        print(f"Search Status: {res_search.status_code}")
        print(f"Found: {res_search.json()[0]['content'] if res_search.json() else 'None'}")

        # Step 3: Test Auto-RAG
        print("\n--- Step 3: Verifying Auto-RAG (Automatic context injection) ---")
        # No tools enabled - the agent MUST use injected context
        agent_payload = {
            "input": "I am planning to visit the AgentOS office. Which city should I book my flight to?",
            "auto_rag": True,
            "model": "llama-3.3-70b-versatile"
        }
        res_agent = await client.post(f"{BASE_URL}/agent/run", json=agent_payload)
        print(f"Agent Status: {res_agent.status_code}")
        
        output = res_agent.json().get("output", "")
        print(f"Agent Output: {output}")
        
        if "bengaluru" in output.lower():
            print("\n✅ SUCCESS: Agent answered correctly using Auto-RAG context!")
        else:
            print("\n❌ FAILED: Agent couldn't find the information automatically.")

if __name__ == "__main__":
    asyncio.run(test_memory_api_and_auto_rag())
