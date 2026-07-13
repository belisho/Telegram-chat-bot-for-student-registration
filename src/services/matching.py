"""Fuzzy name matching against existing student records.

Matches the typed query against the single "Full Name" column. Uses RapidFuzz's
WRatio, which blends partial and token-based scoring, so a user can type just
the first name (or first + father) and still match a longer full name without
having to enter the grandfather name.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rapidfuzz import fuzz

from config import settings


@dataclass(frozen=True)
class MatchResult:
    """A single matched student record and its similarity score."""

    index: int  # position within the source records list
    full_name: str
    education: str
    assigned_class: str
    score: float
    record: dict[str, Any]


def _get_full_name(record: dict[str, Any]) -> str:
    return str(record.get(settings.COL_FULL_NAME, "")).strip()


def find_matches(
    query: str,
    records: list[dict[str, Any]],
    *,
    threshold: int | None = None,
    limit: int | None = None,
) -> list[MatchResult]:
    """Return records whose full name is similar to ``query``.

    Results are sorted by descending similarity and capped at ``limit``.
    """
    threshold = settings.NAME_MATCH_THRESHOLD if threshold is None else threshold
    limit = settings.MAX_MATCH_RESULTS if limit is None else limit

    normalized_query = query.strip().casefold()
    matches: list[MatchResult] = []

    for idx, record in enumerate(records):
        full_name = _get_full_name(record)
        if not full_name:
            continue
        # WRatio handles partial matches, so typing only the first name(s)
        # still scores high against the complete full name.
        score = fuzz.WRatio(normalized_query, full_name.casefold())
        if score >= threshold:
            matches.append(
                MatchResult(
                    index=idx,
                    full_name=full_name,
                    education=str(record.get(settings.COL_EDUCATION, "")).strip(),
                    assigned_class=str(record.get(settings.COL_ASSIGNED_CLASS, "")).strip(),
                    score=score,
                    record=record,
                )
            )

    matches.sort(key=lambda m: m.score, reverse=True)
    return matches[:limit]
