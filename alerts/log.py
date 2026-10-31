import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT NOT NULL,
                type        TEXT NOT NULL,
                asset       TEXT,
                description TEXT NOT NULL,
                values_json TEXT
            )
        """)


def log_event(type: str, description: str, asset: str = None, values: dict = None) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO events (timestamp, type, asset, description, values_json) VALUES (?,?,?,?,?)",
            (
                datetime.utcnow().isoformat(),
                type,
                asset,
                description,
                json.dumps(values) if values else None,
            ),
        )


def get_events(limit: int = 100, type_filter: list = None, asset_filter: list = None) -> list[dict]:
    init_db()
    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if type_filter:
        placeholders = ",".join("?" * len(type_filter))
        query += f" AND type IN ({placeholders})"
        params.extend(type_filter)

    if asset_filter:
        placeholders = ",".join("?" * len(asset_filter))
        query += f" AND asset IN ({placeholders})"
        params.extend(asset_filter)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(r) for r in rows]


def was_recently_alerted(type: str, asset: str, cooldown_hours: int) -> bool:
    init_db()
    cutoff = (datetime.utcnow() - timedelta(hours=cooldown_hours)).isoformat()
    with _connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM events WHERE type=? AND asset=? AND timestamp > ?",
            (type, asset, cutoff),
        ).fetchone()[0]
    return count > 0


if __name__ == "__main__":
    init_db()
    log_event("test", "Evento de prueba desde log.py", asset="SYSTEM", values={"ok": True})
    events = get_events(limit=5)
    print(f"Last {len(events)} events:")
    for e in events:
        print(f"  [{e['timestamp']}] {e['type']} | {e['asset']} — {e['description']}")
