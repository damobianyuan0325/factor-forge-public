from __future__ import annotations

from factor_forge_public.runtime import Decision, SignalPlan, StrategyInput
from factor_forge_public.strategy import Strategy


class MovingAverageCross(Strategy):
    """Minimal example strategy for demonstrating runtime parity."""

    strategy_id = "example.moving_average_cross"
    version = "v001"

    def __init__(self, *, fast_window: int = 5, slow_window: int = 20) -> None:
        if fast_window < 2 or slow_window <= fast_window:
            raise ValueError("require 2 <= fast_window < slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.minimum_candles = slow_window + 1

    def evaluate(self, strategy_input: StrategyInput) -> SignalPlan:
        closes = [candle.close for candle in strategy_input.candles]
        previous_fast = _mean(closes[-self.fast_window - 1 : -1])
        current_fast = _mean(closes[-self.fast_window :])
        previous_slow = _mean(closes[-self.slow_window - 1 : -1])
        current_slow = _mean(closes[-self.slow_window :])

        if previous_fast <= previous_slow and current_fast > current_slow:
            decision = Decision.LONG
            reason = "fast_average_crossed_above_slow_average"
        elif previous_fast >= previous_slow and current_fast < current_slow:
            decision = Decision.SHORT
            reason = "fast_average_crossed_below_slow_average"
        else:
            decision = Decision.FLAT
            reason = "no_new_cross"

        latest = strategy_input.candles[-1]
        separation = abs(current_fast - current_slow) / latest.close if latest.close else 0.0
        return SignalPlan(
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            symbol=strategy_input.symbol,
            timeframe=strategy_input.timeframe,
            decision=decision,
            observed_at_ms=latest.close_time_ms,
            reference_price=latest.close,
            confidence=min(separation * 100.0, 1.0),
            reason=reason,
            diagnostics={
                "fast_window": self.fast_window,
                "slow_window": self.slow_window,
                "fast_average": current_fast,
                "slow_average": current_slow,
            },
        )


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)
