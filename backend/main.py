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

    # Load config after src is in path
    from agentos.core.runtime.config import config

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
