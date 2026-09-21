from __future__ import annotations

from factor_forge_public.models import Candle
from factor_forge_public.research import (
    evaluate_forward_returns,
    summarize_returns,
    volume_spike_events,
)


def synthetic_candles(count: int = 120) -> list[Candle]:
    candles: list[Candle] = []
    price = 100.0
    interval_ms = 15 * 60 * 1000
    for index in range(count):
        open_price = price
        close_price = open_price * (1.001 if index % 5 else 0.998)
        volume = 500.0 if index in {40, 80} else 100.0 + index
        candles.append(
            Candle(
                symbol="SYNTHETIC-USD",
                timeframe="15m",
                open_time_ms=index * interval_ms,
                close_time_ms=(index + 1) * interval_ms,
                open=open_price,
                high=max(open_price, close_price) * 1.001,
                low=min(open_price, close_price) * 0.999,
                close=close_price,
                volume=volume,
            )
        )
        price = close_price
    return candles


def main() -> None:
    candles = synthetic_candles()
    events = volume_spike_events(candles, lookback=20, multiplier=2.0)
    outcomes = evaluate_forward_returns(candles, events, horizons=(4, 12))
    for summary in summarize_returns(outcomes):
        print(summary.model_dump_json())


if __name__ == "__main__":
    main()
