import asyncio
import uuid
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlmodel import Session
from agentos.core.manager.database import engine, create_db_and_tables
from agentos.core.orchestrator.models import Task # Ensure Task table exists for FK
from agentos.services.evaluation.models import Evaluation, EvaluationBatch
from agentos.services.evaluation.service import run_evaluation_workflow, run_batch_evaluation

async def test_evaluation_pipeline():
    print("🚀 Starting Evaluation Pipeline Verification...")
    
    # 1. Initialize DB
    create_db_and_tables()
    
    with Session(engine) as session:
        # 2. Run a single evaluation
        print("\n📝 Testing Single Evaluation Workflow...")
        agent_id = "test-agent-eval"
        input_text = "What is the capital of France?"
        expected = "Paris"
        
        eval_result = await run_evaluation_workflow(
            session, 
            agent_id=agent_id, 
            input_text=input_text, 
            expected_output=expected
        )
        
        print(f"✅ Single Eval Status: {eval_result.status}")
        print(f"📈 Score: {eval_result.score}")
        print(f"📊 Metrics: {eval_result.metrics}")
        
        assert eval_result.status == "completed"
        assert eval_result.score is not None

        # 3. Run a batch evaluation
        print("\n📦 Testing Batch Evaluation Workflow...")
        cases = [
            {"input_text": "Tell me a joke", "expected_output": "why"},
            {"input_text": "Who won the world cup 2022?", "expected_output": "Argentina"}
        ]
        
        batch = await run_batch_evaluation(
            session, 
            name="Test Batch 1", 
            cases=cases, 
            agent_id=agent_id
        )
        
        print(f"✅ Batch Status: {batch.status}")
        
        # Verify batch evaluations
        from sqlmodel import select
        evals = session.exec(select(Evaluation).where(Evaluation.batch_id == batch.id)).all()
        print(f"🔢 Total evaluations in batch: {len(evals)}")
        
        assert len(evals) == 2
        for e in evals:
            print(f"  - Case Input: {e.agent_id} | Score: {e.score} | Status: {e.status}")
            assert e.status == "completed"

    print("\n🎉 Evaluation Pipeline Verification SUCCESSFUL!")

if __name__ == "__main__":
    asyncio.run(test_evaluation_pipeline())
