from __future__ import annotations

from typing import Any, Protocol


class Notifier(Protocol):
    def send(self, event: dict[str, Any]) -> bool: ...


class NullNotifier:
    def send(self, event: dict[str, Any]) -> bool:
        return True

class MemoryNotifier:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def send(self, event: dict[str, Any]) -> bool:
        self.events.append(dict(event))
        return True
