from __future__ import annotations

from abc import ABC, abstractmethod

from factor_forge_public.runtime import SignalPlan, StrategyInput


class Strategy(ABC):
    """One strategy contract for every runtime mode.

    Strategies must not branch on replay versus live mode. Mode-specific code
    belongs in data adapters, while strategy evaluation remains deterministic.
    """

    strategy_id: str
    version: str
    minimum_candles: int = 1

    @abstractmethod
    def evaluate(self, strategy_input: StrategyInput) -> SignalPlan:
        raise NotImplementedError


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        if not strategy.strategy_id:
            raise ValueError("strategy_id is required")
        if strategy.strategy_id in self._strategies:
            raise ValueError(f"strategy already registered: {strategy.strategy_id}")
        self._strategies[strategy.strategy_id] = strategy

    def get(self, strategy_id: str) -> Strategy:
        return self._strategies[strategy_id]

    def ids(self) -> list[str]:
        return sorted(self._strategies)
