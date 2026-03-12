
import subprocess
import sys
import tempfile
import os
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()

class PythonExecutorArgs(BaseModel):
    code: str = Field(..., description="The Python code to execute.")
    timeout: int = Field(default=30, description="Max execution time in seconds.")

def execute_python(code: str, timeout: int = 30) -> str:
    """
    Executes a snippet of Python code and returns its stdout and stderr.
    This is useful for data processing, calculations, or creating new logic.
    """
    logger.info("Executing Python snippet", code_length=len(code))
    
    # Use a temporary file to store the code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
        
    try:
        # Run as a subprocess for basic isolation
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
            
        if not output:
            return "Success: Execution finished with no output."
            
        return "\n".join(output)
        
    except subprocess.TimeoutExpired:
        return f"Error: Execution timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing Python: {str(e)}"
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
