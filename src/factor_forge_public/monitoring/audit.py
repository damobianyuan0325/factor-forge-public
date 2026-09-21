from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    timestamp_ms: int
    category: str
    action: str
    outcome: str
    correlation_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AuditLog:
    """In-memory audit sink suitable for tests and small research runs."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def events(self, *, category: str | None = None) -> list[AuditEvent]:
        selected = self._events if category is None else [
            event for event in self._events if event.category == category
        ]
        return [event.model_copy(deep=True) for event in selected]
