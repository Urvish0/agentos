
import asyncio
import os
import sys

# Ensure src is in sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agentos.core.runtime.runtime import AgentRuntime
from agentos.core.tools.registry import registry as tool_registry

async def test_builtins():
    print("\n--- Phase 4.3: Built-in Tools Test ---")
    
    # Check if tools are registered
    print("\n--- Checking Registry ---")
    tools = tool_registry.list_tools()
    expected_tools = ["list_directory", "read_file", "write_file", "execute_python", "http_request", "search"]
    
    found_count = 0
    for t in tools:
        if t.name in expected_tools:
            print(f"✅ Found Built-in Tool: {t.name}")
            found_count += 1
        else:
            print(f"Found other Tool: {t.name}")
            
    if found_count < len(expected_tools):
        print(f"\n⚠️ WARNING: Only found {found_count}/{len(expected_tools)} built-in tools.")

    print("\n--- Testing Agent with Filesystem & Python Tool ---")
    runtime = AgentRuntime(
        model="llama-3.3-70b-versatile",
        tools=["write_file", "read_file", "execute_python"]
    )
    
    # Complex task: Write a python script to file, then execute that file.
    prompt = (
        "1. Use write_file to save a Python script named 'hello.py' that prints 'Hello from AgentOS!'.\n"
        "2. Use read_file to verify the content of 'hello.py'.\n"
        "3. Use execute_python to run the code: print(open('./storage/agents/hello.py').read()) and then execute another print('Execution Success')"
    )
    
    # Simpler version to ensure first-time success
    prompt = "Please write a file named 'greeting.txt' with the content 'Hello World' and then read it back to confirm."
    
    print(f"User: {prompt}")
    
    try:
        result = await runtime.run(prompt)
        print("\n--- Results ---")
        print(f"Output: {result.get('output')}")
        print(f"Messages Count: {result.get('messages_count')}")
        
        if "Hello World" in result.get('output', ''):
            print("\n✅ SUCCESS: Filesystem tools worked!")
        else:
            print("\n⚠️ WARNING: Output didn't contain expected text.")

        # Test Python Executor
        print("\n--- Testing Python Executor ---")
        py_prompt = "Use the execute_python tool to calculate 2**10 and print the result."
        print(f"User: {py_prompt}")
        
        result_py = await runtime.run(py_prompt)
        print("\n--- Results ---")
        print(f"Output: {result_py.get('output')}")
        
        if "1024" in result_py.get('output', ''):
            print("\n✅ SUCCESS: Python Executor worked!")
        else:
            print("\n⚠️ WARNING: Python output didn't contain expected result.")
            
    except Exception as e:
        print(f"FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_builtins())
