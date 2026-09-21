from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class LifecycleStatus(StrEnum):
    CREATED = "created"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCEL_PENDING = "cancel_pending"
    CANCELED = "canceled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


TERMINAL_STATUSES = {
    LifecycleStatus.FILLED,
    LifecycleStatus.CANCELED,
    LifecycleStatus.REJECTED,
}

ALLOWED_TRANSITIONS = {
    LifecycleStatus.CREATED: {LifecycleStatus.SUBMITTED, LifecycleStatus.REJECTED},
    LifecycleStatus.SUBMITTED: {
        LifecycleStatus.ACKNOWLEDGED,
        LifecycleStatus.REJECTED,
        LifecycleStatus.UNKNOWN,
    },
    LifecycleStatus.ACKNOWLEDGED: {
        LifecycleStatus.PARTIALLY_FILLED,
        LifecycleStatus.FILLED,
        LifecycleStatus.CANCEL_PENDING,
        LifecycleStatus.CANCELED,
        LifecycleStatus.UNKNOWN,
    },
    LifecycleStatus.PARTIALLY_FILLED: {
        LifecycleStatus.FILLED,
        LifecycleStatus.CANCEL_PENDING,
        LifecycleStatus.CANCELED,
        LifecycleStatus.UNKNOWN,
    },
    LifecycleStatus.CANCEL_PENDING: {
        LifecycleStatus.CANCELED,
        LifecycleStatus.FILLED,
        LifecycleStatus.UNKNOWN,
    },
    LifecycleStatus.UNKNOWN: {
        LifecycleStatus.ACKNOWLEDGED,
        LifecycleStatus.PARTIALLY_FILLED,
        LifecycleStatus.FILLED,
        LifecycleStatus.CANCEL_PENDING,
        LifecycleStatus.CANCELED,
        LifecycleStatus.REJECTED,
    },
}


class OrderLifecycle(BaseModel):
    client_order_id: str
    status: LifecycleStatus = LifecycleStatus.CREATED
    filled_quantity: float = Field(default=0.0, ge=0.0)
    exchange_order_id: str | None = None
    revision: int = Field(default=0, ge=0)

    def transition(
        self,
        status: LifecycleStatus,
        *,
        filled_quantity: float | None = None,
        exchange_order_id: str | None = None,
    ) -> "OrderLifecycle":
        if status == self.status:
            return self.model_copy(deep=True)
        if self.status in TERMINAL_STATUSES:
            raise ValueError(f"terminal order cannot transition from {self.status}")
        if status not in ALLOWED_TRANSITIONS.get(self.status, set()):
            raise ValueError(f"illegal order transition: {self.status} -> {status}")
        next_filled = self.filled_quantity if filled_quantity is None else filled_quantity
        if next_filled < self.filled_quantity:
            raise ValueError("filled_quantity cannot decrease")
        return self.model_copy(
            update={
                "status": status,
                "filled_quantity": next_filled,
                "exchange_order_id": exchange_order_id or self.exchange_order_id,
                "revision": self.revision + 1,
            },
            deep=True,
        )
