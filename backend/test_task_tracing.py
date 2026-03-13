import requests
import time
import sys

def run_test():
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    base_url = f"http://localhost:{port}"
    
    print("🚀 Testing Task API Tracing Integration...")
    
    # 1. First we need an agent_id to create a task
    # Let's hit the agents list to find one, or use a default one like we did before.
    # We can try to list agents and pick the first one.
    agents_resp = requests.get(f"{base_url}/agents/")
    if not agents_resp.ok or not agents_resp.json():
        print("❌ Could not get any agents to run a task with.")
        # fallback to arbitrary agent id assuming some default exists or it handles it
        agent_id = "default"
    else:
        agent_id = agents_resp.json()[0]["id"]
        
    print(f"📝 Using Agent ID: {agent_id}")
    
    # 2. Create the task
    payload = {
        "agent_id": agent_id,
        "input": "What is 2 + 2?"
    }
    
    print("📡 Creating task via POST /tasks/create...")
    task_resp = requests.post(f"{base_url}/tasks/create", json=payload)
    if not task_resp.ok:
        print(f"❌ Failed to create task: {task_resp.text}")
        sys.exit(1)
        
    task_data = task_resp.json()
    task_id = task_data["id"]
    print(f"✅ Task created with ID: {task_id}")
    
    # 3. Poll for completion
    print("⏳ Waiting for task to complete...")
    max_retries = 30
    status = "queued"
    for _ in range(max_retries):
        poll_resp = requests.get(f"{base_url}/tasks/{task_id}")
        if poll_resp.ok:
            status = poll_resp.json()["status"]
            if status in ["completed", "failed", "cancelled"]:
                break
        time.sleep(1)
        
    print(f"✅ Task finished with status: {status}")
    
    # 4. Fetch the trace
    print(f"📡 Requesting trace via GET /tasks/{task_id}/trace...")
    trace_resp = requests.get(f"{base_url}/tasks/{task_id}/trace")
    
    if trace_resp.ok:
        trace_data = trace_resp.json()
        print("🎉 Successfully retrieved trace info!")
        print(f"Trace ID: {trace_data['trace_id']}")
        print(f"Trace URL (Jaeger): {trace_data['trace_url']}")
    else:
        print("❌ Failed to get trace.")
        print(f"Status Code: {trace_resp.status_code}")
        print(f"Response: {trace_resp.text}")

if __name__ == "__main__":
    run_test()
