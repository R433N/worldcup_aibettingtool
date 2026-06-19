"""Provider-neutral ingestion helpers for API and local JSON feeds."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class IngestionError(RuntimeError):
    pass


class HttpJsonClient:
    """Small stdlib HTTP client with retries for free API integrations."""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None, timeout_seconds: int = 20):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout_seconds = timeout_seconds

    def get_json(self, endpoint: str, retries: int = 3, backoff_seconds: float = 0.5) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                request = Request(url, headers={"Accept": "application/json", **self.headers})
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < retries - 1:
                    time.sleep(backoff_seconds * (2**attempt))
        raise IngestionError(f"Could not load JSON from {url}: {last_error}") from last_error


class LocalJsonFeed:
    """Deterministic local feed used for tests and provider export imports."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def read(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IngestionError(f"Could not read local feed {self.path}: {exc}") from exc


def require_fields(payload: dict[str, Any], fields: tuple[str, ...], source_name: str) -> None:
    missing = [field for field in fields if field not in payload]
    if missing:
        raise IngestionError(f"{source_name} payload missing required fields: {', '.join(missing)}")
