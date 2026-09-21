from __future__ import annotations

from factor_forge_public.brokers.base import Broker
from factor_forge_public.execution.models import (
    AccountSnapshot,
    Fill,
    OrderRequest,
    OrderSide,
    OrderType,
    Position,
)
from factor_forge_public.models import Candle


class PaperBroker(Broker):
    """Small deterministic futures-style simulator for research.

    Market orders fill at the supplied reference price plus configured slippage.
    Limit orders can fill only on a later candle passed to ``on_candle``. This is
    deliberately simpler than a real matching engine and should not be treated
    as proof of executable performance.
    """

    def __init__(
        self,
        *,
        initial_cash: float = 10_000.0,
        fee_bps: float = 4.0,
        slippage_bps: float = 2.0,
    ) -> None:
        if initial_cash <= 0 or fee_bps < 0 or slippage_bps < 0:
            raise ValueError("invalid paper broker configuration")
        self.cash = initial_cash
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.fees_paid = 0.0
        self.positions: dict[str, Position] = {}
        self.pending: dict[str, OrderRequest] = {}
        self.pending_submitted_at_ms: dict[str, int] = {}
        self.fills: dict[str, Fill] = {}

    def submit(self, order: OrderRequest, *, timestamp_ms: int) -> Fill | None:
        if order.client_order_id in self.pending or order.client_order_id in self.fills:
            raise ValueError(f"duplicate client_order_id: {order.client_order_id}")
        self._validate_reduce_only(order)
        if order.order_type == OrderType.LIMIT:
            self.pending[order.client_order_id] = order
            self.pending_submitted_at_ms[order.client_order_id] = timestamp_ms
            return None
        price = self._market_fill_price(order)
        return self._fill(order, price=price, timestamp_ms=timestamp_ms)

    def cancel(self, client_order_id: str) -> bool:
        removed = self.pending.pop(client_order_id, None) is not None
        self.pending_submitted_at_ms.pop(client_order_id, None)
        return removed

    def on_candle(self, candle: Candle) -> list[Fill]:
        """Process pending limits against one subsequent closed candle."""

        completed: list[Fill] = []
        for order in list(self.pending.values()):
            if order.symbol != candle.symbol or order.limit_price is None:
                continue
            submitted_at_ms = self.pending_submitted_at_ms[order.client_order_id]
            if candle.close_time_ms <= submitted_at_ms:
                continue
            if candle.low <= order.limit_price <= candle.high:
                self.pending.pop(order.client_order_id)
                self.pending_submitted_at_ms.pop(order.client_order_id, None)
                completed.append(
                    self._fill(order, price=order.limit_price, timestamp_ms=candle.close_time_ms)
                )
        return completed

    def account(self, *, marks: dict[str, float] | None = None) -> AccountSnapshot:
        marks = marks or {}
        unrealized = 0.0
        for symbol, position in self.positions.items():
            mark = marks.get(symbol, position.average_price)
            unrealized += position.quantity * (mark - position.average_price)
        return AccountSnapshot(
            cash=self.cash,
            equity=self.cash + unrealized,
            fees_paid=self.fees_paid,
            positions={key: value.model_copy(deep=True) for key, value in self.positions.items()},
        )

    def _market_fill_price(self, order: OrderRequest) -> float:
        direction = 1.0 if order.side == OrderSide.BUY else -1.0
        return order.reference_price * (1.0 + direction * self.slippage_bps / 10_000.0)

    def _fill(self, order: OrderRequest, *, price: float, timestamp_ms: int) -> Fill:
        fee = order.quantity * price * self.fee_bps / 10_000.0
        self.cash -= fee
        self.fees_paid += fee
        signed_quantity = order.quantity if order.side == OrderSide.BUY else -order.quantity
        self._apply_position(order.symbol, signed_quantity, price)
        fill = Fill(
            client_order_id=order.client_order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=price,
            fee=fee,
            filled_at_ms=timestamp_ms,
        )
        self.fills[order.client_order_id] = fill
        return fill

    def _apply_position(self, symbol: str, signed_quantity: float, price: float) -> None:
        position = self.positions.get(symbol, Position(symbol=symbol))
        old_quantity = position.quantity
        new_quantity = old_quantity + signed_quantity

        if old_quantity == 0 or old_quantity * signed_quantity > 0:
            total_notional = abs(old_quantity) * position.average_price + abs(signed_quantity) * price
            average_price = total_notional / abs(new_quantity)
            self.positions[symbol] = position.model_copy(
                update={"quantity": new_quantity, "average_price": average_price}
            )
            return

        closed_quantity = min(abs(old_quantity), abs(signed_quantity))
        direction = 1.0 if old_quantity > 0 else -1.0
        realized = closed_quantity * (price - position.average_price) * direction
        self.cash += realized
        accumulated = position.realized_pnl + realized

        if new_quantity == 0:
            self.positions[symbol] = position.model_copy(
                update={"quantity": 0.0, "average_price": 0.0, "realized_pnl": accumulated}
            )
        elif old_quantity * new_quantity > 0:
            self.positions[symbol] = position.model_copy(
                update={"quantity": new_quantity, "realized_pnl": accumulated}
            )
        else:
            self.positions[symbol] = position.model_copy(
                update={"quantity": new_quantity, "average_price": price, "realized_pnl": accumulated}
            )

    def _validate_reduce_only(self, order: OrderRequest) -> None:
        if not order.reduce_only:
            return
        quantity = self.positions.get(order.symbol, Position(symbol=order.symbol)).quantity
        reduces_long = quantity > 0 and order.side == OrderSide.SELL and order.quantity <= quantity
        reduces_short = quantity < 0 and order.side == OrderSide.BUY and order.quantity <= abs(quantity)
        if not (reduces_long or reduces_short):
            raise ValueError("reduce-only order would increase or reverse exposure")
