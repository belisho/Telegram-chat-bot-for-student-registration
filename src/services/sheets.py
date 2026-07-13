"""Google Sheets access layer using gspread + a service account.

The gspread client and worksheet are created lazily and cached, so we only
authorize once per process. Blocking gspread calls are wrapped with
``asyncio.to_thread`` in the async helpers so they don't block the event loop.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from config import settings

logger = logging.getLogger(__name__)

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

_worksheet: gspread.Worksheet | None = None


class SheetError(RuntimeError):
    """Raised when the Google Sheet cannot be reached or read."""


def _get_worksheet() -> gspread.Worksheet:
    """Return a cached worksheet handle, authorizing on first use."""
    global _worksheet
    if _worksheet is not None:
        return _worksheet

    try:
        creds = Credentials.from_service_account_file(
            str(settings.GOOGLE_CREDENTIALS_FILE), scopes=_SCOPES
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
        _worksheet = spreadsheet.worksheet(settings.GOOGLE_WORKSHEET_NAME)
    except Exception as exc:  # noqa: BLE001 - surface any auth/network error uniformly
        logger.exception("Failed to open Google worksheet")
        raise SheetError(str(exc)) from exc

    _ensure_headers(_worksheet)
    return _worksheet


def _ensure_headers(worksheet: gspread.Worksheet) -> None:
    """Write the header row if the sheet is empty."""
    try:
        existing = worksheet.row_values(1)
    except Exception:  # noqa: BLE001
        existing = []
    if not existing:
        worksheet.update("A1", [settings.SHEET_HEADERS])


def _fetch_records() -> list[dict[str, Any]]:
    worksheet = _get_worksheet()
    try:
        return worksheet.get_all_records()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to read records from sheet")
        raise SheetError(str(exc)) from exc


def _count_rows() -> int:
    """Number of data rows (excludes the header row)."""
    worksheet = _get_worksheet()
    try:
        # len(get_all_values) counts header + data rows; subtract the header.
        values = worksheet.get_all_values()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to count rows in sheet")
        raise SheetError(str(exc)) from exc
    return max(0, len(values) - 1)


def _append_registration(row: dict[str, Any]) -> None:
    worksheet = _get_worksheet()
    ordered = [str(row.get(header, "")) for header in settings.SHEET_HEADERS]
    try:
        # table_range="A1" + INSERT_ROWS makes Sheets add a brand new row after
        # the last data row instead of overwriting existing cells (the default
        # OVERWRITE behaviour can clobber the last row when a Google Form is
        # linked to the sheet).
        worksheet.append_row(
            ordered,
            value_input_option="USER_ENTERED",
            insert_data_option="INSERT_ROWS",
            table_range="A1",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to append registration row")
        raise SheetError(str(exc)) from exc


# --- Async public API ---

async def get_records() -> list[dict[str, Any]]:
    """Return all student records as a list of dicts keyed by header."""
    return await asyncio.to_thread(_fetch_records)


async def count_registrations() -> int:
    """Return the current number of registrants (data rows in the sheet)."""
    return await asyncio.to_thread(_count_rows)


async def add_registration(
    *,
    full_name: str,
    phone: str,
    age: int,
    education: str,
    waiting_family: str,
) -> None:
    """Append a new registration to the sheet with a timestamp."""
    now = datetime.now()
    # Match the Google Form timestamp style, e.g. 7/12/2026 20:12:10
    timestamp = f"{now.month}/{now.day}/{now.year} {now.hour}:{now.minute:02d}:{now.second:02d}"
    row = {
        settings.COL_TIMESTAMP: timestamp,
        settings.COL_FULL_NAME: full_name,
        settings.COL_PHONE: phone,
        settings.COL_AGE: age,
        settings.COL_EDUCATION: education,
        settings.COL_WAITING_FAMILY: waiting_family,
    }
    await asyncio.to_thread(_append_registration, row)
