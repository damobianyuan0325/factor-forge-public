from __future__ import annotations

from factor_forge_public.factors.base import Factor, FactorResult, FactorSpec
from factor_forge_public.runtime import StrategyInput


class CandleShapeFactor(Factor):
    spec = FactorSpec(
        factor_id="candle_shape.latest",
        version="v001",
        name="Latest closed candle shape",
        description="Body, wick, range, direction, and close-position features.",
        required_inputs=("closed_ohlcv",),
        outputs=(
            "direction",
            "body_ratio",
            "upper_wick_ratio",
            "lower_wick_ratio",
            "close_position",
            "range_pct",
        ),
        tags=("causal", "price_action", "replay_live_safe"),
    )

    def compute(self, strategy_input: StrategyInput) -> FactorResult:
        candle = strategy_input.candles[-1]
        full_range = candle.high - candle.low
        body = abs(candle.close - candle.open)
        upper_wick = candle.high - max(candle.open, candle.close)
        lower_wick = min(candle.open, candle.close) - candle.low
        direction = "bull" if candle.close > candle.open else "bear" if candle.close < candle.open else "doji"
        values: dict[str, float | str] = {
            "direction": direction,
            "body_ratio": body / full_range if full_range else 0.0,
            "upper_wick_ratio": upper_wick / full_range if full_range else 0.0,
            "lower_wick_ratio": lower_wick / full_range if full_range else 0.0,
            "close_position": (candle.close - candle.low) / full_range if full_range else 0.5,
            "range_pct": full_range / candle.close if candle.close else 0.0,
        }
        return FactorResult(
            factor_id=self.spec.factor_id,
            version=self.spec.version,
            observed_at_ms=candle.close_time_ms,
            values=values,
        )
