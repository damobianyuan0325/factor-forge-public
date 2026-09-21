from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class CapitalProfile(BaseModel):
    initial_equity: float = Field(gt=0.0)
    equity_fraction_per_order: float = Field(gt=0.0, le=1.0)
    leverage: float = Field(default=1.0, gt=0.0)


class CostProfile(BaseModel):
    fee_bps_per_side: float = Field(default=4.0, ge=0.0)
    slippage_bps_per_side: float = Field(default=2.0, ge=0.0)


class GuardProfile(BaseModel):
    maximum_order_notional: float = Field(gt=0.0)
    maximum_total_notional: float = Field(gt=0.0)
    maximum_open_positions: int = Field(default=1, gt=0)


class RuntimeProfile(BaseModel):
    """Shared assumptions for replay, paper, and private live adapters."""

    profile_id: str
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    capital: CapitalProfile
    costs: CostProfile = Field(default_factory=CostProfile)
    guards: GuardProfile


def load_runtime_profile(path: str | Path) -> RuntimeProfile:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RuntimeProfile.model_validate(payload)
