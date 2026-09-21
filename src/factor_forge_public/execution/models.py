from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(StrEnum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


class OrderRequest(BaseModel):
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: float = Field(gt=0.0)
    order_type: OrderType
    reference_price: float = Field(gt=0.0)
    limit_price: float | None = Field(default=None, gt=0.0)
    reduce_only: bool = False

    @model_validator(mode="after")
    def require_limit_price(self) -> "OrderRequest":
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price is required for limit orders")
        return self


class Fill(BaseModel):
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: float = Field(gt=0.0)
    price: float = Field(gt=0.0)
    fee: float = Field(ge=0.0)
    filled_at_ms: int


class Position(BaseModel):
    symbol: str
    quantity: float = 0.0
    average_price: float = 0.0
    realized_pnl: float = 0.0


class AccountSnapshot(BaseModel):
    cash: float
    equity: float
    fees_paid: float = 0.0
    positions: dict[str, Position] = Field(default_factory=dict)
