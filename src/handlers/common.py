"""Shared helpers for handlers."""
from __future__ import annotations

import logging

from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.handlers import states

logger = logging.getLogger(__name__)


def mark_conversation_idle(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mark the chat as idle so the next input shows the main menu."""
    context.user_data.clear()
    context.user_data[states.UD_IDLE] = True


def clear_conversation_idle(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the idle flag when a new conversation flow starts."""
    context.user_data.pop(states.UD_IDLE, None)


async def edit_or_send(
    update: Update,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Respond to a callback by editing the clicked message in place.

    When the update comes from an inline-button tap, the message that held the
    button is edited to show the next content (removing the old buttons). If the
    edit is not possible (e.g. the button was attached to a photo/caption
    message) or the update is not a callback, a new message is sent instead.
    """
    query = update.callback_query
    if query is not None:
        try:
            await query.edit_message_text(
                text, parse_mode=ParseMode.HTML, reply_markup=reply_markup
            )
            return
        except Exception:  # noqa: BLE001 - fall back to sending a new message
            logger.debug("Could not edit message; sending a new one instead", exc_info=True)

    await update.effective_chat.send_message(
        text, parse_mode=ParseMode.HTML, reply_markup=reply_markup
    )
