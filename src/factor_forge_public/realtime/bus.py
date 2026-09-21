from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable

from pydantic import BaseModel

from factor_forge_public.realtime.events import MarketEvent

EventHandler = Callable[[MarketEvent], Awaitable[None] | None]


class HandlerFailure(BaseModel):
    handler_name: str
    event_type: str
    error_type: str
    message: str


class EventBus:
    """In-process async event bus that isolates subscriber failures."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []
        self.failures: list[HandlerFailure] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def publish(self, event: MarketEvent) -> None:
        for handler in list(self._handlers):
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                self.failures.append(
                    HandlerFailure(
                        handler_name=getattr(handler, "__name__", type(handler).__name__),
                        event_type=event.event_type.value,
                        error_type=type(exc).__name__,
                        message=str(exc)[:240],
                    )
                )
