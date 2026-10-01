from __future__ import annotations

import json
import logging
from typing import Any, Dict


class StructuredLogger:
    """JSON-structured logger for trading events and alerts."""

    def __init__(self, name: str = "trading_agent") -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_event(self, event: str, **context: Any) -> None:
        payload = {"event": event, **context}
        self.logger.info(json.dumps(payload, default=str))


class WebhookNotifier:
    """Simple Telegram/Discord webhook API adapter with graceful failure handling."""

    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url

    def send(self, message: str) -> bool:
        if not self.webhook_url:
            return False
        try:
            import requests

            response = requests.post(self.webhook_url, data={"content": message}, timeout=10)
            return response.ok
        except Exception:
            return False
