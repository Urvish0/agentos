import uvicorn
import os
import sys

def main():
    """
    Entry point for the AgentOS Backend.
    """
    # Ensure src is in PYTHONPATH
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Load .env into os.environ for OpenTelemetry
    from dotenv import load_dotenv
    load_dotenv()

    # Load config after src is in path
    from agentos.core.runtime.config import config

    # Ensure PROMETHEUS_MULTIPROC_DIR exists
    metrics_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if metrics_dir:
        os.makedirs(metrics_dir, exist_ok=True)
        # Clean up old metrics on startup of the main application
        for f in os.listdir(metrics_dir):
            if f.endswith(".db"):
                try:
                    os.remove(os.path.join(metrics_dir, f))
                except OSError:
                    pass

    uvicorn.run(
        "agentos.api.app:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
