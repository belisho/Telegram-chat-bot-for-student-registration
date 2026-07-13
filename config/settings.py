"""Central configuration for the MHSS-KIDDS bot.

All secrets and environment-specific values are loaded from the ``.env`` file.
Import ``settings`` from this module to access configuration values.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root (two levels up from this file: config/ -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from the .env file located at the project root.
load_dotenv(BASE_DIR / ".env")


class ConfigError(RuntimeError):
    """Raised when a required configuration value is missing or invalid."""


def _get_env(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and (value is None or value.strip() == ""):
        raise ConfigError(
            f"Missing required environment variable '{name}'. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


# --- Telegram ---
BOT_TOKEN: str = _get_env("BOT_TOKEN", required=True)  # type: ignore[assignment]

# --- Google Sheets ---
GOOGLE_SHEET_ID: str = _get_env("GOOGLE_SHEET_ID", required=True)  # type: ignore[assignment]
GOOGLE_WORKSHEET_NAME: str = _get_env("GOOGLE_WORKSHEET_NAME", "Sheet1")  # type: ignore[assignment]

# Credentials path is resolved relative to the project root if not absolute.
_creds_raw = _get_env("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_CREDENTIALS_FILE: Path = (
    Path(_creds_raw) if os.path.isabs(_creds_raw) else BASE_DIR / _creds_raw  # type: ignore[arg-type]
)

# --- Registration rules ---
try:
    REGISTRATION_LIMIT: int = int(_get_env("REGISTRATION_LIMIT", "270"))  # type: ignore[arg-type]
except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
    raise ConfigError("REGISTRATION_LIMIT must be an integer.") from exc

# --- Sheet schema ---
# The order here is also the order used when appending a new registration row.
SHEET_HEADERS: list[str] = [
    "Timestamp",
    "ሙሉ ስም",
    "ስልክ ቁጥር",
    "እድሜ",
    "የት/ት ደረጃ",
    "ከትምህርት በኋላ ወደቤታቸው ለመሔድ ወላጅ ይጠብቃሉ?",
]

# Column names used when reading existing student records.
COL_FULL_NAME = "ሙሉ ስም"
COL_PHONE = "ስልክ ቁጥር"
COL_AGE = "እድሜ"
COL_EDUCATION = "የት/ት ደረጃ"
COL_WAITING_FAMILY = "ከትምህርት በኋላ ወደቤታቸው ለመሔድ ወላጅ ይጠብቃሉ?"
COL_TIMESTAMP = "Timestamp"

# Optional, read-only column. Not written by the bot; shown in student details
# if the sheet happens to contain it, otherwise displayed as "—".
COL_ASSIGNED_CLASS = "የተመደበበት ክፍል"

# Welcome image shown on /start. The file must be named "mhsskidds" and can be
# any common image type (png, jpg, jpeg, webp, gif, bmp). The first match found
# in the assets folder is used.
ASSETS_DIR: Path = BASE_DIR / "assets"
WELCOME_IMAGE_NAME: str = "mhsskidds"
SUPPORTED_IMAGE_EXTENSIONS: list[str] = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]


def find_welcome_image() -> Path | None:
    """Return the welcome image path (any supported type), or None if absent."""
    for ext in SUPPORTED_IMAGE_EXTENSIONS:
        candidate = ASSETS_DIR / f"{WELCOME_IMAGE_NAME}{ext}"
        if candidate.exists():
            return candidate
    return None

# Fuzzy-matching threshold (0-100). Names scoring at/above this are shown as matches.
NAME_MATCH_THRESHOLD: int = int(_get_env("NAME_MATCH_THRESHOLD", "70"))  # type: ignore[arg-type]

# Maximum number of match buttons to display.
MAX_MATCH_RESULTS: int = int(_get_env("MAX_MATCH_RESULTS", "5"))  # type: ignore[arg-type]


def validate() -> None:
    """Validate configuration at startup; raise ConfigError on problems."""
    if not BOT_TOKEN:
        raise ConfigError("BOT_TOKEN is empty.")
    if not GOOGLE_SHEET_ID:
        raise ConfigError("GOOGLE_SHEET_ID is empty.")
    if not GOOGLE_CREDENTIALS_FILE.exists():
        raise ConfigError(
            f"Google credentials file not found at '{GOOGLE_CREDENTIALS_FILE}'. "
            f"See README.md for how to create a service account key."
        )
