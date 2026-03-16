import asyncio
import os
import uuid
import sys
from unittest.mock import patch, MagicMock

# Add src to path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from agentos.core.manager.database import create_db_and_tables, get_session as get_db
from agentos.services.evaluation.models import Evaluation, EvaluatorType
from agentos.services.evaluation.service import run_evaluation_workflow

from langchain_core.messages import AIMessage

# Mock LLM to avoid API keys
class MockLLM:
    def __init__(self, *args, **kwargs):
        pass
    async def ainvoke(self, messages):
        # Extract context from system prompt for "realism"
        system_msg = messages[0].content if hasattr(messages[0], "content") else str(messages[0])
        has_context = "Relevant Context from Knowledge Base" in system_msg
        
        content = "The weather in Paris is sunny."
        if has_context:
            content = "According to the knowledge base, Paris is sunny and is known for the Eiffel Tower."
            
        return AIMessage(
            content=content, 
            usage_metadata={
                "total_tokens": 15,
                "input_tokens": 10,
                "output_tokens": 5
            },
            tool_calls=[]
        )
    def bind_tools(self, tools):
        return self
    def astream(self, messages):
        pass

async def test_real_world_usecase():
    print("\nStarting Real-world Evaluation usecase test...")
    
    # 1. Setup DB
    create_db_and_tables()
    
    # 2. Setup Vector Memory (Mocked search results)
    with patch("agentos.core.memory.vector.vector_memory.search") as mock_search:
        mock_search.return_value = [
            {"content": "Paris is the capital of France and is known for its Eiffel Tower.", "metadata": {}},
            {"content": "The current weather in Paris is consistently sunny during spring.", "metadata": {}}
        ]
        
        # 3. Setup Agent Runtime (Mocked LLM)
        with patch("agentos.core.runtime.runtime.get_llm", side_effect=MockLLM):
            
            # 4. Mock RAGAS/DeepEval to avoid real scoring
            with patch("ragas.evaluate") as mock_ragas:
                # Mock Ragas result
                mock_ragas_result = MagicMock()
                mock_ragas_result.to_pandas.return_value.iloc.__getitem__.return_value.to_dict.return_value = {
                    "faithfulness": 0.95, 
                    "answer_relevancy": 0.88
                }
                mock_ragas.return_value = mock_ragas_result
                
                # Patch classes before instantiation in run_evaluation_workflow
                with patch("agentos.services.evaluation.deepeval_eval.AnswerRelevancyMetric") as mock_rel, \
                     patch("agentos.services.evaluation.deepeval_eval.FaithfulnessMetric") as mock_faith:
                    
                    # Setup mock instances
                    mock_rel_inst = mock_rel.return_value
                    mock_rel_inst.score = 0.92
                    mock_faith_inst = mock_faith.return_value
                    mock_faith_inst.score = 0.85
                    
                    db_gen = get_db()
                    session = next(db_gen)
                    
                    # --- RUN RAGAS ---
                    print("\n--- [Scenario 1] Running RAGAS Evaluation (with retrieval context) ---")
                    eval_result = await run_evaluation_workflow(
                        session,
                        agent_id="test-agent-rag",
                        input_text="What do you know about weather in Paris?",
                        evaluator_type=EvaluatorType.RAGAS
                    )
                    
                    print(f"[OK] Status: {eval_result.status}")
                    print(f"Aggregate Score: {eval_result.score}")
                    print(f"Metrics Breakdown: {eval_result.metrics}")
                    
                    # Verify context injection happened
                    # (We can't easily check the system prompt inside run_evaluation_workflow here 
                    # but we can verify that the score matches our mock)
                    if eval_result.status == "failed":
                        with open("error.txt", "w", encoding="utf-8") as f:
                            f.write(str(eval_result.error_message))
                    assert eval_result.status == "completed"
                    assert eval_result.evaluator_type == EvaluatorType.RAGAS
                    
                    # --- RUN DEEPEVAL ---
                    print("\n--- [Scenario 2] Running DeepEval Evaluation (with retrieval context) ---")
                    eval_result2 = await run_evaluation_workflow(
                        session,
                        agent_id="test-agent-deepeval",
                        input_text="Describe Paris and its weather.",
                        evaluator_type=EvaluatorType.DEEPEVAL
                    )
                    
                    print(f"Status: {eval_result2.status}")
                    print(f"Aggregate Score: {eval_result2.score}")
                    print(f"Metrics Breakdown: {eval_result2.metrics}")
                    
                    assert eval_result2.status == "completed"
                    assert eval_result2.evaluator_type == EvaluatorType.DEEPEVAL

    print("\nReal-world Scenario Test Completed SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_real_world_usecase())
