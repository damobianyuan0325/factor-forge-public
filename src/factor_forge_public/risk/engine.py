from __future__ import annotations

from pydantic import BaseModel, Field

from factor_forge_public.execution.models import AccountSnapshot, OrderRequest


class RiskLimits(BaseModel):
    max_order_notional: float = Field(default=1_000.0, gt=0.0)
    max_total_notional: float = Field(default=5_000.0, gt=0.0)
    max_equity_fraction_per_order: float = Field(default=0.20, gt=0.0, le=1.0)
    min_equity: float = Field(default=100.0, ge=0.0)


class RiskDecision(BaseModel):
    allowed: bool
    reasons: list[str] = Field(default_factory=list)
    order_notional: float
    projected_total_notional: float


class RiskEngine:
    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits

    def check(self, order: OrderRequest, account: AccountSnapshot) -> RiskDecision:
        order_notional = order.quantity * (
            order.limit_price if order.limit_price is not None else order.reference_price
        )
        current_notional = sum(
            abs(position.quantity * position.average_price)
            for position in account.positions.values()
        )
        projected = current_notional + (0.0 if order.reduce_only else order_notional)
        reasons: list[str] = []

        if account.equity < self.limits.min_equity:
            reasons.append("equity_below_minimum")
        if order_notional > self.limits.max_order_notional:
            reasons.append("order_notional_above_limit")
        if order_notional > account.equity * self.limits.max_equity_fraction_per_order:
            reasons.append("order_equity_fraction_above_limit")
        if projected > self.limits.max_total_notional:
            reasons.append("projected_total_notional_above_limit")

        return RiskDecision(
            allowed=not reasons,
            reasons=reasons,
            order_notional=order_notional,
            projected_total_notional=projected,
        )
