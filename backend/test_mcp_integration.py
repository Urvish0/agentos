
import asyncio
import os
import json
import sys

# Ensure src is in sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agentos.core.tools.mcp_manager import mcp_manager
from agentos.core.runtime.runtime import AgentRuntime
from agentos.core.tools.registry import registry as tool_registry

async def test_mcp_integration():
    print("\n--- Phase 4.2: MCP Integration Test ---")
    
    # Define config for our local test server
    # Note: Using absolute path to the server script for reliability
    server_script = os.path.abspath("test_mcp_server.py")
    mcp_config = {
        "test_server": {
            "command": sys.executable,
            "args": [server_script]
        }
    }
    
    config_json = json.dumps(mcp_config)
    
    print(f"Connecting to test MCP server at: {server_script}...")
    await mcp_manager.initialize_from_config(config_json)
    
    # Wait a bit for connection and sync
    await asyncio.sleep(2)
    
    print("\n--- Checking Registry ---")
    tools = tool_registry.list_tools()
    mcp_tool_name = "test_server__mcp_echo"
    found = False
    for t in tools:
        print(f"Found Tool: {t.name}")
        if t.name == mcp_tool_name:
            found = True
            
    if not found:
        print(f"FAILED: {mcp_tool_name} not found in registry.")
        return

    print(f"\n--- Testing Agent with MCP Tool ({mcp_tool_name}) ---")
    runtime = AgentRuntime(
        model="llama-3.3-70b-versatile",
        tools=[mcp_tool_name]
    )
    
    prompt = "Please use the test_server__mcp_echo tool to say 'Hello MCP Integration!'"
    print(f"User: {prompt}")
    
    try:
        result = await runtime.run(prompt)
        print("\n--- Results ---")
        print(f"Output: {result.get('output')}")
        print(f"Messages Count: {result.get('messages_count')}")
        
        if "MCP Echo:" in result.get('output', ''):
            print("\n✅ SUCCESS: MCP Tool successfully invoked and result processed by agent!")
        else:
            print("\n⚠️ WARNING: Agent output didn't contain the expected echo prefix.")
            
    except Exception as e:
        print(f"FAILED with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp_manager.disconnect_all()

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
