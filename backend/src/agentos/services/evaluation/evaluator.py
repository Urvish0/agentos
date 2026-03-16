from typing import List, Dict, Any, Optional
from agentos.services.evaluation.base import BaseEvaluator
from agentos.services.evaluation.models import Evaluation

class SimpleEvaluator(BaseEvaluator):
    """
    A basic evaluator that scores based on response length and keyword presence.
    """
    
    def __init__(self, keywords: List[str] = None, min_length: int = 20):
        self.keywords = keywords or []
        self.min_length = min_length

    def evaluate(self, 
                 task_id: str, 
                 agent_input: str, 
                 agent_output: str, 
                 context_retrieved: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Calculates a simple score based on heuristics.
        """
        score = 0.0
        metrics = {}
        
        # 1. Length check (0.3 weight)
        length = float(len(agent_output))
        length_score = min(1.0, length / float(self.min_length))
        score += length_score * 0.3
        metrics["length_score"] = round(float(length_score), 2)
        metrics["output_length"] = int(length)
        
        # 2. Keyword check (0.7 weight)
        if self.keywords:
            found = [k for k in self.keywords if k.lower() in agent_output.lower()]
            keyword_score = float(len(found)) / float(len(self.keywords))
            score += keyword_score * 0.7
            metrics["keyword_score"] = round(float(keyword_score), 2)
            metrics["keywords_found"] = found
        else:
            # If no keywords expected, we give full marks for reasoning if length is okay
            score += 0.7
            metrics["keyword_score"] = 1.0
            
        return {
            "score": round(float(score), 2),
            "metrics": metrics,
            "status": "completed"
        }
