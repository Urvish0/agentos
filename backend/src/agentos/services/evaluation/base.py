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
                 context_retrieved: Optional[List[str]] = None) -> Evaluation:
        """
        Execute the evaluation logic and return an Evaluation model record.
        
        Args:
            task_id: The ID of the task being evaluated.
            agent_input: The initial prompt or goal given to the agent.
            agent_output: The final output produced by the agent.
            context_retrieved: Optional list of context strings retrieved during the task.
        """
        pass
