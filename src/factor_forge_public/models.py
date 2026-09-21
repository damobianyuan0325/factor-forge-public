from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class Candle(BaseModel):
    """A normalized, timestamped OHLCV candle.

    Research functions should consume only candles whose close timestamp is not
    later than the simulated decision timestamp.
    """

    symbol: str
    timeframe: str
    open_time_ms: int
    close_time_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(default=0.0, ge=0.0)
    is_closed: bool = True

    @model_validator(mode="after")
    def validate_market_data(self) -> "Candle":
        if self.close_time_ms <= self.open_time_ms:
            raise ValueError("close_time_ms must be greater than open_time_ms")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close):
            raise ValueError("high/low must contain open and close")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        return self


class ResearchEvent(BaseModel):
    """A causal observation to evaluate, never an execution instruction."""

    event_id: str
    symbol: str
    timeframe: str
    name: str
    candle_index: int = Field(ge=0)
    observed_at_ms: int
    value: float | None = None
    features: dict[str, Any] = Field(default_factory=dict)
