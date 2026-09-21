from __future__ import annotations

import csv

import pytest

from factor_forge_public.data.csv_loader import load_candles_csv
from factor_forge_public.execution.lifecycle import LifecycleStatus, OrderLifecycle
from factor_forge_public.execution.preflight import JsonlPreflightLedger
from factor_forge_public.execution.retry import (
    ReconcileResult,
    WriteRecoveryAction,
    run_read_with_retry,
    write_timeout_action,
)
from factor_forge_public.research.performance import TradeReturn, summarize_trade_returns


def test_lifecycle_rejects_illegal_and_terminal_transitions() -> None:
    lifecycle = OrderLifecycle(client_order_id="test-1")
    lifecycle = lifecycle.transition(LifecycleStatus.SUBMITTED)
    lifecycle = lifecycle.transition(LifecycleStatus.UNKNOWN)
    lifecycle = lifecycle.transition(LifecycleStatus.FILLED, filled_quantity=2.0)
    assert lifecycle.revision == 3
    with pytest.raises(ValueError, match="terminal"):
        lifecycle.transition(LifecycleStatus.CANCELED)


def test_read_retry_and_write_reconcile_are_separate() -> None:
    attempts = 0
    sleeps: list[float] = []

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError
        return "ok"

    assert run_read_with_retry(operation, sleep=sleeps.append) == "ok"
    assert sleeps == [1.0, 3.0]
    assert write_timeout_action(ReconcileResult.FOUND) == WriteRecoveryAction.ACCEPT_RECONCILED
    assert write_timeout_action(ReconcileResult.NOT_FOUND) == WriteRecoveryAction.RETRY_ONCE
    assert write_timeout_action(ReconcileResult.INCONCLUSIVE) == WriteRecoveryAction.HOLD_FOR_REVIEW


def test_preflight_approval_is_bound_to_exact_payload(tmp_path) -> None:
    ledger = JsonlPreflightLedger(tmp_path / "preflight.jsonl")
    payload = {"symbol": "TEST", "quantity": 1.0}
    ledger.record("order-1", payload)
    ledger.approve("order-1", payload, approved_by="reviewer")
    assert ledger.require_approval("order-1", payload).approved
    with pytest.raises(ValueError, match="does not match"):
        ledger.require_approval("order-1", {**payload, "quantity": 2.0})


def test_csv_loader_rejects_future_candles(tmp_path) -> None:
    path = tmp_path / "candles.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "symbol", "timeframe", "open_time_ms", "close_time_ms",
            "open", "high", "low", "close", "volume",
        ])
        writer.writeheader()
        writer.writerow({
            "symbol": "TEST", "timeframe": "15m", "open_time_ms": 0,
            "close_time_ms": 900_000, "open": 10, "high": 12,
            "low": 9, "close": 11, "volume": 5,
        })
    assert len(load_candles_csv(path, available_at_ms=900_000)) == 1
    with pytest.raises(ValueError, match="unavailable"):
        load_candles_csv(path, available_at_ms=899_999)


def test_performance_summary_compounds_and_tracks_drawdown() -> None:
    result = summarize_trade_returns([
        TradeReturn(net_return=0.10),
        TradeReturn(net_return=-0.05),
        TradeReturn(net_return=-0.02),
        TradeReturn(net_return=0.03),
    ])
    assert result.trades == 4
    assert result.win_rate == 0.5
    assert result.max_consecutive_losses == 2
    assert result.max_drawdown == pytest.approx(0.069)
    assert result.profit_factor == pytest.approx(0.13 / 0.07)
