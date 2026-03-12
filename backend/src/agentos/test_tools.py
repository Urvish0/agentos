
import asyncio
import sys
import os

# Ensure src is in sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agentos.core.runtime.runtime import AgentRuntime
from agentos.core.tools.registry import registry as tool_registry

async def test_tool_calling():
    print("\n--- Testing Tool Registry ---")
    tools = tool_registry.list_tools()
    for t in tools:
        print(f"Found Tool: {t.name} - {t.description}")

    print("\n--- Testing Agent Runtime with Tools ---")
    runtime = AgentRuntime(
        model="llama-3.3-70b-versatile",
        tools=["get_weather"]
    )
    
    prompt = "What is the weather in Mumbai? Use the get_weather tool."
    print(f"User: {prompt}")
    
    try:
        result = await runtime.run(prompt)
        print("\n--- Results ---")
        print(f"Output: {result.get('output')}")
        print(f"Total Tokens: {result.get('total_tokens')}")
        print(f"Messages Count: {result.get('messages_count')}")
    except Exception as e:
        print(f"FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_calling())
