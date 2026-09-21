from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from factor_forge_public.monitoring.audit import AuditEvent


class SQLiteAuditLog:
    """Append-only local audit sink with a generic, public schema."""

    def __init__(self, path: str | Path, *, busy_timeout_ms: int = 5_000) -> None:
        self.path = Path(path)
        self.busy_timeout_ms = busy_timeout_ms
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_ms INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    correlation_id TEXT,
                    details_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_category_time "
                "ON audit_events(category, timestamp_ms)"
            )

    def append(self, event: AuditEvent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events(
                    timestamp_ms, category, action, outcome, correlation_id, details_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.timestamp_ms,
                    event.category,
                    event.action,
                    event.outcome,
                    event.correlation_id,
                    json.dumps(event.details, sort_keys=True, separators=(",", ":")),
                ),
            )

    def events(self, *, category: str | None = None) -> list[AuditEvent]:
        query = (
            "SELECT timestamp_ms, category, action, outcome, correlation_id, details_json "
            "FROM audit_events"
        )
        parameters: tuple[str, ...] = ()
        if category is not None:
            query += " WHERE category = ?"
            parameters = (category,)
        query += " ORDER BY sequence"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [
            AuditEvent(
                timestamp_ms=row[0],
                category=row[1],
                action=row[2],
                outcome=row[3],
                correlation_id=row[4],
                details=json.loads(row[5]),
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute(f"PRAGMA busy_timeout={int(self.busy_timeout_ms)}")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection
