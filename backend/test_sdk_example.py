import sys
import os
import asyncio
from typing import Dict, Any

# Add src to path so we can import the local sdk
sys.path.append(os.path.join(os.getcwd(), "src"))

import agentos.sdk as agentos

def test_sync():
    print("\n--- Testing Sync SDK ---")
    with agentos.AgentOS() as client:
        # 1. List Agents
        agents = client.agents.list()
        print(f"✅ Found {len(agents)} agents.")
        
        if agents:
            agent_id = agents[0]["id"]
            print(f"🚀 Running task with Agent: {agents[0]['name']} ({agent_id})")
            
            # 2. Run and Wait
            result = client.tasks.run_and_wait(
                agent_id=agent_id, 
                input_text="What is 2+2?",
                poll_interval=0.5
            )
            print(f"✅ Task Completed! Status: {result['status']}")
            print(f"📝 Output: {result.get('output', 'No output')[:100]}...")

async def test_async():
    print("\n--- Testing Async SDK ---")
    async with agentos.AgentOS(async_mode=True) as client:
        # 1. List Agents
        agents = await client.agents.list()
        print(f"✅ Found {len(agents)} agents.")
        
        if agents:
            agent_id = agents[0]["id"]
            print(f"🚀 Running task with Agent: {agents[0]['name']} ({agent_id})")
            
            # 2. Run and Wait (Async)
            result = await client.tasks.run_and_wait(
                agent_id=agent_id, 
                input_text="What is the capital of Japan?",
                poll_interval=0.5
            )
            print(f"✅ Task Completed! Status: {result['status']}")
            print(f"📝 Output: {result.get('output', 'No output')[:100]}...")

if __name__ == "__main__":
    try:
        test_sync()
        asyncio.run(test_async())
        print("\n✨ SDK Verification Successful!")
    except Exception as e:
        print(f"\n❌ SDK Verification Failed: {e}")
        sys.exit(1)
