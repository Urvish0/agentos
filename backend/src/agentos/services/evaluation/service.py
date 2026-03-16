from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timezone
import uuid

from agentos.core.manager.database import get_session as get_db
from agentos.services.evaluation.models import Evaluation, EvaluationCreate, EvaluationBatch

def create_evaluation(db: Session, eval_data: EvaluationCreate) -> Evaluation:
    """Create a new evaluation record in the database."""
    db_eval = Evaluation.model_validate(eval_data)
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)
    return db_eval

def get_evaluation(db: Session, eval_id: uuid.UUID) -> Optional[Evaluation]:
    """Retrieve an evaluation record by ID."""
    return db.get(Evaluation, eval_id)

def list_evaluations(db: Session, task_id: Optional[uuid.UUID] = None, batch_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[Evaluation]:
    """List evaluations, optionally filtered by task_id or batch_id."""
    query = select(Evaluation)
    if task_id:
        query = query.where(Evaluation.task_id == task_id)
    if batch_id:
        query = query.where(Evaluation.batch_id == batch_id)
    query = query.offset(skip).limit(limit)
    return db.exec(query).all()

async def run_evaluation_workflow(db: Session, agent_id: str, input_text: str, expected_output: str = None, batch_id: uuid.UUID = None) -> Evaluation:
    """
    Executes the full evaluation pipeline:
    1. Run the agent.
    2. Score the agent output.
    3. Persist the results.
    """
    from agentos.core.runtime.runtime import AgentRuntime
    from agentos.services.evaluation.evaluator import SimpleEvaluator

    # 1. Initialize evaluation record
    eval_record = Evaluation(
        agent_id=agent_id,
        eval_type="simple",
        status="running",
        batch_id=batch_id
    )
    db.add(eval_record)
    db.commit()
    db.refresh(eval_record)

    try:
        # 2. Run Agent
        runtime = AgentRuntime()
        result = await runtime.run(input_text)
        
        # 3. Score Output
        evaluator = SimpleEvaluator(keywords=[expected_output] if expected_output else [])
        scores = evaluator.evaluate(
            task_id=str(eval_record.id),
            agent_input=input_text,
            agent_output=result["output"]
        )

        # 4. Update Record
        eval_record.score = scores["score"]
        eval_record.metrics = scores["metrics"]
        eval_record.status = "completed"
        eval_record.completed_at = datetime.now(timezone.utc)
        
    except Exception as e:
        eval_record.status = "failed"
        eval_record.error_message = str(e)
        eval_record.completed_at = datetime.now(timezone.utc)
    
    db.add(eval_record)
    db.commit()
    db.refresh(eval_record)
    return eval_record

async def run_batch_evaluation(db: Session, name: str, cases: List[Dict[str, str]], agent_id: str) -> EvaluationBatch:
    """
    Runs evaluation for multiple cases in sequence.
    """
    from agentos.services.evaluation.models import EvaluationBatch
    
    # Create batch
    batch = EvaluationBatch(name=name, status="running")
    db.add(batch)
    db.commit()
    db.refresh(batch)

    try:
        for case in cases:
            await run_evaluation_workflow(
                db, 
                agent_id=agent_id, 
                input_text=case["input_text"], 
                expected_output=case.get("expected_output"),
                batch_id=batch.id
            )
        batch.status = "completed"
    except Exception as e:
        batch.status = "failed"
        
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch
