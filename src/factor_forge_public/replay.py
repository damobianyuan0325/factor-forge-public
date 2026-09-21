from __future__ import annotations

from factor_forge_public.engine import SignalEngine
from factor_forge_public.models import Candle
from factor_forge_public.runtime import RunMode, SignalPlan, StrategyInput


def replay_closed_candles(
    engine: SignalEngine,
    *,
    strategy_id: str,
    candles: list[Candle],
    warmup_bars: int,
) -> list[SignalPlan]:
    """Advance one closed candle at a time without exposing future candles."""

    if warmup_bars < 1:
        raise ValueError("warmup_bars must be positive")
    plans: list[SignalPlan] = []
    for end in range(warmup_bars, len(candles) + 1):
        visible = candles[:end]
        latest = visible[-1]
        plans.append(
            engine.evaluate(
                strategy_id,
                StrategyInput(
                    symbol=latest.symbol,
                    timeframe=latest.timeframe,
                    candles=visible,
                    mode=RunMode.REPLAY,
                    as_of_ms=latest.close_time_ms,
                ),
            )
        )
    return plans
