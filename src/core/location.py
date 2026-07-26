"""Location helpers for grouping subscription nodes."""

from __future__ import annotations

from models.node import SubscriptionNode

_COUNTRY_FILE_OVERRIDES = {
    "GB": "EN",
    "UK": "EN",
}


def country_code_for_node(node: SubscriptionNode) -> str | None:
    """Return a two-letter location code for a tested subscription node."""

    metadata_code = _country_code_from_metadata(node.metadata)
    if metadata_code:
        return metadata_code
    return None


def _country_code_from_metadata(metadata: object) -> str | None:
    if not isinstance(metadata, dict):
        return None
    for key in ("country_code", "country", "location"):
        value = metadata.get(key)
        if not isinstance(value, str):
            continue
        code = value.strip().upper()
        if len(code) == 2 and code.isalpha():
            return _normalize_country_file_code(code)
    return None


def _normalize_country_file_code(code: str) -> str:
    return _COUNTRY_FILE_OVERRIDES.get(code, code)
