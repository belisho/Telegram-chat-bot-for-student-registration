"""Registration form handlers (multi-step ConversationHandler)."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import messages, settings
from src.handlers import common, states
from src.keyboards import inline
from src.services import sheets
from src.utils import validators

logger = logging.getLogger(__name__)


async def _limit_reached() -> bool:
    """True if the sheet already holds the maximum number of registrants."""
    count = await sheets.count_registrations()
    return count >= settings.REGISTRATION_LIMIT


async def _begin_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the intro + first-name prompt. Returns the next state or END."""
    # If triggered by a button, edit that message into the intro; else send new.
    await common.edit_or_send(update, messages.REG_START)

    try:
        count = await sheets.count_registrations()
        await update.effective_chat.send_message(
            messages.REGISTERED_COUNT.format(count=count, limit=settings.REGISTRATION_LIMIT),
            parse_mode=ParseMode.HTML,
        )
    except sheets.SheetError:
        logger.exception("Could not fetch registration count for the form intro")

    await update.effective_chat.send_message(messages.ASK_FIRST_NAME, parse_mode=ParseMode.HTML)
    return states.REG_FIRST_NAME


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the /register command."""
    context.user_data.clear()
    try:
        if await _limit_reached():
            await update.effective_message.reply_text(
                messages.LIMIT_EXCEEDED.format(limit=settings.REGISTRATION_LIMIT),
                parse_mode=ParseMode.HTML,
            )
            common.mark_conversation_idle(context)
            return ConversationHandler.END
    except sheets.SheetError:
        await update.effective_message.reply_text(
            messages.SHEET_ERROR, parse_mode=ParseMode.HTML
        )
        common.mark_conversation_idle(context)
        return ConversationHandler.END

    return await _begin_form(update, context)


async def menu_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry into the form from the 'To register' main-menu button."""
    return await register_new_callback(update, context)


async def register_new_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry into the form from the 'register new' inline button."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    try:
        if await _limit_reached():
            await common.edit_or_send(
                update, messages.LIMIT_EXCEEDED.format(limit=settings.REGISTRATION_LIMIT)
            )
            common.mark_conversation_idle(context)
            return ConversationHandler.END
    except sheets.SheetError:
        await common.edit_or_send(update, messages.SHEET_ERROR)
        common.mark_conversation_idle(context)
        return ConversationHandler.END

    return await _begin_form(update, context)


async def receive_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = (update.effective_message.text or "").strip()
    if not validators.is_valid_name_part(value):
        await update.effective_message.reply_text(
            messages.INVALID_FIRST_NAME, parse_mode=ParseMode.HTML
        )
        return states.REG_FIRST_NAME
    context.user_data[states.UD_FIRST_NAME] = value
    await update.effective_message.reply_text(messages.ASK_FATHER_NAME, parse_mode=ParseMode.HTML)
    return states.REG_FATHER_NAME


async def receive_father_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = (update.effective_message.text or "").strip()
    if not validators.is_valid_name_part(value):
        await update.effective_message.reply_text(
            messages.INVALID_FATHER_NAME, parse_mode=ParseMode.HTML
        )
        return states.REG_FATHER_NAME
    context.user_data[states.UD_FATHER_NAME] = value
    await update.effective_message.reply_text(messages.ASK_PHONE, parse_mode=ParseMode.HTML)
    return states.REG_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.effective_message.text or ""
    if not validators.is_valid_phone(value):
        await update.effective_message.reply_text(
            messages.INVALID_PHONE, parse_mode=ParseMode.HTML
        )
        return states.REG_PHONE
    context.user_data[states.UD_PHONE] = validators.normalize_phone(value)
    await update.effective_message.reply_text(messages.ASK_AGE, parse_mode=ParseMode.HTML)
    return states.REG_AGE


async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.effective_message.text or ""
    if not validators.is_valid_age(value):
        await update.effective_message.reply_text(
            messages.INVALID_AGE, parse_mode=ParseMode.HTML
        )
        return states.REG_AGE
    context.user_data[states.UD_AGE] = validators.parse_age(value)
    await update.effective_message.reply_text(
        messages.ASK_EDUCATION,
        parse_mode=ParseMode.HTML,
        reply_markup=inline.education_keyboard(),
    )
    return states.REG_EDUCATION


async def receive_education(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    try:
        index = int(query.data[len(inline.CB_EDU_PREFIX):])
        education = messages.EDUCATION_LEVELS[index]
    except (ValueError, IndexError):
        await query.answer(messages.INVALID_EDUCATION, show_alert=True)
        return states.REG_EDUCATION

    context.user_data[states.UD_EDUCATION] = education
    await common.edit_or_send(update, f"{messages.ASK_EDUCATION}\n✅ {education}")
    await update.effective_chat.send_message(
        messages.ASK_WAITING_FAMILY,
        parse_mode=ParseMode.HTML,
        reply_markup=inline.waiting_family_keyboard(),
    )
    return states.REG_WAITING_FAMILY


async def receive_waiting_family(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == inline.CB_WF_YES:
        waiting_family = messages.WAITING_FAMILY_YES
    elif query.data == inline.CB_WF_NO:
        waiting_family = messages.WAITING_FAMILY_NO
    else:
        return states.REG_WAITING_FAMILY

    data = context.user_data
    full_name = f"{data[states.UD_FIRST_NAME]} {data[states.UD_FATHER_NAME]}".strip()
    try:
        await sheets.add_registration(
            full_name=full_name,
            phone=data[states.UD_PHONE],
            age=data[states.UD_AGE],
            education=data[states.UD_EDUCATION],
            waiting_family=waiting_family,
        )
    except sheets.SheetError:
        await common.edit_or_send(update, messages.SHEET_ERROR)
        common.mark_conversation_idle(context)
        return ConversationHandler.END
    except KeyError:
        logger.exception("Missing registration field in user_data")
        await common.edit_or_send(update, messages.GENERIC_ERROR)
        common.mark_conversation_idle(context)
        return ConversationHandler.END

    await common.edit_or_send(
        update,
        messages.REG_CONFIRMATION.format(
            first_name=data[states.UD_FIRST_NAME],
            father_name=data[states.UD_FATHER_NAME],
            phone=data[states.UD_PHONE],
            age=data[states.UD_AGE],
            education=data[states.UD_EDUCATION],
            waiting_family=waiting_family,
        ),
    )
    common.mark_conversation_idle(context)
    return ConversationHandler.END
