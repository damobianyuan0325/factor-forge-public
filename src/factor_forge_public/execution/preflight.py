from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class PreflightRecord(BaseModel):
    client_order_id: str
    payload_hash: str
    approved: bool = False
    approved_by: str | None = None


class JsonlPreflightLedger:
    """Append-only preflight ledger with no exchange-specific fields."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, client_order_id: str, payload: dict[str, Any]) -> PreflightRecord:
        if self.find(client_order_id) is not None:
            raise ValueError("client_order_id already exists in preflight ledger")
        record = PreflightRecord(
            client_order_id=client_order_id,
            payload_hash=canonical_payload_hash(payload),
        )
        self._append(record)
        return record

    def approve(self, client_order_id: str, payload: dict[str, Any], *, approved_by: str) -> PreflightRecord:
        existing = self.find(client_order_id)
        if existing is None:
            raise ValueError("preflight record not found")
        if existing.payload_hash != canonical_payload_hash(payload):
            raise ValueError("payload changed after preflight")
        approved = existing.model_copy(update={"approved": True, "approved_by": approved_by})
        self._append(approved)
        return approved

    def require_approval(self, client_order_id: str, payload: dict[str, Any]) -> PreflightRecord:
        record = self.find(client_order_id)
        if record is None or not record.approved:
            raise ValueError("exact payload has not been approved")
        if record.payload_hash != canonical_payload_hash(payload):
            raise ValueError("approved payload does not match current payload")
        return record

    def find(self, client_order_id: str) -> PreflightRecord | None:
        latest = None
        if not self.path.exists():
            return None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = PreflightRecord.model_validate_json(line)
            if record.client_order_id == client_order_id:
                latest = record
        return latest

    def _append(self, record: PreflightRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")
