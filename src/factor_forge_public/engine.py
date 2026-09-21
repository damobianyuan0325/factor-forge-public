from __future__ import annotations

from factor_forge_public.runtime import SignalPlan, StrategyInput
from factor_forge_public.strategy import StrategyRegistry


class SignalEngine:
    """Deterministic strategy entrypoint shared by every runtime adapter."""

    def __init__(self, registry: StrategyRegistry) -> None:
        self.registry = registry

    def evaluate(self, strategy_id: str, strategy_input: StrategyInput) -> SignalPlan:
        strategy = self.registry.get(strategy_id)
        if len(strategy_input.candles) < strategy.minimum_candles:
            raise ValueError(
                f"{strategy_id} requires at least {strategy.minimum_candles} candles"
            )
        return strategy.evaluate(strategy_input)
