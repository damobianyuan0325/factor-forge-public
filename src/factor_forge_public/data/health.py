from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field

from factor_forge_public.models import Candle


class HealthStatus(StrEnum):
    PASS = "pass"
    CAUTION = "caution"
    BLOCK = "block"


class DataHealth(BaseModel):
    status: HealthStatus
    issues: list[str] = Field(default_factory=list)
    expected_interval_ms: int
    latest_close_time_ms: int | None = None
    gap_count: int = 0


def check_candle_health(
    candles: list[Candle],
    *,
    timeframe: str,
    as_of_ms: int,
    minimum_bars: int,
    maximum_staleness_intervals: int = 2,
) -> DataHealth:
    interval = timeframe_to_ms(timeframe)
    issues: list[str] = []
    if len(candles) < minimum_bars:
        issues.append("insufficient_history")
    if any(not candle.is_closed for candle in candles):
        issues.append("contains_open_candle")
    if any(candle.close_time_ms > as_of_ms for candle in candles):
        issues.append("contains_future_candle")

    ordered = sorted(candles, key=lambda candle: candle.open_time_ms)
    gaps = sum(
        current.open_time_ms - previous.open_time_ms != interval
        for previous, current in zip(ordered, ordered[1:])
    )
    if gaps:
        issues.append("non_contiguous_history")

    latest = ordered[-1].close_time_ms if ordered else None
    if latest is None:
        issues.append("no_candles")
    elif as_of_ms - latest > interval * maximum_staleness_intervals:
        issues.append("stale_latest_candle")

    blocking = {"contains_open_candle", "contains_future_candle", "no_candles"}
    if blocking.intersection(issues):
        status = HealthStatus.BLOCK
    elif issues:
        status = HealthStatus.CAUTION
    else:
        status = HealthStatus.PASS
    return DataHealth(
        status=status,
        issues=issues,
        expected_interval_ms=interval,
        latest_close_time_ms=latest,
        gap_count=gaps,
    )


def timeframe_to_ms(timeframe: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*)(m|min|h|hour|d|day)", timeframe.strip().lower())
    if match is None:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    value = int(match.group(1))
    unit = match.group(2)
    multiplier = 60_000 if unit in {"m", "min"} else 3_600_000 if unit in {"h", "hour"} else 86_400_000
    return value * multiplier
