from __future__ import annotations

import sqlite3
from pathlib import Path


class StateStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS published_posts (
                    platform TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (platform, post_id)
                )
                """
            )

    def already_processed(self, platform: str, post_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM published_posts WHERE platform = ? AND post_id = ?",
                (platform, post_id),
            ).fetchone()
        return bool(row)

    def mark_processed(self, platform: str, post_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO published_posts(platform, post_id) VALUES (?, ?)",
                (platform, post_id),
            )
