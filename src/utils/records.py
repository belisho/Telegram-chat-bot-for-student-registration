"""Helpers for reading student records from Google Sheet rows."""
from __future__ import annotations

from typing import Any


def _normalize_key(key: str) -> str:
    """Collapse whitespace/newlines so header variants still match."""
    return " ".join(str(key).split())


def get_field(record: dict[str, Any], *keys: str) -> str:
    """Return the first non-empty value for any of the given column headers.

    Also matches headers that differ only by spaces vs newlines (common with
    Google Form-linked sheets).
    """
    for key in keys:
        value = str(record.get(key, "")).strip()
        if value:
            return value

    normalized_targets = {_normalize_key(key) for key in keys}
    for record_key, raw in record.items():
        if _normalize_key(record_key) in normalized_targets:
            value = str(raw).strip()
            if value:
                return value
    return ""
