# ---------------------------------------------------------------------------
# A thread‑safe, in‑memory registry that tracks long‑running background jobs 
# ---------------------------------------------------------------------------
from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Dict

class JobRegistry:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    # ───────────────────────── CRUD helpers ──────────────────────────
    def create(self, filename: str) -> str:
        """Register a new job and return its unique job_id."""
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "file":        filename,
                "created_at":  time.time(),
                "state":       "queued",    # queued | parsing | chunking | embedding | storing | done | error
                "progress":    0.0,
                "error":       None,
            }
        return job_id

    def update(self, job_id: str, **changes) -> None:
        """Atomically merge *changes* (state, progress, error…) into the job dict."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(changes)

    def get(self, job_id: str) -> Dict[str, Any] | None:
        """Return the job dict or *None* if the id is unknown."""
        with self._lock:
            return self._jobs.get(job_id)

    def delete(self, job_id: str) -> None:
        """Remove a job from the registry."""
        with self._lock:
            self._jobs.pop(job_id, None)

    # ───────────────────────── housekeeping ─────────────────────────
    def cleanup(self, older_than_sec: int = 24 * 3600) -> None:
        """
        Delete finished jobs that are older than *older_than_sec* seconds.
        Call this periodically (e.g. in /status or via a cron).
        """
        now = time.time()
        with self._lock:
            for jid, job in list(self._jobs.items()):
                if job["state"] in {"done", "error"} and now - job["created_at"] > older_than_sec:
                    self._jobs.pop(jid, None)

# ---------------------------------------------------------------------------
# Global singleton – import `jobs` wherever you need to read/update progress.
# ---------------------------------------------------------------------------
jobs = JobRegistry()
