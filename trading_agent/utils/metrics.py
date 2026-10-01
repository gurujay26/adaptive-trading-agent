from __future__ import annotations

import json
import logging
from typing import Any


class StructuredLogger:
    """JSON structured logger."""

    def __init__(self, name: str = "trading_agent") -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def log_event(self, event: str, **context: Any) -> None:
        self.logger.info(json.dumps({"event": event, **context}, default=str))


class WebhookNotifier:
    """Simple Telegram/Discord webhook sender."""

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

