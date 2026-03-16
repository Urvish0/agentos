import abc
from typing import Any, Dict, List, Optional
from agentos.services.evaluation.models import Evaluation

class BaseEvaluator(abc.ABC):
    """
    Abstract base class for all AgentOS evaluators.
    """
    
    @abc.abstractmethod
    def evaluate(self, 
                 task_id: str, 
                 agent_input: str, 
                 agent_output: str, 
                 context_retrieved: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute evaluation logic."""
        pass
