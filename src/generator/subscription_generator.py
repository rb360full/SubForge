"""Generate importable subscription payloads."""

from __future__ import annotations

import base64
import json

from models.node import SubscriptionNode


class SubscriptionGenerator:
    """Create subscription payloads for client import."""

    def generate(self, nodes: tuple[SubscriptionNode, ...]) -> str:
        lines = [self._serialize_node(node) for node in nodes]
        payload = "\n".join(lines)
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        return encoded

    def _serialize_node(self, node: SubscriptionNode) -> str:
        if node.protocol == "vmess":
            return self._serialize_vmess(node)
        if node.protocol == "vless":
            return self._serialize_vless(node)
        if node.protocol == "trojan":
            return self._serialize_trojan(node)
        if node.protocol == "ss":
            return self._serialize_ss(node)
        if node.protocol == "socks":
            return self._serialize_socks(node)
        raise ValueError(f"Unsupported protocol: {node.protocol}")

    def _serialize_vmess(self, node: SubscriptionNode) -> str:
        payload = {
            "v": "2",
            "ps": node.remark or node.host,
            "add": node.host,
            "port": str(node.port),
            "id": node.uuid or "",
            "aid": "0",
            "scy": node.security or "auto",
            "net": node.network or "tcp",
            "type": "none",
            "host": node.sni or "",
            "path": "",
            "tls": node.security or "",
            "sni": node.sni or "",
        }
        encoded = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii")
        return f"vmess://{encoded}"

    def _serialize_vless(self, node: SubscriptionNode) -> str:
        return self._serialize_uri(node, "vless")

    def _serialize_trojan(self, node: SubscriptionNode) -> str:
        return self._serialize_uri(node, "trojan")

    def _serialize_ss(self, node: SubscriptionNode) -> str:
        return self._serialize_uri(node, "ss")

    def _serialize_socks(self, node: SubscriptionNode) -> str:
        return self._serialize_uri(node, "socks")

    def _serialize_ss(self, node: SubscriptionNode) -> str:
        if not node.username or node.password is None:
            raise ValueError("SS node requires method and password")
        auth = f"{node.username}:{node.password}"
        encoded = base64.b64encode(auth.encode("utf-8")).decode("ascii")
        uri = f"ss://{encoded}@{node.host}:{node.port}"
        if node.remark:
            uri += f"#{node.remark}"
        return uri

    def _serialize_uri(self, node: SubscriptionNode, scheme: str) -> str:
        auth = node.uuid or node.username or ""
        if node.password:
            auth = f"{auth}:{node.password}"
        host = node.host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        uri = f"{scheme}://{auth}@{host}:{node.port}"
        params = []
        if node.security:
            params.append(f"security={node.security}")
        if node.network:
            params.append(f"type={node.network}")
        if node.sni:
            params.append(f"sni={node.sni}")
        if params:
            uri += "?" + "&".join(params)
        if node.remark:
            uri += f"#{node.remark}"
        return uri
