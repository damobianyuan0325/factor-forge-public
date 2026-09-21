from __future__ import annotations

from factor_forge_public.factors.base import Factor


class FactorRegistry:
    def __init__(self) -> None:
        self._factors: dict[str, Factor] = {}

    def register(self, factor: Factor) -> None:
        factor_id = factor.spec.factor_id
        if factor_id in self._factors:
            raise ValueError(f"factor already registered: {factor_id}")
        self._factors[factor_id] = factor

    def get(self, factor_id: str) -> Factor:
        return self._factors[factor_id]

    def all(self) -> list[Factor]:
        return list(self._factors.values())

    def catalog(self) -> list[dict[str, object]]:
        return [
            factor.spec.model_dump()
            for factor in sorted(self._factors.values(), key=lambda item: item.spec.factor_id)
        ]
