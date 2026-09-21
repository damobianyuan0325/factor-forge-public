from __future__ import annotations

from threading import RLock

from factor_forge_public.models import Candle


class MarketState:
    """Thread-safe in-memory current and last-closed candle state."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._current: dict[tuple[str, str], Candle] = {}
        self._last_closed: dict[tuple[str, str], Candle] = {}

    def update(self, candle: Candle) -> Candle | None:
        key = (candle.symbol, candle.timeframe)
        with self._lock:
            previous = self._current.get(key)
            newly_closed: Candle | None = None
            if previous is not None and candle.open_time_ms > previous.open_time_ms:
                newly_closed = previous.model_copy(update={"is_closed": True})
                self._last_closed[key] = newly_closed
            self._current[key] = candle.model_copy(deep=True)
            if candle.is_closed:
                self._last_closed[key] = candle.model_copy(deep=True)
            return newly_closed

    def current(self, symbol: str, timeframe: str) -> Candle | None:
        with self._lock:
            candle = self._current.get((symbol, timeframe))
            return candle.model_copy(deep=True) if candle is not None else None

    def last_closed(self, symbol: str, timeframe: str) -> Candle | None:
        with self._lock:
            candle = self._last_closed.get((symbol, timeframe))
            return candle.model_copy(deep=True) if candle is not None else None

    def snapshot(self) -> dict[str, dict[str, dict[str, dict[str, object]]]]:
        with self._lock:
            result: dict[str, dict[str, dict[str, dict[str, object]]]] = {}
            for (symbol, timeframe), candle in self._current.items():
                slot = result.setdefault(symbol, {}).setdefault(timeframe, {})
                slot["current"] = candle.model_dump()
            for (symbol, timeframe), candle in self._last_closed.items():
                slot = result.setdefault(symbol, {}).setdefault(timeframe, {})
                slot["last_closed"] = candle.model_dump()
            return result
