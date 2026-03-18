"""
Metrics API Routes for AgentOS Dashboard.

Provides aggregated statistics for token usage, latency, and success rates.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from agentos.core.manager.database import get_session
from agentos.core.orchestrator.models import Task, TaskStatus

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/summary")
def get_metrics_summary(session: Session = Depends(get_session)):
    """
    Get aggregated performance and usage metrics for the dashboard.
    Calculated from historical task data.
    """
    # 1. Total Tasks
    total_tasks = session.scalar(select(func.count(Task.id))) or 0
    
    # 2. Token Usage
    total_tokens = session.scalar(select(func.sum(Task.total_tokens))) or 0
    
    # 3. Latency Metrics
    # Filter for tasks that have a non-zero execution time (usually completed/failed)
    avg_latency = session.scalar(
        select(func.avg(Task.execution_time_ms)).where(Task.execution_time_ms > 0)
    ) or 0.0
    
    # 4. Success Rate
    completed_tasks = session.scalar(
        select(func.count(Task.id)).where(Task.status == TaskStatus.COMPLETED.value)
    ) or 0
    
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 100.0
    
    # 5. Usage by Model
    # Get total tokens and task count grouped by model
    model_usage_query = session.exec(
        select(Task.model, func.sum(Task.total_tokens), func.count(Task.id))
        .where(Task.model != "")
        .group_by(Task.model)
    ).all()
    
    model_usage = [
        {"model": m, "tokens": t, "tasks": c} 
        for m, t, c in model_usage_query
    ]
    
    # 6. Recent Throughput (Last 7 days - simplified for MVP)
    # For a real implementation, we'd group by day. 
    # For now, we return the global aggregates.
    
    return {
        "total_tasks": total_tasks,
        "total_tokens": total_tokens,
        "avg_latency_ms": round(float(avg_latency), 2),
        "success_rate": round(float(success_rate), 1),
        "model_usage": model_usage,
    }
