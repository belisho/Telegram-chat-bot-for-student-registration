"""Inline keyboard builders and their callback-data constants."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import messages
from src.services.matching import MatchResult

# Callback-data prefixes/values (keep short: Telegram limits to 64 bytes).
CB_MATCH_PREFIX = "match:"
CB_REGISTER_NEW = "register_new"
CB_EDU_PREFIX = "edu:"
CB_WF_YES = "wf:yes"
CB_WF_NO = "wf:no"
CB_MENU_REGISTER = "menu:register"
CB_MENU_STATUS = "menu:status"
CB_CANCEL = "cancel"


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Two-choice menu: register a new student or check registration status."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=messages.BTN_TO_REGISTER, callback_data=CB_MENU_REGISTER)],
            [
                InlineKeyboardButton(
                    text=messages.BTN_REGISTRATION_STATUS, callback_data=CB_MENU_STATUS
                )
            ],
        ]
    )


def match_results_keyboard(matches: list[MatchResult]) -> InlineKeyboardMarkup:
    """One button per matched student, plus a 'register new' button."""
    rows: list[list[InlineKeyboardButton]] = []
    for match in matches:
        rows.append(
            [
                InlineKeyboardButton(
                    text=match.full_name,
                    callback_data=f"{CB_MATCH_PREFIX}{match.index}",
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text=messages.REGISTER_NEW_BUTTON, callback_data=CB_REGISTER_NEW)]
    )
    rows.append([InlineKeyboardButton(text=messages.BTN_CANCEL, callback_data=CB_CANCEL)])
    return InlineKeyboardMarkup(rows)


def register_new_only_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown when there are no matches: register + cancel."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=messages.REGISTER_NEW_BUTTON, callback_data=CB_REGISTER_NEW)],
            [InlineKeyboardButton(text=messages.BTN_CANCEL, callback_data=CB_CANCEL)],
        ]
    )


def education_keyboard() -> InlineKeyboardMarkup:
    """Two-column keyboard of the configured education levels."""
    buttons = [
        InlineKeyboardButton(text=level, callback_data=f"{CB_EDU_PREFIX}{idx}")
        for idx, level in enumerate(messages.EDUCATION_LEVELS)
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)


def waiting_family_keyboard() -> InlineKeyboardMarkup:
    """Yes / No keyboard for the waiting-family question."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=messages.WAITING_FAMILY_YES, callback_data=CB_WF_YES),
                InlineKeyboardButton(text=messages.WAITING_FAMILY_NO, callback_data=CB_WF_NO),
            ]
        ]
    )
