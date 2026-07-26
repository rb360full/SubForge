"""Location helpers for grouping subscription nodes."""

from __future__ import annotations

from urllib.parse import unquote

from models.node import SubscriptionNode

_REGIONAL_INDICATOR_BASE = 0x1F1E6
_REGIONAL_INDICATOR_END = 0x1F1FF
_COUNTRY_FILE_OVERRIDES = {
    "GB": "EN",
    "UK": "EN",
}


def country_code_for_node(node: SubscriptionNode) -> str | None:
    """Return a two-letter location code for a tested subscription node."""

    metadata_code = _country_code_from_metadata(node.metadata)
    if metadata_code:
        return metadata_code

    candidates = [
        node.remark,
        node.metadata.get("raw") if isinstance(node.metadata, dict) else None,
    ]
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        flag_code = _country_code_from_flag(candidate)
        if flag_code:
            return flag_code
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


def _country_code_from_flag(text: str) -> str | None:
    decoded = unquote(text)
    for index in range(len(decoded) - 1):
        first = ord(decoded[index])
        second = ord(decoded[index + 1])
        if (
            _REGIONAL_INDICATOR_BASE <= first <= _REGIONAL_INDICATOR_END
            and _REGIONAL_INDICATOR_BASE <= second <= _REGIONAL_INDICATOR_END
        ):
            code = chr(ord("A") + first - _REGIONAL_INDICATOR_BASE)
            code += chr(ord("A") + second - _REGIONAL_INDICATOR_BASE)
            return _normalize_country_file_code(code)
    return None


def _normalize_country_file_code(code: str) -> str:
    return _COUNTRY_FILE_OVERRIDES.get(code, code)
