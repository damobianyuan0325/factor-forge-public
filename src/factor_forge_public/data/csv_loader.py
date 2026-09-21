from __future__ import annotations

import csv
from pathlib import Path

from factor_forge_public.models import Candle


REQUIRED_COLUMNS = {
    "symbol",
    "timeframe",
    "open_time_ms",
    "close_time_ms",
    "open",
    "high",
    "low",
    "close",
    "volume",
}


def load_candles_csv(path: str | Path, *, available_at_ms: int | None = None) -> list[Candle]:
    """Load normalized candles and optionally enforce point-in-time availability."""

    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing CSV columns: {sorted(missing)}")
        candles = [
            Candle(
                symbol=row["symbol"],
                timeframe=row["timeframe"],
                open_time_ms=int(row["open_time_ms"]),
                close_time_ms=int(row["close_time_ms"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
            for row in reader
        ]
    candles.sort(key=lambda candle: candle.open_time_ms)
    if len({candle.open_time_ms for candle in candles}) != len(candles):
        raise ValueError("duplicate candle open_time_ms")
    if available_at_ms is not None and any(candle.close_time_ms > available_at_ms for candle in candles):
        raise ValueError("CSV contains candles unavailable at the requested decision time")
    return candles
