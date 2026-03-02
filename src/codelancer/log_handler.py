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
    ) -> List[dict]:
        results = list(self._records)
        if level:
            level_upper = level.upper()
            results = [r for r in results if r["level"] == level_upper]
        if search:
            search_lower = search.lower()
            results = [r for r in results if search_lower in r["message"].lower()]
        return results[-limit:]
