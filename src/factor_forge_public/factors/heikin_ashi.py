from __future__ import annotations

from factor_forge_public.models import Candle


def heikin_ashi(candles: list[Candle]) -> list[Candle]:
    """Transform regular candles into Heikin-Ashi candles causally.

    Each output uses only the current raw candle and the previous transformed
    candle. Raw exchange candles should remain the source of truth.
    """

    transformed: list[Candle] = []
    previous_open: float | None = None
    previous_close: float | None = None

    for candle in candles:
        ha_close = (candle.open + candle.high + candle.low + candle.close) / 4.0
        if previous_open is None or previous_close is None:
            ha_open = (candle.open + candle.close) / 2.0
        else:
            ha_open = (previous_open + previous_close) / 2.0

        transformed.append(
            candle.model_copy(
                update={
                    "open": ha_open,
                    "high": max(candle.high, ha_open, ha_close),
                    "low": min(candle.low, ha_open, ha_close),
                    "close": ha_close,
                }
            )
        )
        previous_open = ha_open
        previous_close = ha_close

    return transformed
