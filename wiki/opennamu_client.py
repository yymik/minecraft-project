from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class OpenNAMUConfig:
    enabled: bool
    base_url: str
    api_token: Optional[str] = None
    endpoints: Optional[Dict[str, str]] = None

    @classmethod
    def from_settings(cls) -> "OpenNAMUConfig":
        raw = getattr(settings, "OPENNAMU", {}) or {}
        enabled = bool(raw.get("ENABLED")) and bool(raw.get("BASE_URL"))
        endpoints = raw.get("ENDPOINTS") or {
            "GET_PAGE": "/api/document/{title}",
            "PUT_PAGE": "/api/document/{title}"
        }
        return cls(
            enabled=enabled,
            base_url=(raw.get("BASE_URL") or "").rstrip("/"),
            api_token=raw.get("API_TOKEN"),
            endpoints=endpoints,
        )


class OpenNAMUClient:
    def __init__(self, config: Optional[OpenNAMUConfig] = None):
        self.config = config or OpenNAMUConfig.from_settings()

    @property
    def enabled(self) -> bool:
        return self.config.enabled

    def _resolve_endpoint(self, key: str, title: str) -> str:
        endpoint = self.config.endpoints.get(key)
        if not endpoint:
            raise ValueError(f"Endpoint {key} is not configured.")
        return endpoint.format(title=quote(title))

    def _make_url(self, path: str) -> str:
        return f"{self.config.base_url}{path}"

    def fetch_page(self, title: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        try:
            path = self._resolve_endpoint("GET_PAGE", title)
            response = requests.get(self._make_url(path), timeout=5)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            # openNAMU의 응답을 표준화
            return {
                "title": data.get("title") or title,
                "content": data.get("content") or data.get("data") or "",
                "summary": data.get("summary") or "",
                "updated_at": data.get("updated") or data.get("timestamp"),
                "metadata": data,
            }
        except Exception as exc:
            logger.warning("openNAMU fetch failed for %s: %s", title, exc)
            return None

    def push_page(self, title: str, content: str, summary: str = "") -> bool:
        if not self.enabled:
            return False
        payload = {
            "title": title,
            "content": content,
            "summary": summary,
        }
        headers = {}
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        try:
            path = self._resolve_endpoint("PUT_PAGE", title)
            response = requests.put(
                self._make_url(path),
                json=payload,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            logger.error("openNAMU push failed for %s: %s", title, exc)
            return False


_cached_client: Optional[OpenNAMUClient] = None


def get_opennamu_client() -> OpenNAMUClient:
    global _cached_client
    if _cached_client is None:
        _cached_client = OpenNAMUClient()
    return _cached_client
