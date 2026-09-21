from __future__ import annotations

import pytest

from factor_forge_public.engine import SignalEngine
from factor_forge_public.live import evaluate_closed_snapshot
from factor_forge_public.models import Candle
from factor_forge_public.replay import replay_closed_candles
from factor_forge_public.runtime import RunMode, StrategyInput
from factor_forge_public.strategies import MovingAverageCross
from factor_forge_public.strategy import StrategyRegistry


def make_candles(count: int = 32) -> list[Candle]:
    candles: list[Candle] = []
    for index in range(count):
        close = 100.0 - index if index < 22 else 78.0 + (index - 21) * 4.0
        candles.append(
            Candle(
                symbol="TEST-USD",
                timeframe="15m",
                open_time_ms=index * 900_000,
                close_time_ms=(index + 1) * 900_000,
                open=close - 0.5,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=100.0,
            )
        )
    return candles


def make_engine() -> SignalEngine:
    registry = StrategyRegistry()
    registry.register(MovingAverageCross(fast_window=3, slow_window=8))
    return SignalEngine(registry)


def test_replay_and_live_use_the_same_strategy_result() -> None:
    candles = make_candles()
    engine = make_engine()
    replay_plan = replay_closed_candles(
        engine,
        strategy_id="example.moving_average_cross",
        candles=candles,
        warmup_bars=9,
    )[-1]
    live_plan = evaluate_closed_snapshot(
        engine,
        strategy_id="example.moving_average_cross",
        candles=candles,
        mode=RunMode.LIVE,
    )
    assert replay_plan == live_plan


def test_strategy_input_rejects_future_candle() -> None:
    candles = make_candles(9)
    with pytest.raises(ValueError, match="future data"):
        StrategyInput(
            symbol="TEST-USD",
            timeframe="15m",
            candles=candles,
            mode=RunMode.REPLAY,
            as_of_ms=candles[-1].close_time_ms - 1,
        )


def test_strategy_input_rejects_open_candle() -> None:
    candles = make_candles(9)
    candles[-1] = candles[-1].model_copy(update={"is_closed": False})
    with pytest.raises(ValueError, match="only closed candles"):
        StrategyInput(
            symbol="TEST-USD",
            timeframe="15m",
            candles=candles,
            mode=RunMode.LIVE,
            as_of_ms=candles[-1].close_time_ms,
        )
