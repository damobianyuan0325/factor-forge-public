from __future__ import annotations

from abc import ABC, abstractmethod

from factor_forge_public.execution.models import AccountSnapshot, Fill, OrderRequest


class Broker(ABC):
    """Execution boundary implemented by paper or external live adapters."""

    @abstractmethod
    def submit(self, order: OrderRequest, *, timestamp_ms: int) -> Fill | None:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, client_order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def account(self, *, marks: dict[str, float] | None = None) -> AccountSnapshot:
        raise NotImplementedError
