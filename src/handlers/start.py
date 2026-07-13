"""/start, /help and /cancel handlers."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import messages, settings
from src.handlers import common, states
from src.keyboards import inline
from src.services import sheets

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the logo and welcome text, then prompt for the student's name."""
    context.user_data.clear()
    chat = update.effective_chat

    menu = inline.main_menu_keyboard()
    image_path = settings.find_welcome_image()
    welcome_sent_as_caption = False
    if image_path is not None:
        try:
            with image_path.open("rb") as image:
                await chat.send_photo(
                    photo=image,
                    caption=messages.WELCOME,
                    parse_mode=ParseMode.HTML,
                    reply_markup=menu,
                )
            welcome_sent_as_caption = True
        except Exception:  # noqa: BLE001 - image is non-critical
            logger.exception("Failed to send welcome image")
    else:
        logger.warning(
            "Welcome image '%s' not found in %s; sending text only",
            settings.WELCOME_IMAGE_NAME,
            settings.ASSETS_DIR,
        )

    # Fallback: if no image was sent, still show the welcome text.
    if not welcome_sent_as_caption:
        await chat.send_message(
            messages.WELCOME, parse_mode=ParseMode.HTML, reply_markup=menu
        )

    return states.SEARCH_NAME


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(messages.HELP, parse_mode=ParseMode.HTML)


async def _send_menu(chat, text: str) -> None:
    """Send a caption with the main menu inline buttons."""
    await chat.send_message(
        text, parse_mode=ParseMode.HTML, reply_markup=inline.main_menu_keyboard()
    )


async def _send_cancel_menu(chat) -> None:
    """After cancel: cancelled notice + menu prompt."""
    await _send_menu(chat, messages.CHOOSE_ACTION)


async def _send_idle_menu(chat) -> None:
    """After conversation ended: menu prompt only (no cancelled text)."""
    await _send_menu(chat, messages.MENU_PROMPT)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel any ongoing conversation and show the main menu (/cancel command)."""
    common.mark_conversation_idle(context)
    await _send_cancel_menu(update.effective_chat)
    return ConversationHandler.END


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel from an inline 'Cancel' button; behaves like /cancel."""
    query = update.callback_query
    await query.answer()
    common.mark_conversation_idle(context)
    await common.edit_or_send(update, messages.CANCELLED)
    await update.effective_chat.send_message(
        messages.CHOOSE_ACTION,
        parse_mode=ParseMode.HTML,
        reply_markup=inline.main_menu_keyboard(),
    )
    return ConversationHandler.END


async def idle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """After a conversation ends, guide the user back with the main menu."""
    if not context.user_data.get(states.UD_IDLE):
        return
    await _send_idle_menu(update.effective_chat)
