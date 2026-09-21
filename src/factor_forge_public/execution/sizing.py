from __future__ import annotations

from decimal import Decimal, ROUND_DOWN

from pydantic import BaseModel, Field


class InstrumentRules(BaseModel):
    quantity_step: float = Field(gt=0.0)
    minimum_quantity: float = Field(gt=0.0)
    minimum_notional: float = Field(default=0.0, ge=0.0)


class PositionSize(BaseModel):
    quantity: float
    notional: float
    accepted: bool
    reason: str


def size_by_equity_fraction(
    *,
    equity: float,
    price: float,
    equity_fraction: float,
    leverage: float,
    rules: InstrumentRules,
) -> PositionSize:
    if equity <= 0 or price <= 0 or not 0 < equity_fraction <= 1 or leverage <= 0:
        raise ValueError("invalid sizing inputs")
    target_notional = equity * equity_fraction * leverage
    raw_quantity = target_notional / price
    step = Decimal(str(rules.quantity_step))
    quantity = float((Decimal(str(raw_quantity)) / step).to_integral_value(rounding=ROUND_DOWN) * step)
    notional = quantity * price

    if quantity < rules.minimum_quantity:
        return PositionSize(quantity=quantity, notional=notional, accepted=False, reason="below_minimum_quantity")
    if notional < rules.minimum_notional:
        return PositionSize(quantity=quantity, notional=notional, accepted=False, reason="below_minimum_notional")
    return PositionSize(quantity=quantity, notional=notional, accepted=True, reason="accepted")
