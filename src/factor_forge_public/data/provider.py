from __future__ import annotations

from typing import Protocol

from factor_forge_public.models import Candle


class MarketDataProvider(Protocol):
    """Boundary for historical or live candle sources.

    Implementations must return ordered, closed candles no later than
    ``as_of_ms``. Credentials and vendor-specific code stay outside the core.
    """

    def closed_candles(
        self,
        *,
        symbol: str,
        timeframe: str,
        as_of_ms: int,
        limit: int,
    ) -> list[Candle]: ...
