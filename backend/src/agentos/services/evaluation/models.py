import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, SQLModel, JSON

class EvaluatorType(str, Enum):
    SIMPLE = "simple"
    RAGAS = "ragas"
    DEEPEVAL = "deepeval"
    CUSTOM = "custom"

class EvaluationBase(SQLModel):
    task_id: Optional[str] = Field(default=None, foreign_key="task.id")
    agent_id: str
    evaluator_type: EvaluatorType = Field(default=EvaluatorType.SIMPLE, description="Framework to use")
    eval_type: str = Field(description="E.g., 'ragas', 'deepeval', 'custom', 'simple'")
    score: Optional[float] = Field(default=None, description="Aggregate score 0.0 to 1.0")
    metrics: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    usage_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    status: str = Field(default="pending", description="pending, running, completed, failed")
    error_message: Optional[str] = None
    batch_id: Optional[uuid.UUID] = Field(default=None, foreign_key="evaluationbatch.id")

class Evaluation(EvaluationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class EvaluationBatch(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    evaluator_type: EvaluatorType = Field(default=EvaluatorType.SIMPLE)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="pending") # pending, running, completed, failed
    
class EvaluationCase(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    input_text: str
    expected_output: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationUpdate(SQLModel):
    score: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

class EvaluationResponse(EvaluationBase):
    id: uuid.UUID
    created_at: datetime
    completed_at: Optional[datetime]

class EvaluationBatchResponse(SQLModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    status: str
    evaluations: List[EvaluationResponse] = []
