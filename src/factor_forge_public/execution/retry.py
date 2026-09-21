from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    delays_seconds: Sequence[float] = (1.0, 3.0, 8.0)


def run_read_with_retry(
    operation: Callable[[], T],
    *,
    policy: RetryPolicy = RetryPolicy(),
    retryable: Callable[[Exception], bool] = lambda exc: isinstance(exc, TimeoutError),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Retry an idempotent read. Write operations must not use this helper."""

    for delay in (*policy.delays_seconds, None):
        try:
            return operation()
        except Exception as exc:
            if delay is None or not retryable(exc):
                raise
            sleep(delay)
    raise RuntimeError("unreachable")


class ReconcileResult(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    INCONCLUSIVE = "inconclusive"


class WriteRecoveryAction(StrEnum):
    ACCEPT_RECONCILED = "accept_reconciled"
    RETRY_ONCE = "retry_once"
    HOLD_FOR_REVIEW = "hold_for_review"


def write_timeout_action(
    result: ReconcileResult,
    *,
    retry_already_used: bool = False,
) -> WriteRecoveryAction:
    """Choose a safe action after an ambiguous write timeout.

    Callers must reconcile by deterministic client order ID before retrying.
    """

    if result == ReconcileResult.FOUND:
        return WriteRecoveryAction.ACCEPT_RECONCILED
    if result == ReconcileResult.NOT_FOUND and not retry_already_used:
        return WriteRecoveryAction.RETRY_ONCE
    return WriteRecoveryAction.HOLD_FOR_REVIEW
