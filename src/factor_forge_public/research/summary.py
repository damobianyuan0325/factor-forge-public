from __future__ import annotations

from collections import defaultdict
from statistics import mean, median

from pydantic import BaseModel

from factor_forge_public.research.forward_returns import ForwardReturn


class ReturnSummary(BaseModel):
    event_name: str
    horizon_bars: int
    count: int
    mean_return_pct: float
    median_return_pct: float
    positive_rate: float
    mean_favorable_excursion_pct: float
    mean_adverse_excursion_pct: float


def summarize_returns(rows: list[ForwardReturn]) -> list[ReturnSummary]:
    grouped: dict[tuple[str, int], list[ForwardReturn]] = defaultdict(list)
    for row in rows:
        grouped[(row.event_name, row.horizon_bars)].append(row)

    summaries: list[ReturnSummary] = []
    for (event_name, horizon), group in sorted(grouped.items()):
        returns = [row.return_pct for row in group]
        summaries.append(
            ReturnSummary(
                event_name=event_name,
                horizon_bars=horizon,
                count=len(group),
                mean_return_pct=mean(returns),
                median_return_pct=median(returns),
                positive_rate=sum(value > 0 for value in returns) / len(returns),
                mean_favorable_excursion_pct=mean(
                    row.max_favorable_excursion_pct for row in group
                ),
                mean_adverse_excursion_pct=mean(
                    row.max_adverse_excursion_pct for row in group
                ),
            )
        )
    return summaries
