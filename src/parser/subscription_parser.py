"""Parse proxy subscriptions from raw Telegram message text."""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, unquote, urlparse

from models.node import SubscriptionNode

SUPPORTED_PROTOCOLS = ("vmess", "vless", "trojan", "ss", "socks")
_LINK_PATTERN = re.compile(r"(?P<link>(?:vmess|vless|trojan|ss|socks)://[^\s<>\"]+)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class ParsedSubscription:
    """Parsed subscription payload extracted from text."""

    nodes: tuple[SubscriptionNode, ...]


class SubscriptionParser:
    """Extract supported proxy URLs from Telegram messages."""

    def parse_text(self, text: str, source: str | None = None) -> ParsedSubscription:
        nodes: list[SubscriptionNode] = []
        for match in _LINK_PATTERN.finditer(text):
            raw_link = self._cleanup_link(match.group("link"))
            node = self._parse_link(raw_link, source=source)
            if node is not None:
                nodes.append(node)
        return ParsedSubscription(nodes=tuple(nodes))

    def _cleanup_link(self, link: str) -> str:
        return link.rstrip(").,;]}>\"'")

    def _parse_link(self, link: str, source: str | None) -> SubscriptionNode | None:
        parsed = urlparse(link)
        protocol = parsed.scheme.lower()
        if protocol not in SUPPORTED_PROTOCOLS:
            return None

        if protocol == "vmess":
            return self._parse_vmess(link, source=source)

        username, password = self._parse_userinfo(parsed)
        query = dict(parse_qsl(parsed.query))
        metadata = {"raw": link}
        if query:
            metadata["query"] = query

        return SubscriptionNode(
            protocol=protocol,
            host=parsed.hostname or "",
            port=parsed.port or 0,
            username=username,
            password=password,
            uuid=username,
            security=query.get("security"),
            network=query.get("type") or query.get("network"),
            sni=query.get("sni") or query.get("peer") or query.get("host"),
            remark=unquote(parsed.fragment) or query.get("remarks") or query.get("name"),
            source=source,
            metadata=metadata,
        )

    def _parse_userinfo(self, parsed: Any) -> tuple[str | None, str | None]:
        username = parsed.username
        password = parsed.password
        return (username, password)

    def _parse_vmess(self, link: str, source: str | None) -> SubscriptionNode | None:
        encoded = link.removeprefix("vmess://")
        try:
            payload = self._decode_vmess_payload(encoded)
        except (ValueError, json.JSONDecodeError):
            return None

        host = str(payload.get("add", "")).strip()
        port_value = payload.get("port", 0)
        try:
            port = int(port_value)
        except (TypeError, ValueError):
            port = 0

        remark = payload.get("ps")
        metadata = {"raw": link, "vmess": payload}
        return SubscriptionNode(
            protocol="vmess",
            host=host,
            port=port,
            uuid=str(payload.get("id", "")) or None,
            security=str(payload.get("tls", "")) or None,
            network=str(payload.get("net", "")) or None,
            sni=str(payload.get("sni", "")) or None,
            remark=str(remark) if remark else None,
            source=source,
            metadata=metadata,
        )

    def _decode_vmess_payload(self, encoded: str) -> dict[str, Any]:
        decoded = self._base64_decode(encoded)
        payload = json.loads(decoded)
        if not isinstance(payload, dict):
            raise ValueError("vmess payload must be a JSON object")
        return payload

    def _base64_decode(self, encoded: str) -> str:
        padding = "=" * (-len(encoded) % 4)
        raw = base64.b64decode((encoded + padding).encode("utf-8"), altchars=b"-_", validate=False)
        return raw.decode("utf-8")
