
import asyncio
import os
import sys
import uuid

# Ensure src is in sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agentos.core.runtime.runtime import AgentRuntime

async def test_memory():
    print("\n--- Phase 5.1: Short-term Memory (Redis) Test ---")
    
    thread_id = f"test-thread-{uuid.uuid4().hex[:8]}"
    print(f"Using Thread ID: {thread_id}")

    runtime = AgentRuntime(
        model="llama-3.3-70b-versatile",
        thread_id=thread_id
    )
    
    # Step 1: Intrduction
    print("\n--- Step 1: Introducing myself ---")
    prompt1 = "My name is Urvish. Remember this for our next conversation."
    print(f"User: {prompt1}")
    
    result1 = await runtime.run(prompt1)
    print(f"Agent: {result1.get('output')}")

    # Step 2: Verification (New Runtime instance, same thread_id)
    print("\n--- Step 2: Asking for my name (New instance, same thread) ---")
    runtime2 = AgentRuntime(
        model="llama-3.3-70b-versatile",
        thread_id=thread_id
    )
    prompt2 = "What is my name? And tell me what we just talked about."
    print(f"User: {prompt2}")
    
    result2 = await runtime2.run(prompt2)
    print(f"Agent: {result2.get('output')}")
    
    output = result2.get('output', '').lower()
    if "urvish" in output:
        print("\n✅ SUCCESS: Agent remembered the name across turns!")
    else:
        print("\n❌ FAILED: Agent forgot the name.")

if __name__ == "__main__":
    asyncio.run(test_memory())
