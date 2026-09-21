from __future__ import annotations

from factor_forge_public.brokers import PaperBroker
from factor_forge_public.execution import OrderRequest, OrderSide, OrderType
from factor_forge_public.execution.idempotency import deterministic_client_order_id
from factor_forge_public.models import Candle
from factor_forge_public.monitoring import AuditEvent, SQLiteAuditLog
from factor_forge_public.risk import PortfolioLimits, PortfolioRiskGate, PortfolioState
from factor_forge_public.runtime import Decision, SignalPlan


def _plan() -> SignalPlan:
    return SignalPlan(
        strategy_id="example",
        strategy_version="1",
        symbol="TEST-USD",
        timeframe="15m",
        decision=Decision.LONG,
        observed_at_ms=900_000,
        reference_price=100.0,
        reason="test",
    )


def test_client_order_id_is_deterministic_and_decision_bound() -> None:
    first = deterministic_client_order_id(_plan())
    second = deterministic_client_order_id(_plan())
    changed = deterministic_client_order_id(_plan().model_copy(update={"observed_at_ms": 1_800_000}))
    assert first == second
    assert first != changed


def test_limit_order_cannot_fill_from_same_or_older_candle() -> None:
    broker = PaperBroker(slippage_bps=0.0)
    broker.submit(
        OrderRequest(
            client_order_id="limit-1",
            symbol="TEST-USD",
            side=OrderSide.BUY,
            quantity=1.0,
            order_type=OrderType.LIMIT,
            reference_price=100.0,
            limit_price=99.0,
        ),
        timestamp_ms=900_000,
    )
    same_candle = Candle(
        symbol="TEST-USD", timeframe="15m", open_time_ms=0, close_time_ms=900_000,
        open=100.0, high=101.0, low=98.0, close=100.0,
    )
    later_candle = same_candle.model_copy(
        update={"open_time_ms": 900_000, "close_time_ms": 1_800_000}
    )
    assert broker.on_candle(same_candle) == []
    assert len(broker.on_candle(later_candle)) == 1


def test_portfolio_gate_combines_session_limits() -> None:
    decision = PortfolioRiskGate(
        PortfolioLimits(
            maximum_open_positions=2,
            maximum_daily_loss_fraction=0.03,
            maximum_consecutive_losses=3,
        )
    ).check(
        PortfolioState(
            session_start_equity=1_000.0,
            current_equity=960.0,
            open_positions=2,
            consecutive_losses=3,
        )
    )
    assert not decision.allowed
    assert len(decision.reasons) == 3


def test_portfolio_gate_accepts_bankruptcy_state_for_rejection() -> None:
    decision = PortfolioRiskGate(PortfolioLimits()).check(
        PortfolioState(session_start_equity=1_000.0, current_equity=-10.0)
    )
    assert not decision.allowed
    assert "maximum_daily_loss_reached" in decision.reasons


def test_sqlite_audit_log_round_trip(tmp_path) -> None:
    log = SQLiteAuditLog(tmp_path / "audit.sqlite3")
    event = AuditEvent(
        timestamp_ms=123,
        category="execution",
        action="preflight",
        outcome="allowed",
        correlation_id="order-1",
        details={"quantity": 1.0},
    )
    log.append(event)
    assert log.events(category="execution") == [event]
