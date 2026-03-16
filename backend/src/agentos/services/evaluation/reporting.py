import uuid
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from datetime import datetime
from agentos.services.evaluation.models import Evaluation, EvaluationBatch

def calculate_batch_stats(evaluations: List[Evaluation], threshold: float = 0.7) -> Dict[str, Any]:
    """
    Calculates summary statistics for a list of evaluations.
    """
    if not evaluations:
        return {}

    total_evals = len(evaluations)
    completed_evals = [e for e in evaluations if e.status == "completed"]
    failed_evals = [e for e in evaluations if e.status == "failed"]
    
    # Pass/Fail based on threshold
    passed_count = len([e for e in completed_evals if e.score and e.score >= threshold])
    
    # Aggregate scores
    avg_score = sum(e.score for e in completed_evals if e.score is not None) / len(completed_evals) if completed_evals else 0
    
    # Metric averages
    metric_sums = {}
    metric_counts = {}
    for e in completed_evals:
        if e.metrics:
            for k, v in e.metrics.items():
                if isinstance(v, (int, float)):
                    metric_sums[k] = metric_sums.get(k, 0) + v
                    metric_counts[k] = metric_counts.get(k, 0) + 1
    
    avg_metrics = {k: round(metric_sums[k] / metric_counts[k], 2) for k in metric_sums}
    
    # Token usage
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    for e in completed_evals:
        if e.usage_metadata:
            total_tokens += e.usage_metadata.get("total_tokens", 0)
            # Support both old and new naming for robustness
            prompt_tokens += e.usage_metadata.get("input_tokens", e.usage_metadata.get("prompt_tokens", 0))
            completion_tokens += e.usage_metadata.get("output_tokens", e.usage_metadata.get("completion_tokens", 0))

    return {
        "total_cases": total_evals,
        "completed_cases": len(completed_evals),
        "failed_cases": len(failed_evals),
        "pass_rate": round((passed_count / total_evals) * 100, 2) if total_evals > 0 else 0,
        "average_score": round(avg_score, 2),
        "average_metrics": avg_metrics,
        "total_usage": {
            "total_tokens": total_tokens,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens
        }
    }

def generate_json_report(db: Session, batch_id: uuid.UUID) -> Dict[str, Any]:
    """
    Generates a structured JSON report for a batch.
    """
    batch = db.get(EvaluationBatch, batch_id)
    if not batch:
        return {"error": "Batch not found"}
    
    evals = db.exec(select(Evaluation).where(Evaluation.batch_id == batch_id)).all()
    stats = calculate_batch_stats(evals)
    
    return {
        "batch_info": {
            "id": str(batch.id),
            "name": batch.name,
            "evaluator": batch.evaluator_type,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "status": batch.status
        },
        "summary": stats,
        "evaluations": [
            {
                "id": str(e.id),
                "agent_id": e.agent_id,
                "score": e.score,
                "metrics": e.metrics,
                "status": e.status,
                "error": e.error_message
            } for e in evals
        ]
    }

def get_score_color(score: Optional[float]) -> str:
    """Helper to map score to Green/Yellow/Red."""
    if score is None:
        return "#94a3b8"  # Slate-400 (Muted)
    if score >= 0.8:
        return "#22c55e"  # Green-500
    if score >= 0.5:
        return "#eab308"  # Yellow-500
    return "#ef4444"      # Red-500

def generate_html_report(db: Session, batch_id: uuid.UUID) -> str:
    """
    Generates a premium Dark Mode HTML report for a batch with Green/Yellow/Red status indicators.
    """
    data = generate_json_report(db, batch_id)
    if "error" in data:
        return f"<html><body style='background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:50px;'><h1>Error: {data['error']}</h1></body></html>"
    
    batch = data["batch_info"]
    summary = data["summary"]
    evals = data["evaluations"]
    
    # Pre-calculate category colors for the summary
    pass_rate_color = get_score_color(summary['pass_rate'] / 100)
    avg_score_color = get_score_color(summary['average_score'])
    
    # Modern HTML template with Premium Dark Mode styling
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AgentOS Evaluation | {batch['name']}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #030712;
                --card-bg: #111827;
                --card-hover: #1f2937;
                --text: #f9fafb;
                --text-muted: #9ca3af;
                --border: #374151;
                --primary: #3b82f6;
                --success: #22c55e;
                --warning: #eab308;
                --error: #ef4444;
                --glass: rgba(255, 255, 255, 0.03);
            }}
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg);
                background-image: radial-gradient(circle at 50% -20%, #1e1b4b 0%, var(--bg) 80%);
                color: var(--text);
                margin: 0;
                padding: 60px 20px;
                line-height: 1.5;
            }}
            .container {{ max-width: 1100px; margin: 0 auto; }}
            
            /* Header Styling */
            .header {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 50px;
                background: var(--glass);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid var(--border);
                backdrop-filter: blur(10px);
            }}
            .header-info h1 {{ margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; color: #fff; }}
            .header-info p {{ color: var(--text-muted); margin: 8px 0 0; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; }}
            .status-badge {{
                padding: 8px 16px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                background: rgba(59, 130, 246, 0.1);
                color: var(--primary);
                border: 1px solid rgba(59, 130, 246, 0.2);
            }}

            /* Stats Grid */
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
                gap: 24px; 
                margin-bottom: 50px; 
            }}
            .stat-card {{ 
                background: var(--card-bg); 
                padding: 32px; 
                border-radius: 20px; 
                border: 1px solid var(--border); 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }}
            .stat-card:hover {{ transform: translateY(-5px); border-color: var(--text-muted); background: var(--card-hover); }}
            .stat-card::after {{
                content: '';
                position: absolute;
                top: 0; left: 0; width: 4px; height: 100%;
                background: var(--primary);
                opacity: 0.5;
            }}
            .stat-card.pass::after {{ background: var(--success); }}
            .stat-card.warn::after {{ background: var(--warning); }}
            .stat-card.error::after {{ background: var(--error); }}
            
            .stat-value {{ display: block; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px; color: #fff; }}
            .stat-label {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }}
            
            /* Table Styling */
            .table-container {{ 
                background: var(--card-bg); 
                border-radius: 20px; 
                border: 1px solid var(--border); 
                overflow: hidden; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ 
                background: rgba(255,255,255,0.02); 
                padding: 20px; 
                text-align: left; 
                color: var(--text-muted); 
                font-size: 0.75rem; 
                text-transform: uppercase; 
                letter-spacing: 0.1em;
                border-bottom: 1px solid var(--border);
            }}
            td {{ padding: 20px; border-bottom: 1px solid var(--border); font-size: 0.95rem; }}
            tr:last-child td {{ border-bottom: none; }}
            tr:hover td {{ background: rgba(255,255,255,0.01); }}
            
            .agent-name {{ font-weight: 600; color: #fff; }}
            .eval-id {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--text-muted); }}
            
            /* Score Pillars */
            .score-container {{ display: flex; align-items: center; gap: 12px; }}
            .score-track {{ 
                height: 10px; 
                width: 120px; 
                background: #1f2937; 
                border-radius: 5px; 
                overflow: hidden; 
                border: 1px solid rgba(255,255,255,0.05);
            }}
            .score-fill {{ height: 100%; transition: width 1s ease-out; }}
            .score-text {{ font-weight: 700; font-family: 'JetBrains Mono', monospace; width: 40px; }}
            
            /* Enhanced Indicators */
            .indicator {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 10px;
                border-radius: 8px;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
            }}
            .ind-success {{ background: rgba(34, 197, 94, 0.1); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.2); }}
            .ind-warning {{ background: rgba(234, 179, 8, 0.1); color: var(--warning); border: 1px solid rgba(234, 179, 8, 0.2); }}
            .ind-error {{ background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }}

            footer {{
                margin-top: 60px;
                text-align: center;
                color: var(--text-muted);
                font-size: 0.85rem;
                border-top: 1px solid var(--border);
                padding-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <div class="header-info">
                    <h1>{batch['name']}</h1>
                    <p>BATCH::{batch['id']} // {batch['evaluator'].upper()}_ENGINE</p>
                </div>
                <div class="status-badge">{batch['status']}</div>
            </header>

            <section class="stats-grid">
                <div class="stat-card" style="--primary: {pass_rate_color}">
                    <span class="stat-value" style="color: {pass_rate_color}">{summary['pass_rate']}%</span>
                    <span class="stat-label">System Pass Rate</span>
                </div>
                <div class="stat-card" style="--primary: {avg_score_color}">
                    <span class="stat-value" style="color: {avg_score_color}">{summary['average_score']}</span>
                    <span class="stat-label">Average Performance</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{summary['total_usage']['total_tokens']}</span>
                    <span class="stat-label">Total Token Usage</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{summary['total_cases']}</span>
                    <span class="stat-label">Test Cases Executed</span>
                </div>
            </section>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Case / ID</th>
                            <th>Agent Identification</th>
                            <th>Performance Metric</th>
                            <th>Outcome</th>
                            <th>Granular Metrics</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for e in evals:
        score = e['score']
        score_pct = (score * 100) if score is not None else 0
        color = get_score_color(score)
        
        # Determine indicator class
        if score is None: ind_class = "ind-warning"; ind_label = "PENDING"
        elif score >= 0.8: ind_class = "ind-success"; ind_label = "PASS"
        elif score >= 0.5: ind_class = "ind-warning"; ind_label = "STABLE"
        else: ind_class = "ind-error"; ind_label = "FAIL"

        metrics_html = ""
        if e['metrics']:
            for k, v in e['metrics'].items():
                m_color = get_score_color(v if isinstance(v, (int, float)) else None)
                metrics_html += f"<span style='color: {m_color}; border-left: 2px solid {m_color}; padding-left: 6px; margin-right: 12px; font-size: 0.75rem; font-family: monospace;'>{k.upper()}: {v}</span>"

        html += f"""
                        <tr>
                            <td><span class="eval-id">EVAL_CASE::{e['id'][:8].upper()}</span></td>
                            <td class="agent-name">{e['agent_id']}</td>
                            <td>
                                <div class="score-container">
                                    <div class="score-track"><div class="score-fill" style="width: {score_pct}%; background: {color};"></div></div>
                                    <span class="score-text" style="color: {color}">{score if score is not None else '??'}</span>
                                </div>
                            </td>
                            <td><span class="indicator {ind_class}">{ind_label}</span></td>
                            <td>{metrics_html if metrics_html else '<span style="color:var(--text-muted)">-</span>'}</td>
                        </tr>
        """
        
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <footer>
                <div style="margin-bottom: 10px;">
                    <span style="color: var(--success)">● OPERATIONAL</span> &nbsp; 
                    <span style="color: var(--text-muted)">// AGENTOS_ENGINE_V1.0</span>
                </div>
                Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC
            </footer>
        </div>
    </body>
    </html>
    """
    return html
