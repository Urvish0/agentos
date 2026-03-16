import asyncio
import uuid
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlmodel import Session
from agentos.core.manager.database import engine, create_db_and_tables
from agentos.services.evaluation.models import Evaluation, EvaluatorType
from agentos.services.evaluation.service import run_evaluation_workflow

def log(msg):
    print(msg)
    with open("debug_test.log", "a") as f:
        f.write(str(msg) + "\n")

async def test_advanced_evaluators():
    if os.path.exists("debug_test.log"):
        os.remove("debug_test.log")
    log("Starting Advanced Evaluator Integration Tests...")
    
    # 1. Initialize DB
    create_db_and_tables()
    
    with Session(engine) as session:
        agent_id = "test-agent-advanced"
        input_text = "What is AgentOS?"
        output_text = "AgentOS is a powerful agentic operating system."
        
        # Mocking the AgentRuntime to avoid actual LLM calls pendanting the evaluation
        with patch("agentos.core.runtime.runtime.AgentRuntime.run", return_value={"output": output_text}):
            
            # 2. Test RAGAS Integration (Mocking Ragas evaluation to avoid OpenAI dep in test)
            print("\n- Testing RAGAS Evaluator...")
            with patch("agentos.services.evaluation.ragas_eval.ragas_evaluate") as mock_ragas:
                # Setup mock result
                mock_result = MagicMock()
                mock_result.to_pandas.return_value.iloc.__getitem__.return_value.to_dict.return_value = {
                    "faithfulness": 0.9,
                    "answer_relevancy": 0.8
                }
                mock_ragas.return_value = mock_result
                
                eval_result = await run_evaluation_workflow(
                    session, 
                    agent_id=agent_id, 
                    input_text=input_text, 
                    evaluator_type=EvaluatorType.RAGAS
                )
                
                print(f"[OK] RAGAS Eval Status: {eval_result.status}")
                print(f"Aggregate Score: {eval_result.score}")
                print(f"Metrics: {eval_result.metrics}")
                
                assert eval_result.status == "completed"
                assert eval_result.evaluator_type == EvaluatorType.RAGAS
                assert eval_result.score == 0.85 # (0.9 + 0.8) / 2

            # 3. Test DeepEval Integration (Mocking metrics)
            log("\n- Testing DeepEval Evaluator...")
            with patch("deepeval.metrics.AnswerRelevancyMetric"), \
                 patch("deepeval.metrics.FaithfulnessMetric"):
                
                with patch("agentos.services.evaluation.deepeval_eval.DeepEvalEvaluator.evaluate") as mock_eval:
                    mock_eval.return_value = {
                        "score": 0.90,
                        "metrics": {"AnswerRelevancyMetric": 0.95, "FaithfulnessMetric": 0.85},
                        "status": "completed"
                    }
                    
                    eval_result = await run_evaluation_workflow(
                        session, 
                        agent_id=agent_id, 
                        input_text=input_text, 
                        evaluator_type=EvaluatorType.DEEPEVAL
                    )
                
                log(f"[OK] DeepEval Eval Status: {eval_result.status}")
                if eval_result.status == "failed":
                    log(f"ERROR: {eval_result.error_message}")
                log(f"Aggregate Score: {eval_result.score} (type: {type(eval_result.score)})")
                log(f"Metrics: {eval_result.metrics}")
                
                assert eval_result.status == "completed"
                assert eval_result.evaluator_type == EvaluatorType.DEEPEVAL
                # (0.95 + 0.85) / 2 = 0.9
                score_val = float(eval_result.score) if eval_result.score is not None else 0.0
                log(f"DEBUG: score_val={score_val}")
                assert abs(score_val - 0.90) < 0.01

    print("\nAdvanced Evaluator Integrations Verified!")

if __name__ == "__main__":
    try:
        asyncio.run(test_advanced_evaluators())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
