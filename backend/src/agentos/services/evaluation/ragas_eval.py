from typing import List, Dict, Any, Optional
from agentos.services.evaluation.base import BaseEvaluator
import pandas as pd
from ragas import evaluate as ragas_evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_openai import ChatOpenAI # Default for Ragas usually, might need config

class RagasEvaluator(BaseEvaluator):
    """
    Evaluator using the RAGAS framework for RAG-specific metrics.
    """
    
    def __init__(self, metrics: List[Any] = None):
        # Default metrics if none provided
        self.metrics = metrics or [faithfulness, answer_relevancy]

    def evaluate(self, 
                 task_id: str, 
                 agent_input: str, 
                 agent_output: str, 
                 context_retrieved: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Runs RAGAS evaluation for a single sample.
        """
        # RAGAS expects a dataset (pandas/hf)
        data = {
            "question": [agent_input],
            "answer": [agent_output],
            "contexts": [context_retrieved or [""]],
            "ground_truth": [""] # Placeholder, can be extended later
        }
        
        df = pd.DataFrame(data)
        
        try:
            # Note: Ragas requires an LLM for scoring (usually OpenAI)
            # This implementation assumes env vars like OPENAI_API_KEY are set
            result = ragas_evaluate(
                df,
                metrics=self.metrics,
            )
            
            # Extract scores
            scores = result.to_pandas().iloc[0].to_dict()
            aggregate_score = sum(scores[m.name] for m in self.metrics) / len(self.metrics)
            
            return {
                "score": round(float(aggregate_score), 2),
                "metrics": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in scores.items()},
                "status": "completed"
            }
        except Exception as e:
            return {
                "score": 0.0,
                "metrics": {},
                "status": "failed",
                "error": str(e)
            }
