"""
Metrics collection for AgentOS using Prometheus.

This module defines counters, histograms, and other metrics to track agent performance,
token usage, and costs.
"""

import time
import os
from prometheus_client import Counter, Histogram, CollectorRegistry, multiprocess

# Create a custom registry for multi-process mode
# This relies on the PROMETHEUS_MULTIPROC_DIR environment variable
REGISTRY = CollectorRegistry()
if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    multiprocess.MultiProcessCollector(REGISTRY)


# ---------------------------------------------------------------------------
# Metrics Definitions
# ---------------------------------------------------------------------------

# Token Usage Counters
TOKENS_TOTAL = Counter(
    "agentos_tokens_total",
    "Total tokens consumed by agents",
    ["agent_id", "model", "provider", "token_type"],  # token_type: prompt, completion, total
    registry=REGISTRY
)

# Execution Time Histograms
EXECUTION_TIME = Histogram(
    "agentos_execution_time_seconds",
    "Time spent executing agent runs",
    ["agent_id", "model", "provider"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
    registry=REGISTRY
)

# Task Success/Failure Counters
TASKS_TOTAL = Counter(
    "agentos_tasks_total",
    "Total number of agent tasks executed",
    ["agent_id", "status"],  # status: success, failure
    registry=REGISTRY
)

# Cost Estimation (Approximation in USD)
COST_TOTAL = Counter(
    "agentos_cost_usd_total",
    "Estimated cost of agent runs in USD",
    ["agent_id", "model", "provider"],
    registry=REGISTRY
)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

# Approximate costs per 1M tokens (very rough estimates, should be updated)
COST_PER_1M_TOKENS = {
    "groq": {
        "llama-3.3-70b-versatile": 0.59,
        "llama-3.1-8b-instant": 0.05,
        "mixtral-8x7b-32768": 0.24,
    },
    "openai": {
        "gpt-4o": 5.0,
        "gpt-4o-mini": 0.15,
    },
    "anthropic": {
        "claude-3-5-sonnet-latest": 3.0,
        "claude-3-haiku-20240307": 0.25,
    }
}

def record_run_metrics(
    agent_id: str,
    model: str,
    provider: str,
    total_tokens: int,
    execution_time_ms: float,
    status: str = "success"
):
    """
    Record metrics for a single agent run.
    """
    # Record tokens
    TOKENS_TOTAL.labels(
        agent_id=agent_id, 
        model=model, 
        provider=provider, 
        token_type="total"
    ).inc(total_tokens)
    
    # Record execution time
    EXECUTION_TIME.labels(
        agent_id=agent_id, 
        model=model, 
        provider=provider
    ).observe(execution_time_ms / 1000.0)
    
    # Record task completion
    TASKS_TOTAL.labels(
        agent_id=agent_id, 
        status=status
    ).inc()
    
    # Record estimated cost
    provider_costs = COST_PER_1M_TOKENS.get(provider.lower(), {})
    cost_per_1m = provider_costs.get(model, 0.0) # Default to 0 if unknown
    
    # If not found directly, try a more relaxed match (common for versioned models)
    if cost_per_1m == 0.0:
        for m_name, cost in provider_costs.items():
            if m_name in model:
                cost_per_1m = cost
                break
                
    estimated_cost = (total_tokens / 1_000_000.0) * cost_per_1m
    COST_TOTAL.labels(
        agent_id=agent_id, 
        model=model, 
        provider=provider
    ).inc(estimated_cost)
