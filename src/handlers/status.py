"""Name-search / registration-status handlers.

Handles the free-text name the user types after /start, searches the sheet
for similar names, and shows either matching students or a 'register new'
option as inline buttons.
"""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import messages, settings
from src.handlers import common, states
from src.keyboards import inline
from src.services import sheets
from src.services.matching import find_matches
from src.utils.validators import parse_search_name

logger = logging.getLogger(__name__)


async def menu_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry from the 'Registration status' main-menu button: prompt for a name."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await common.edit_or_send(update, messages.ASK_NAME)
    return states.SEARCH_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate the typed name and search the sheet for similar students."""
    text = update.effective_message.text or ""
    parts = parse_search_name(text)
    if parts is None:
        await update.effective_message.reply_text(
            messages.INVALID_NAME, parse_mode=ParseMode.HTML
        )
        return states.SEARCH_NAME

    query = " ".join(parts)
    context.user_data[states.UD_QUERY] = query
    await update.effective_message.reply_text(messages.SEARCHING)

    try:
        records = await sheets.get_records()
    except sheets.SheetError:
        await update.effective_message.reply_text(
            messages.SHEET_ERROR, parse_mode=ParseMode.HTML
        )
        return states.SEARCH_NAME

    context.user_data[states.UD_RECORDS] = records
    matches = find_matches(query, records)

    if matches:
        await update.effective_message.reply_text(
            messages.MATCHES_FOUND,
            parse_mode=ParseMode.HTML,
            reply_markup=inline.match_results_keyboard(matches),
        )
    else:
        await update.effective_message.reply_text(
            messages.NO_MATCHES,
            parse_mode=ParseMode.HTML,
            reply_markup=inline.register_new_only_keyboard(),
        )
    return states.SHOW_RESULTS


async def select_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the selected student's details from the sheet."""
    query = update.callback_query
    await query.answer()

    try:
        index = int(query.data[len(inline.CB_MATCH_PREFIX):])
    except (ValueError, IndexError):
        await common.edit_or_send(update, messages.GENERIC_ERROR)
        common.mark_conversation_idle(context)
        return ConversationHandler.END

    records = context.user_data.get(states.UD_RECORDS, [])
    if index < 0 or index >= len(records):
        await common.edit_or_send(update, messages.GENERIC_ERROR)
        common.mark_conversation_idle(context)
        return ConversationHandler.END

    record = records[index]
    missing = messages.STUDENT_DETAILS_MISSING

    await common.edit_or_send(
        update,
        messages.STUDENT_DETAILS.format(
            full_name=str(record.get(settings.COL_FULL_NAME, "")).strip() or missing,
            phone=str(record.get(settings.COL_PHONE, "")).strip() or missing,
            age=str(record.get(settings.COL_AGE, "")).strip() or missing,
            education=str(record.get(settings.COL_EDUCATION, "")).strip() or missing,
            assigned_class=str(record.get(settings.COL_ASSIGNED_CLASS, "")).strip() or missing,
            waiting_family=str(record.get(settings.COL_WAITING_FAMILY, "")).strip() or missing,
        ),
    )
    common.mark_conversation_idle(context)
    return ConversationHandler.END
