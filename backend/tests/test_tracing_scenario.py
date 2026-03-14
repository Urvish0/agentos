import requests
import json
import time
import sys

def run_scenario():
    print("🚀 Starting Phase 6.3 Tracing Verification Scenario...")
    print("-------------------------------------------------------")
    
    url = "http://localhost:8000/agent/run"
    
    # scenario: User asks to list agents (requires tool call)
    payload = {
        "input": "Can you check which agents are currently registered in the system? Please use the tool to find out.",
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "tools": ["list_agents"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    try:
        print(f"📡 Sending request to {url}...")
        print(f"📝 Prompt: \"{payload['input']}\"")
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers)
        
        end_time = time.time()
        duration = end_time - start_time

        if response.status_code == 200:
            print("✅ Request Successful!")
            print(f"⏱️ Duration: {duration:.2f}s")
            result = response.json()
            print("\n🤖 Agent Output:")
            print(f"\"{result['output']}\"")
            
            print("\n🔍 Verification Steps for You:")
            print("1. Check the TERMINAL where the server is running.")
            print("2. Look for the JSON representation of spans. You should see:")
            print("   - 'name': 'POST /agent/run' (Server Span)")
            print("   - 'name': 'agent_run' (Runtime Span)")
            print("   - 'name': 'reason_node' (Thought Span)")
            print("   - 'name': 'action_node' (Tool Execution Span)")
            print("   - 'name': 'tool_call:list_agents' (Individual Tool Span)")
            print("\n3. Look for the LOG entries (info). They should now include:")
            print("   - trace_id=0x...")
            print("   - span_id=0x...")
            print("   Confirm that the 'trace_id' matches across all logs for this request.")
            
        else:
            print(f"❌ Request Failed with status: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("💡 Make sure the backend is running (uv run python main.py) before running this test.")

if __name__ == "__main__":
    run_scenario()
