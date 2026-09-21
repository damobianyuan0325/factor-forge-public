from __future__ import annotations

import hashlib

from factor_forge_public.runtime import SignalPlan


def deterministic_client_order_id(plan: SignalPlan, *, namespace: str = "research") -> str:
    """Return the same compact ID for the same causal strategy decision."""

    material = "|".join(
        (
            namespace,
            plan.strategy_id,
            plan.strategy_version,
            plan.symbol,
            plan.timeframe,
            plan.decision.value,
            str(plan.observed_at_ms),
        )
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{namespace}-{digest}"
