"""
codelancer.log_handler
In-memory log handler that captures structured log records for the /logs endpoint.
"""

import logging
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional


class InMemoryLogHandler(logging.Handler):
    """Logging handler that stores the most recent log records in memory."""

    def __init__(self, maxlen: int = 1000):
        super().__init__()
        self._records: deque = deque(maxlen=maxlen)

    def emit(self, record: logging.LogRecord) -> None:
        self._records.append({
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self.format(record),
        })

    def get_records(
        self,
        level: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[dict]:
        results = list(self._records)
        if level:
            level_upper = level.upper()
            results = [r for r in results if r["level"] == level_upper]
        if search:
            search_lower = search.lower()
            results = [r for r in results if search_lower in r["message"].lower()]
        if since:
            since_dt = datetime.fromisoformat(since)
            if since_dt.tzinfo is None:
                since_dt = since_dt.replace(tzinfo=timezone.utc)
            results = [
                r for r in results
                if datetime.fromisoformat(r["timestamp"]) >= since_dt
            ]
        if until:
            until_dt = datetime.fromisoformat(until)
            if until_dt.tzinfo is None:
                until_dt = until_dt.replace(tzinfo=timezone.utc)
            results = [
                r for r in results
                if datetime.fromisoformat(r["timestamp"]) <= until_dt
            ]
        return results[-limit:]
