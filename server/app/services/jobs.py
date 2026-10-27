"""Background jobs for long tasks (answer evals make many LLM calls). The UI polls a job's status.

In-memory and per server process: a restart forgets running jobs, but their results are files
(run folders), so nothing finished is lost.
"""
from __future__ import annotations

import threading
import time
import traceback
import uuid
from dataclasses import asdict, dataclass, field


@dataclass
class Job:
    id: str
    kind: str
    state: str = "running"          # running | done | error
    done: int = 0
    total: int | None = None
    result: dict | None = None
    error: str | None = None
    details: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)  # what the job is about, e.g. {"run": ..., "model": ...}
    started: float = field(default_factory=time.time)
    finished: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class JobManager:
    def __init__(self, keep: int = 50):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self.keep = keep

    def start(self, kind: str, fn, *args, meta: dict | None = None, **kwargs) -> Job:
        """Run fn(*args, progress=callback, **kwargs) in a thread. fn returns a dict (the job result)."""
        job = Job(id=uuid.uuid4().hex[:12], kind=kind, meta=dict(meta or {}))
        with self._lock:
            self._jobs[job.id] = job
            for old in sorted(self._jobs.values(), key=lambda j: j.started)[:-self.keep]:
                if old.state != "running":
                    del self._jobs[old.id]

        def progress(done: int, total: int) -> None:
            job.done, job.total = done, total

        def target():
            try:
                job.result = fn(*args, progress=progress, **kwargs)
                job.state = "done"
            except Exception as exc:  # noqa: BLE001 - reported to the UI
                job.state = "error"
                job.error = str(exc) or type(exc).__name__
                details = getattr(exc, "details", None)
                job.details = list(details) if details else traceback.format_exc().splitlines()[-3:]
            finally:
                job.finished = time.time()

        threading.Thread(target=target, daemon=True, name=f"job-{job.id}").start()
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def running(self, kind: str | None = None) -> list[Job]:
        return [j for j in self._jobs.values() if j.state == "running" and (kind is None or j.kind == kind)]
