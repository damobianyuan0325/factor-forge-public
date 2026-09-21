from __future__ import annotations

from statistics import mean

from pydantic import BaseModel

from factor_forge_public.research.forward_returns import ForwardReturn


class StressResult(BaseModel):
    count: int
    round_trip_cost_bps: float
    removed_best_trades: int
    mean_net_return_pct: float | None
    positive_rate: float | None


def stress_forward_returns(
    rows: list[ForwardReturn],
    *,
    round_trip_cost_bps: float,
    remove_best_trades: int = 0,
) -> StressResult:
    """Apply extra costs and remove the strongest outcomes as a fragility check."""

    if round_trip_cost_bps < 0 or remove_best_trades < 0:
        raise ValueError("stress parameters cannot be negative")
    net = sorted(
        (row.return_pct - round_trip_cost_bps / 10_000.0 for row in rows),
        reverse=True,
    )
    remaining = net[min(remove_best_trades, len(net)) :]
    return StressResult(
        count=len(remaining),
        round_trip_cost_bps=round_trip_cost_bps,
        removed_best_trades=min(remove_best_trades, len(net)),
        mean_net_return_pct=mean(remaining) if remaining else None,
        positive_rate=(sum(value > 0 for value in remaining) / len(remaining)) if remaining else None,
    )
