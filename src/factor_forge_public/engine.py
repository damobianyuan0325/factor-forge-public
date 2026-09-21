from __future__ import annotations

from factor_forge_public.factors.registry import FactorRegistry
from factor_forge_public.runtime import SignalPlan, StrategyInput
from factor_forge_public.strategy import StrategyRegistry


class SignalEngine:
    """Deterministic strategy entrypoint shared by every runtime adapter."""

    def __init__(
        self,
        registry: StrategyRegistry,
        *,
        factors: FactorRegistry | None = None,
    ) -> None:
        self.registry = registry
        self.factors = factors or FactorRegistry()

    def evaluate(self, strategy_id: str, strategy_input: StrategyInput) -> SignalPlan:
        strategy = self.registry.get(strategy_id)
        if len(strategy_input.candles) < strategy.minimum_candles:
            raise ValueError(
                f"{strategy_id} requires at least {strategy.minimum_candles} candles"
            )
        features = dict(strategy_input.features)
        for factor in self.factors.all():
            result = factor.compute(strategy_input)
            for key, value in result.values.items():
                features[f"{result.factor_id}.{key}"] = value
        enriched = strategy_input.model_copy(update={"features": features})
        return strategy.evaluate(enriched)
