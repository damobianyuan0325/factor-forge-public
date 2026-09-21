from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from factor_forge_public.runtime import StrategyInput


class FactorSpec(BaseModel):
    factor_id: str
    version: str
    name: str
    description: str = ""
    required_inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


class FactorResult(BaseModel):
    factor_id: str
    version: str
    observed_at_ms: int
    values: dict[str, float | int | str | bool | None] = Field(default_factory=dict)


class Factor(ABC):
    spec: FactorSpec

    @abstractmethod
    def compute(self, strategy_input: StrategyInput) -> FactorResult:
        raise NotImplementedError
