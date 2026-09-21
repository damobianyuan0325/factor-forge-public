from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from factor_forge_public.models import Candle


class RunMode(StrEnum):
    REPLAY = "replay"
    PAPER = "paper"
    LIVE = "live"


class Decision(StrEnum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class StrategyInput(BaseModel):
    """Point-in-time input shared by replay, paper, and live evaluation."""

    symbol: str
    timeframe: str
    candles: list[Candle]
    mode: RunMode
    as_of_ms: int
    features: dict[str, float | int | str | bool | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def reject_future_or_open_candles(self) -> "StrategyInput":
        if not self.candles:
            raise ValueError("at least one candle is required")
        if any(not candle.is_closed for candle in self.candles):
            raise ValueError("strategy input may contain only closed candles")
        if any(candle.close_time_ms > self.as_of_ms for candle in self.candles):
            raise ValueError("strategy input contains future data")
        if any(candle.symbol != self.symbol for candle in self.candles):
            raise ValueError("all candles must match the input symbol")
        if any(candle.timeframe != self.timeframe for candle in self.candles):
            raise ValueError("all candles must match the input timeframe")
        return self


class SignalPlan(BaseModel):
    """Research signal output; an external risk layer decides whether to trade."""

    strategy_id: str
    strategy_version: str
    symbol: str
    timeframe: str
    decision: Decision
    observed_at_ms: int
    reference_price: float
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str
    diagnostics: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
