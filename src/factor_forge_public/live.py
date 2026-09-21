from __future__ import annotations

from factor_forge_public.engine import SignalEngine
from factor_forge_public.models import Candle
from factor_forge_public.runtime import RunMode, SignalPlan, StrategyInput


def evaluate_closed_snapshot(
    engine: SignalEngine,
    *,
    strategy_id: str,
    candles: list[Candle],
    mode: RunMode = RunMode.LIVE,
) -> SignalPlan:
    """Evaluate the latest closed snapshot through the shared signal engine.

    This adapter creates signals only. It contains no exchange or order code.
    """

    if mode not in {RunMode.LIVE, RunMode.PAPER}:
        raise ValueError("live adapter supports only live or paper mode")
    if not candles:
        raise ValueError("at least one candle is required")
    latest = candles[-1]
    return engine.evaluate(
        strategy_id,
        StrategyInput(
            symbol=latest.symbol,
            timeframe=latest.timeframe,
            candles=candles,
            mode=mode,
            as_of_ms=latest.close_time_ms,
        ),
    )
