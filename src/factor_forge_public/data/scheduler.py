from __future__ import annotations

import time
from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class PollingJob(BaseModel):
    name: str
    resource: str
    interval_seconds: float = Field(gt=0.0)
    enabled: bool = True
    parameters: dict[str, str | int | float | bool] = Field(default_factory=dict)


@dataclass
class PollingScheduler:
    """Pure scheduling helper with no networking or credentials."""

    jobs: list[PollingJob]
    last_run_monotonic: dict[str, float] = field(default_factory=dict)

    def due_jobs(self, *, now: float | None = None) -> list[PollingJob]:
        current = time.monotonic() if now is None else now
        return [
            job
            for job in self.jobs
            if job.enabled
            and (
                job.name not in self.last_run_monotonic
                or current - self.last_run_monotonic[job.name] >= job.interval_seconds
            )
        ]

    def mark_ran(self, job: PollingJob, *, now: float | None = None) -> None:
        self.last_run_monotonic[job.name] = time.monotonic() if now is None else now
