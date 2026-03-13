
import asyncio
import os
import sys

# Ensure src is in sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agentos.core.runtime.runtime import AgentRuntime

async def test_long_term_memory():
    print("\n--- Phase 5.2: Long-term Memory (Qdrant + FastEmbed) Test ---")
    
    # Instance 1: Teacher Agent
    # This agent will store a secret in the knowledge base
    teacher = AgentRuntime(
        model="llama-3.3-70b-versatile",
        tools=["save_to_knowledge_base"]
    )
    
    print("\n--- Step 1: Teacher stores a secret ---")
    question1 = "Please save this information to your knowledge base: 'The favorite travel destination of the CEO is Mars'."
    print(f"User: {question1}")
    
    result1 = await teacher.run(question1)
    print(f"Agent: {result1.get('output')}")

    # Diagnosis: Check if anything is in Qdrant
    from agentos.core.memory.vector import vector_memory
    points = vector_memory.list_all_points()
    print(f"\n[DIAGNOSIS] Current Qdrant points count: {len(points)}")
    for p in points:
        print(f" - Point ID: {p.id}, Content: {p.payload.get('content')[:50]}")

    # Instance 2: Forgetful Agent (New instance, no history/thread)
    # This agent has no idea what happened above, but can search the database
    student = AgentRuntime(
        model="llama-3.3-70b-versatile",
        tools=["query_knowledge_base"]
    )
    
    print("\n--- Step 2: Student retrieves the information ---")
    question2 = "Where does the CEO like to travel according to our knowledge base?"
    print(f"User: {question2}")
    
    result2 = await student.run(question2)
    print(f"Agent: {result2.get('output')}")
    
    output = result2.get('output', '').lower()
    if "mars" in output:
        print("\n[SUCCESS] Agent retrieved the fact from long-term memory!")
    else:
        print("\n[FAILED] Agent couldn't find the information.")

if __name__ == "__main__":
    asyncio.run(test_long_term_memory())
