from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel

from factor_forge_public.brokers.base import Broker
from factor_forge_public.execution.models import Fill, OrderRequest, OrderSide, OrderType
from factor_forge_public.risk.engine import RiskDecision, RiskEngine
from factor_forge_public.runtime import Decision, SignalPlan


class ExecutionResult(BaseModel):
    submitted: bool
    reason: str
    order: OrderRequest | None = None
    risk: RiskDecision | None = None
    fill: Fill | None = None


class ExecutionService:
    """Convert an approved signal into a broker request after risk checks."""

    def __init__(self, *, broker: Broker, risk_engine: RiskEngine) -> None:
        self.broker = broker
        self.risk_engine = risk_engine

    def submit_market_signal(
        self,
        plan: SignalPlan,
        *,
        quantity: float,
        timestamp_ms: int,
    ) -> ExecutionResult:
        if plan.decision == Decision.FLAT:
            return ExecutionResult(submitted=False, reason="flat_signal")

        order = OrderRequest(
            client_order_id=f"research-{uuid4().hex}",
            symbol=plan.symbol,
            side=OrderSide.BUY if plan.decision == Decision.LONG else OrderSide.SELL,
            quantity=quantity,
            order_type=OrderType.MARKET,
            reference_price=plan.reference_price,
        )
        risk = self.risk_engine.check(
            order,
            self.broker.account(marks={plan.symbol: plan.reference_price}),
        )
        if not risk.allowed:
            return ExecutionResult(
                submitted=False,
                reason="risk_rejected",
                order=order,
                risk=risk,
            )

        fill = self.broker.submit(order, timestamp_ms=timestamp_ms)
        return ExecutionResult(
            submitted=True,
            reason="submitted",
            order=order,
            risk=risk,
            fill=fill,
        )
