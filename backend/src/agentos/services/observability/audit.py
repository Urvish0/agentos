import json
import hashlib
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

class AuditLogger:
    """
    Immutable Audit Logger that creates a tamper-evident cryptographic hash chain.
    """
    def __init__(self, log_dir: str = "../storage/audit", filename: str = "audit_log.jsonl"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.log_dir / filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure the audit log file exists and has an initial genesis block if empty."""
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            genesis_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "system",
                "action": "system_initialized",
                "resource": "audit_log",
                "details": {"message": "Audit log initialized"},
                "previous_hash": "0" * 64
            }
            # Calculate genesis hash
            entry_str = json.dumps(genesis_entry, sort_keys=True)
            genesis_entry["hash"] = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
            
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(genesis_entry) + "\n")

    def _get_last_hash(self) -> str:
        """Read the last entry in the log to get its hash."""
        try:
            with open(self.file_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                if f.tell() == 0:
                    return "0" * 64
                
                # Try reading the last line
                f.seek(-2, os.SEEK_END)
                while f.tell() > 0 and f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                
                last_line = f.readline().decode()
                if not last_line.strip():
                    return "0" * 64
                    
                last_entry = json.loads(last_line)
                return last_entry.get("hash", "0" * 64)
        except Exception:
            return "0" * 64

    def log_sensitive_action(
        self, 
        actor: str, 
        action: str, 
        resource: str, 
        details: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        """
        Record a sensitive action into the tamper-evident log.
        """
        previous_hash = self._get_last_hash()
        
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "details": details,
            "trace_id": trace_id,
            "previous_hash": previous_hash
        }
        
        # Calculate hash of the content so far (without the hash field itself)
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
        
        # Append atomically 
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def verify_audit_chain(self) -> bool:
        """
        Verify the integrity of the audit log by recalculating hashes.
        Returns True if the chain is intact, raises ValueError if tampered.
        """
        if not self.file_path.exists():
            return True
            
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            return True
            
        expected_previous_hash = "0" * 64
        
        for i, line in enumerate(lines):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"Corrupted JSON format at line {i+1}")
                
            stored_hash = entry.pop("hash", None)
            if stored_hash is None:
                raise ValueError(f"Missing hash at line {i+1}")
                
            actual_previous_hash = entry.get("previous_hash")
            if i == 0 and actual_previous_hash != expected_previous_hash:
                # Genesis block usually has a different rule, but we enforce "0"*64
                raise ValueError(f"Genesis block tampering at line {i+1}")
            elif i > 0 and actual_previous_hash != expected_previous_hash:
                raise ValueError(f"Broken hash chain at line {i+1}. Expected prev: {expected_previous_hash}, Found: {actual_previous_hash}")
                
            # Recalculate hash
            entry_str = json.dumps(entry, sort_keys=True)
            calculated_hash = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
            
            if calculated_hash != stored_hash:
                raise ValueError(f"Tampered content at line {i+1}. Hash mismatch.")
                
            expected_previous_hash = calculated_hash
            
        return True

# Global instance for ease of use
audit_logger = AuditLogger()
