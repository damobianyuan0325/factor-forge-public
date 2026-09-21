from __future__ import annotations

from pydantic import BaseModel, Field


class TradeReturn(BaseModel):
    net_return: float


class PerformanceSummary(BaseModel):
    trades: int = Field(ge=0)
    total_return: float
    max_drawdown: float = Field(ge=0.0)
    win_rate: float = Field(ge=0.0, le=1.0)
    profit_factor: float | None
    average_trade: float
    max_consecutive_losses: int = Field(ge=0)


def summarize_trade_returns(trades: list[TradeReturn], *, initial_equity: float = 1.0) -> PerformanceSummary:
    if initial_equity <= 0:
        raise ValueError("initial_equity must be positive")
    equity = initial_equity
    peak = equity
    max_drawdown = 0.0
    gross_profit = 0.0
    gross_loss = 0.0
    losses = 0
    max_losses = 0
    wins = 0
    for trade in trades:
        equity *= 1.0 + trade.net_return
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak)
        if trade.net_return > 0:
            wins += 1
            gross_profit += trade.net_return
            losses = 0
        elif trade.net_return < 0:
            gross_loss += abs(trade.net_return)
            losses += 1
            max_losses = max(max_losses, losses)
        else:
            losses = 0
    count = len(trades)
    return PerformanceSummary(
        trades=count,
        total_return=equity / initial_equity - 1.0,
        max_drawdown=max_drawdown,
        win_rate=wins / count if count else 0.0,
        profit_factor=gross_profit / gross_loss if gross_loss else None,
        average_trade=sum(trade.net_return for trade in trades) / count if count else 0.0,
        max_consecutive_losses=max_losses,
    )
