from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MarketEventType(StrEnum):
    CANDLE_UPDATE = "candle_update"
    CANDLE_CLOSED = "candle_closed"
    MARKET_SNAPSHOT = "market_snapshot"
    DATA_HEALTH = "data_health"


class MarketEvent(BaseModel):
    event_type: MarketEventType
    symbol: str
    timestamp_ms: int
    timeframe: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
