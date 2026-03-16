import sys
import os
import uuid
import asyncio
from typing import List

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlmodel import Session, create_engine, SQLModel, select
from agentos.core.manager.database import create_db_and_tables, get_session
from agentos.services.evaluation.models import Evaluation, EvaluationBatch, EvaluatorType
from agentos.core.orchestrator.models import Task
from agentos.services.evaluation import reporting

# Setup test DB
sqlite_url = "sqlite:///./verify_phase7.db"
engine = create_engine(sqlite_url)

async def verify_reporting():
    print("🚀 Initializing verification database...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print("📝 Creating sample evaluation batch...")
        batch = EvaluationBatch(
            name="Phase 7.3 Verification Batch", 
            status="completed", 
            evaluator_type=EvaluatorType.SIMPLE,
            created_at=None # SQLModel handles this
        )
        session.add(batch)
        session.commit()
        session.refresh(batch)
        
        # Add sample data
        evals = [
            Evaluation(
                agent_id="travel-agent-v1",
                eval_type="simple",
                score=0.95,
                metrics={"accuracy": 0.9, "relevancy": 1.0},
                usage_metadata={"total_tokens": 120, "input_tokens": 80, "output_tokens": 40},
                status="completed",
                batch_id=batch.id
            ),
            Evaluation(
                agent_id="travel-agent-v1",
                eval_type="simple",
                score=0.4, # Fail
                metrics={"accuracy": 0.3, "relevancy": 0.5},
                usage_metadata={"total_tokens": 200, "input_tokens": 150, "output_tokens": 50},
                status="completed",
                batch_id=batch.id
            )
        ]
        session.add_all(evals)
        session.commit()
        
        print(f"📊 Generating Reports for Batch ID: {batch.id}")
        
        # Test JSON
        report_json = reporting.generate_json_report(session, batch.id)
        print(f"✅ JSON Report Summary: Pass Rate: {report_json['summary']['pass_rate']}%")
        
        # Test HTML
        report_html = reporting.generate_html_report(session, batch.id)
        report_path = os.path.abspath("eval_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_html)
        
        file_url = f"file:///{report_path.replace(os.sep, '/')}"
        print(f"✅ HTML Report saved to: {report_path}")
        print(f"🔗 Click to open: {file_url}")
        
        # Automatically open in default browser
        import webbrowser
        print("\n🌐 Opening report in your default browser...")
        webbrowser.open(file_url)
        
        print("\nVerification Successful! The premium report should now be open in your browser.")

if __name__ == "__main__":
    asyncio.run(verify_reporting())
