from __future__ import annotations

import asyncio

from factor_forge_public.data import (
    HealthStatus,
    PollingJob,
    PollingScheduler,
    check_candle_health,
)
from factor_forge_public.factors import CandleShapeFactor, FactorRegistry
from factor_forge_public.models import Candle
from factor_forge_public.realtime import EventBus, MarketEvent, MarketEventType
from factor_forge_public.research import expanding_walk_forward_splits, stress_forward_returns
from factor_forge_public.research.forward_returns import ForwardReturn


def candles(count: int = 10) -> list[Candle]:
    return [
        Candle(
            symbol="TEST-USD",
            timeframe="15m",
            open_time_ms=index * 900_000,
            close_time_ms=(index + 1) * 900_000,
            open=100.0,
            high=102.0,
            low=99.0,
            close=101.0,
            volume=100.0,
        )
        for index in range(count)
    ]


def test_data_health_detects_contiguous_closed_history() -> None:
    rows = candles()
    health = check_candle_health(
        rows,
        timeframe="15m",
        as_of_ms=rows[-1].close_time_ms,
        minimum_bars=10,
    )
    assert health.status == HealthStatus.PASS
    assert health.gap_count == 0


def test_polling_scheduler_is_deterministic_with_explicit_clock() -> None:
    job = PollingJob(name="candles", resource="closed_candles", interval_seconds=60)
    scheduler = PollingScheduler([job])
    assert scheduler.due_jobs(now=100.0) == [job]
    scheduler.mark_ran(job, now=100.0)
    assert scheduler.due_jobs(now=159.9) == []
    assert scheduler.due_jobs(now=160.0) == [job]


def test_factor_registry_exposes_sanitized_catalog_and_values() -> None:
    registry = FactorRegistry()
    factor = CandleShapeFactor()
    registry.register(factor)
    assert registry.catalog()[0]["factor_id"] == "candle_shape.latest"


def test_event_bus_isolates_handler_failures() -> None:
    received: list[str] = []

    def broken(_: MarketEvent) -> None:
        raise RuntimeError("expected test failure")

    def healthy(event: MarketEvent) -> None:
        received.append(event.event_type.value)

    bus = EventBus()
    bus.subscribe(broken)
    bus.subscribe(healthy)
    asyncio.run(
        bus.publish(
            MarketEvent(
                event_type=MarketEventType.CANDLE_CLOSED,
                symbol="TEST-USD",
                timeframe="15m",
                timestamp_ms=1,
            )
        )
    )
    assert received == ["candle_closed"]
    assert len(bus.failures) == 1


def test_walk_forward_and_cost_stress_are_strictly_out_of_sample() -> None:
    splits = expanding_walk_forward_splits(
        100,
        minimum_train_size=40,
        test_size=20,
    )
    assert all(split.train_end == split.test_start for split in splits)
    assert all(split.test_end <= 100 for split in splits)

    outcomes = [
        ForwardReturn(
            event_id=f"event-{index}",
            event_name="example",
            horizon_bars=4,
            entry_price=100.0,
            exit_price=100.0 * (1.0 + value),
            return_pct=value,
            max_favorable_excursion_pct=max(value, 0.0),
            max_adverse_excursion_pct=min(value, 0.0),
        )
        for index, value in enumerate([0.03, 0.02, 0.01, -0.01])
    ]
    stressed = stress_forward_returns(
        outcomes,
        round_trip_cost_bps=10.0,
        remove_best_trades=1,
    )
    assert stressed.count == 3
    assert stressed.removed_best_trades == 1
