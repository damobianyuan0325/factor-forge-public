from __future__ import annotations

from pydantic import BaseModel, Field


class PortfolioLimits(BaseModel):
    maximum_open_positions: int = Field(default=1, gt=0)
    maximum_daily_loss_fraction: float = Field(default=0.03, gt=0.0, le=1.0)
    maximum_consecutive_losses: int = Field(default=3, gt=0)


class PortfolioState(BaseModel):
    session_start_equity: float = Field(gt=0.0)
    current_equity: float
    open_positions: int = Field(default=0, ge=0)
    consecutive_losses: int = Field(default=0, ge=0)


class PortfolioDecision(BaseModel):
    allowed: bool
    reasons: list[str] = Field(default_factory=list)
    daily_loss_fraction: float = Field(ge=0.0)


class PortfolioRiskGate:
    """Session-level guard applied before per-order risk checks."""

    def __init__(self, limits: PortfolioLimits) -> None:
        self.limits = limits

    def check(self, state: PortfolioState) -> PortfolioDecision:
        loss = max(0.0, (state.session_start_equity - state.current_equity) / state.session_start_equity)
        reasons: list[str] = []
        if state.open_positions >= self.limits.maximum_open_positions:
            reasons.append("maximum_open_positions_reached")
        if loss >= self.limits.maximum_daily_loss_fraction:
            reasons.append("maximum_daily_loss_reached")
        if state.consecutive_losses >= self.limits.maximum_consecutive_losses:
            reasons.append("maximum_consecutive_losses_reached")
        return PortfolioDecision(allowed=not reasons, reasons=reasons, daily_loss_fraction=loss)
