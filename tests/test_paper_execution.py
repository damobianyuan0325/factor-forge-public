from __future__ import annotations

from math import isclose

from factor_forge_public.brokers import PaperBroker
from factor_forge_public.execution.models import OrderRequest, OrderSide, OrderType
from factor_forge_public.risk import RiskEngine, RiskLimits


def test_paper_round_trip_accounts_for_fee_and_realized_pnl() -> None:
    broker = PaperBroker(initial_cash=10_000.0, fee_bps=4.0, slippage_bps=0.0)
    broker.submit(
        OrderRequest(
            client_order_id="open-long",
            symbol="TEST-USD",
            side=OrderSide.BUY,
            quantity=2.0,
            order_type=OrderType.MARKET,
            reference_price=100.0,
        ),
        timestamp_ms=1,
    )
    broker.submit(
        OrderRequest(
            client_order_id="close-long",
            symbol="TEST-USD",
            side=OrderSide.SELL,
            quantity=2.0,
            order_type=OrderType.MARKET,
            reference_price=110.0,
            reduce_only=True,
        ),
        timestamp_ms=2,
    )
    account = broker.account()
    expected_fees = 2.0 * 100.0 * 0.0004 + 2.0 * 110.0 * 0.0004
    assert account.positions["TEST-USD"].quantity == 0.0
    assert isclose(account.cash, 10_020.0 - expected_fees)
    assert isclose(account.fees_paid, expected_fees)


def test_risk_engine_rejects_oversized_order() -> None:
    broker = PaperBroker(initial_cash=1_000.0)
    order = OrderRequest(
        client_order_id="too-large",
        symbol="TEST-USD",
        side=OrderSide.BUY,
        quantity=10.0,
        order_type=OrderType.MARKET,
        reference_price=100.0,
    )
    decision = RiskEngine(
        RiskLimits(
            max_order_notional=500.0,
            max_total_notional=2_000.0,
            max_equity_fraction_per_order=0.20,
        )
    ).check(order, broker.account())
    assert not decision.allowed
    assert "order_notional_above_limit" in decision.reasons
    assert "order_equity_fraction_above_limit" in decision.reasons
