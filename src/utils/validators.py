"""Input validation helpers for names, phone numbers and age."""
from __future__ import annotations

import re

# Phone must start with 09, 07, 2519, 2517, +2519 or +2517 then 8 more digits.
_PHONE_RE = re.compile(r"^(?:\+?251[79]|0[79])\d{8}$")

# A single name part: letters (Latin or Ethiopic) allowing hyphen/apostrophe.
_NAME_PART_RE = re.compile(r"^[\w'\-\u1200-\u137F]+$", re.UNICODE)

AGE_MIN = 7
AGE_MAX = 16


def normalize_phone(phone: str) -> str:
    """Strip spaces, dashes and parentheses from a phone number."""
    return re.sub(r"[\s\-()]", "", phone.strip())


def is_valid_phone(phone: str) -> bool:
    """True if the phone matches the accepted Ethiopian formats."""
    return bool(_PHONE_RE.match(normalize_phone(phone)))


def is_valid_age(value: str) -> bool:
    """True if ``value`` is an integer within the allowed age range."""
    try:
        age = int(str(value).strip())
    except (TypeError, ValueError):
        return False
    return AGE_MIN <= age <= AGE_MAX


def parse_age(value: str) -> int:
    """Return the age as an int (assumes ``is_valid_age`` already passed)."""
    return int(str(value).strip())


def is_valid_name_part(value: str) -> bool:
    """True if a single name field is a plausible name."""
    value = value.strip()
    return bool(value) and bool(_NAME_PART_RE.match(value))


def parse_full_name(text: str) -> list[str] | None:
    """Return the three name parts, or ``None`` if not exactly three valid parts.

    The student must type First, Middle and Last names separated by spaces.
    """
    parts = text.strip().split()
    if len(parts) != 3:
        return None
    if not all(is_valid_name_part(part) for part in parts):
        return None
    return parts


def parse_search_name(text: str) -> list[str] | None:
    """Return the name parts used to search, or ``None`` if invalid.

    The grandfather name is not required: the user may type just the first
    name, or the first and father names. We only require at least one valid
    name part; matching then compares it against the full name in the sheet.
    """
    parts = text.strip().split()
    if not parts:
        return None
    if not all(is_valid_name_part(part) for part in parts):
        return None
    return parts
