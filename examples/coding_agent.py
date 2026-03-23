"""
Example: Coding Agent
This script demonstrates an agent with filesystem access to write code.
"""
import time
from agentos.sdk.client import AgentOS

def main():
    print("🤖 Initializing AgentOS Client...")
    with AgentOS() as client:
        agent_data = {
            "name": "Senior Developer",
            "description": "An AI developer that writes Python scripts.",
            "system_prompt": "You are an expert Python developer. Use the filesystem tool to write the code the user requests into a file named 'generated_script.py'. Ensure the code is production-ready and fully commented.",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.2,
            "tools": '["filesystem"]'
        }

        print(f"📝 Registering '{agent_data['name']}' agent...")
        agent = client.agents.register(agent_data)
        
        prompt = "Write a Python script that uses httpx to fetch data from the PokéAPI and prints the abilities of Pikachu. Save it to 'generated_script.py'."
        print(f"🚀 Submitting Task: '{prompt}'")
        task = client.tasks.create(agent_id=agent['id'], input=prompt)
        
        print("⏳ Waiting for task completion (this may take a minute)...")
        while True:
            status = client.tasks.get(task['id'])
            if status['status'] in ['completed', 'failed']:
                print(f"\n🎉 Task Finished with status: {status['status']}")
                print("Check your directory for 'generated_script.py'!")
                break
            time.sleep(3)

if __name__ == "__main__":
    main()
