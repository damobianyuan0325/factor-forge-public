from __future__ import annotations

from factor_forge_public.models import Candle, ResearchEvent


def volume_spike_events(
    candles: list[Candle],
    *,
    lookback: int = 20,
    multiplier: float = 2.0,
) -> list[ResearchEvent]:
    """Find closed candles whose volume exceeds a trailing mean."""

    _validate_window(lookback, multiplier)
    events: list[ResearchEvent] = []
    for index in range(lookback, len(candles)):
        candle = candles[index]
        if not candle.is_closed:
            continue
        trailing = candles[index - lookback : index]
        average = sum(item.volume for item in trailing) / lookback
        if average <= 0:
            continue
        ratio = candle.volume / average
        if ratio >= multiplier:
            events.append(
                _event(
                    candle,
                    index=index,
                    name="volume_spike",
                    value=ratio,
                    features={"trailing_average_volume": average, "volume_ratio": ratio},
                )
            )
    return events


def wide_range_events(
    candles: list[Candle],
    *,
    lookback: int = 20,
    multiplier: float = 1.5,
) -> list[ResearchEvent]:
    """Find closed candles whose relative range exceeds a trailing mean."""

    _validate_window(lookback, multiplier)
    events: list[ResearchEvent] = []
    for index in range(lookback, len(candles)):
        candle = candles[index]
        if not candle.is_closed or candle.close == 0:
            continue
        trailing_ranges = [
            (item.high - item.low) / item.close
            for item in candles[index - lookback : index]
            if item.close != 0
        ]
        if len(trailing_ranges) != lookback:
            continue
        average = sum(trailing_ranges) / lookback
        current = (candle.high - candle.low) / candle.close
        if average > 0 and current >= average * multiplier:
            events.append(
                _event(
                    candle,
                    index=index,
                    name="wide_range",
                    value=current,
                    features={"trailing_average_range": average, "range_ratio": current / average},
                )
            )
    return events


def _event(
    candle: Candle,
    *,
    index: int,
    name: str,
    value: float,
    features: dict[str, float],
) -> ResearchEvent:
    return ResearchEvent(
        event_id=f"{candle.symbol}:{candle.timeframe}:{name}:{candle.close_time_ms}",
        symbol=candle.symbol,
        timeframe=candle.timeframe,
        name=name,
        candle_index=index,
        observed_at_ms=candle.close_time_ms,
        value=value,
        features=features,
    )


def _validate_window(lookback: int, multiplier: float) -> None:
    if lookback < 2:
        raise ValueError("lookback must be at least 2")
    if multiplier <= 0:
        raise ValueError("multiplier must be positive")
