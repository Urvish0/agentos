from typing import List, Dict, Any, Optional
from agentos.services.evaluation.base import BaseEvaluator
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

class DeepEvalEvaluator(BaseEvaluator):
    """
    Evaluator using the DeepEval framework.
    """
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        # Initialize metrics
        self.metrics = [
            AnswerRelevancyMetric(threshold=threshold),
            FaithfulnessMetric(threshold=threshold)
        ]

    def evaluate(self, 
                 task_id: str, 
                 agent_input: str, 
                 agent_output: str, 
                 context_retrieved: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Runs DeepEval evaluation for a single test case.
        """
        test_case = LLMTestCase(
            input=agent_input,
            actual_output=agent_output,
            retrieval_context=context_retrieved or [""]
        )
        
        try:
            scores = {}
            for metric in self.metrics:
                metric.measure(test_case)
                scores[metric.__class__.__name__] = metric.score
            
            aggregate_score = sum(scores.values()) / len(scores)
            
            return {
                "score": round(float(aggregate_score), 2),
                "metrics": {k: round(float(v), 2) for k, v in scores.items()},
                "status": "completed"
            }
        except Exception as e:
            return {
                "score": 0.0,
                "metrics": {},
                "status": "failed",
                "error": str(e)
            }
