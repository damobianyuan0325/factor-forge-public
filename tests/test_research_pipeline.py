from __future__ import annotations

from factor_forge_public.factors import heikin_ashi
from factor_forge_public.models import Candle
from factor_forge_public.research import evaluate_forward_returns, volume_spike_events


def make_candles(count: int = 40) -> list[Candle]:
    candles: list[Candle] = []
    for index in range(count):
        price = 100.0 + index
        candles.append(
            Candle(
                symbol="TEST-USD",
                timeframe="15m",
                open_time_ms=index * 900_000,
                close_time_ms=(index + 1) * 900_000,
                open=price,
                high=price + 2.0,
                low=price - 1.0,
                close=price + 1.0,
                volume=1_000.0 if index == 25 else 100.0,
            )
        )
    return candles


def test_heikin_ashi_uses_only_current_and_previous_values() -> None:
    candles = make_candles(3)
    transformed = heikin_ashi(candles)
    assert transformed[0].close == sum(
        [candles[0].open, candles[0].high, candles[0].low, candles[0].close]
    ) / 4.0
    assert transformed[1].open == (transformed[0].open + transformed[0].close) / 2.0


def test_event_detection_is_independent_of_future_candles() -> None:
    candles = make_candles()
    prefix_events = volume_spike_events(candles[:30], lookback=20, multiplier=2.0)
    full_events = volume_spike_events(candles, lookback=20, multiplier=2.0)
    assert [event.event_id for event in prefix_events] == [
        event.event_id for event in full_events if event.candle_index < 30
    ]


def test_forward_returns_are_computed_only_after_detection() -> None:
    candles = make_candles()
    events = volume_spike_events(candles, lookback=20, multiplier=2.0)
    outcomes = evaluate_forward_returns(candles, events, horizons=(4,))
    assert len(events) == 1
    assert len(outcomes) == 1
    assert outcomes[0].event_id == events[0].event_id
