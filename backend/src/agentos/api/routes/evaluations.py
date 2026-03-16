import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from agentos.core.manager.database import get_session as get_db
from agentos.services.evaluation.models import (
    Evaluation, 
    EvaluationCreate, 
    EvaluationResponse,
    EvaluationBatchResponse,
    EvaluationCase,
    EvaluatorType
)
from agentos.services.evaluation import service

router = APIRouter(prefix="/evaluations", tags=["evaluations"])

class BatchEvalRequest(BaseModel):
    name: str
    agent_id: str
    cases: List[Dict[str, str]]
    evaluator_type: EvaluatorType = EvaluatorType.SIMPLE

@router.post("/run", response_model=EvaluationResponse)
async def run_evaluation(agent_id: str, 
                         input_text: str, 
                         expected_output: Optional[str] = None, 
                         evaluator_type: EvaluatorType = EvaluatorType.SIMPLE,
                         db=Depends(get_db)):
    """Trigger a new evaluation pipeline (Agent Run -> Scorer)."""
    return await service.run_evaluation_workflow(db, agent_id, input_text, expected_output, evaluator_type=evaluator_type)

@router.post("/batch", response_model=EvaluationBatchResponse)
async def run_batch_evaluation(request: BatchEvalRequest, db=Depends(get_db)):
    """Run a batch of evaluations."""
    return await service.run_batch_evaluation(
        db, 
        name=request.name, 
        cases=request.cases, 
        agent_id=request.agent_id,
        evaluator_type=request.evaluator_type
    )

@router.get("", response_model=List[EvaluationResponse])
def list_evaluations(task_id: Optional[uuid.UUID] = None, batch_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """List evaluations, optionally filtering by task_id or batch_id."""
    return service.list_evaluations(db, task_id=task_id, batch_id=batch_id, skip=skip, limit=limit)

@router.get("/{eval_id}", response_model=EvaluationResponse)
def get_evaluation(eval_id: uuid.UUID, db=Depends(get_db)):
    """Get details of a specific evaluation."""
    db_eval = service.get_evaluation(db, eval_id)
    if not db_eval:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return db_eval
