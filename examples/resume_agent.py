"""
Example: Resume Agent
This script demonstrates using an agent to format raw markdown into a professional resume.
"""
import time
from agentos.sdk.client import AgentOS

def main():
    print("🤖 Initializing AgentOS Client...")
    with AgentOS() as client:
        agent_data = {
            "name": "Career Coach",
            "description": "Expert at writing and formatting technical resumes.",
            "system_prompt": "You are a professional resume writer. Take the user's raw experience and format it into a stunning, ATS-friendly markdown resume. Highlight action verbs and metrics.",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.4,
            "tools": '[]'
        }

        print(f"📝 Registering '{agent_data['name']}' agent...")
        agent = client.agents.register(agent_data)
        
        raw_background = """
        Name: Jane Doe
        Jobs:
        - Worked at OCI from 2020 to 2023. Did backend Java stuff. Improved performance by 20%.
        - Startup XYZ 2018-2020. Built a Node.js API. 10k users.
        Education:
        B.S. Computer Science, State University, 2018.
        """

        print("🚀 Submitting Career Background...")
        task = client.tasks.create(
            agent_id=agent['id'], 
            input=f"Please format this into a professional Markdown resume:\n\n{raw_background}"
        )
        
        print("⏳ Waiting for career coach to finish writing...")
        while True:
            status = client.tasks.get(task['id'])
            if status['status'] == 'completed':
                print("\n🎉 Resume Generated!")
                print("="*50)
                print(status.get('output', 'No output received.'))
                print("="*50)
                break
            elif status['status'] == 'failed':
                print(f"❌ Task Failed.")
                break
            time.sleep(3)

if __name__ == "__main__":
    main()
