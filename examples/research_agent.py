"""
Example: Research Agent
This script demonstrates how to register an agent using the AgentOS SDK and run a research task.
"""
import time
from agentos.sdk.client import AgentOS

def main():
    print("🤖 Initializing AgentOS Client...")
    # Assumes the backend is running at localhost:8000
    with AgentOS() as client:
        # 1. Define the Agent
        agent_data = {
            "name": "Market Researcher",
            "description": "An agent that researches topics using the web.",
            "system_prompt": "You are a diligent researcher. Use the web_search tool to find accurate and up-to-date information. Summarize your findings clearly.",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.5,
            "tools": '["web_search"]'
        }

        # 2. Register the Agent
        print(f"📝 Registering '{agent_data['name']}' agent...")
        agent = client.agents.register(agent_data)
        print(f"✅ Agent Registered! ID: {agent['id']}")

        # 3. Create a Task
        prompt = "What are the latest breakthroughs in solid-state batteries?"
        print(f"\n🚀 Submitting Task: '{prompt}'")
        task = client.tasks.create(agent_id=agent['id'], input=prompt)
        task_id = task['id']
        print(f"✅ Task Created! ID: {task_id}")

        # 4. Monitor Task Status
        print("\n⏳ Waiting for task completion...")
        while True:
            status = client.tasks.get(task_id)
            print(f"Current Status: {status['status']}")
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                print("\n🎉 Task Finished!")
                print("="*40)
                print("Final Output:\n")
                print(status.get('output', 'No output received.'))
                print("="*40)
                break
            
            time.sleep(3)

if __name__ == "__main__":
    main()
