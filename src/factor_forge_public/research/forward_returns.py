from __future__ import annotations

from pydantic import BaseModel, Field

from factor_forge_public.models import Candle, ResearchEvent


class ForwardReturn(BaseModel):
    event_id: str
    event_name: str
    horizon_bars: int = Field(gt=0)
    entry_price: float
    exit_price: float
    return_pct: float
    max_favorable_excursion_pct: float
    max_adverse_excursion_pct: float


def evaluate_forward_returns(
    candles: list[Candle],
    events: list[ResearchEvent],
    *,
    horizons: tuple[int, ...] = (4, 12, 24),
) -> list[ForwardReturn]:
    """Evaluate outcomes after events without feeding outcomes into detection.

    This function is an offline labeling step. Event detectors must run first
    and must not receive any values produced here.
    """

    if not horizons or any(horizon <= 0 for horizon in horizons):
        raise ValueError("horizons must contain positive integers")

    results: list[ForwardReturn] = []
    for event in events:
        index = event.candle_index
        if index >= len(candles):
            continue
        entry = candles[index].close
        if entry == 0:
            continue

        for horizon in horizons:
            exit_index = index + horizon
            if exit_index >= len(candles):
                continue
            future_window = candles[index + 1 : exit_index + 1]
            results.append(
                ForwardReturn(
                    event_id=event.event_id,
                    event_name=event.name,
                    horizon_bars=horizon,
                    entry_price=entry,
                    exit_price=candles[exit_index].close,
                    return_pct=(candles[exit_index].close - entry) / entry,
                    max_favorable_excursion_pct=(max(item.high for item in future_window) - entry) / entry,
                    max_adverse_excursion_pct=(min(item.low for item in future_window) - entry) / entry,
                )
            )
    return results
