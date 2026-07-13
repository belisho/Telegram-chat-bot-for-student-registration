"""Application factory: builds the Telegram Application and registers handlers."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import messages, settings
from src.handlers import register, start, states, status
from src.keyboards import inline

logger = logging.getLogger(__name__)


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log unexpected errors and notify the user when possible."""
    logger.error("Unhandled exception while processing update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message is not None:
        try:
            await update.effective_message.reply_text(
                messages.GENERIC_ERROR, parse_mode=ParseMode.HTML
            )
        except Exception:  # noqa: BLE001
            pass


def _build_conversation() -> ConversationHandler:
    """The main conversation covering status search and registration."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start.start),
            CommandHandler("register", register.register_command),
            CommandHandler("status", start.start),
            CallbackQueryHandler(register.menu_register, pattern=f"^{inline.CB_MENU_REGISTER}$"),
            CallbackQueryHandler(status.menu_status, pattern=f"^{inline.CB_MENU_STATUS}$"),
        ],
        states={
            states.SEARCH_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, status.receive_name),
            ],
            states.SHOW_RESULTS: [
                CallbackQueryHandler(
                    register.register_new_callback, pattern=f"^{inline.CB_REGISTER_NEW}$"
                ),
                CallbackQueryHandler(
                    status.select_match, pattern=f"^{inline.CB_MATCH_PREFIX}"
                ),
                CallbackQueryHandler(start.cancel_callback, pattern=f"^{inline.CB_CANCEL}$"),
            ],
            states.REG_FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register.receive_first_name),
            ],
            states.REG_FATHER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register.receive_father_name),
            ],
            states.REG_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register.receive_phone),
            ],
            states.REG_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register.receive_age),
            ],
            states.REG_EDUCATION: [
                CallbackQueryHandler(
                    register.receive_education, pattern=f"^{inline.CB_EDU_PREFIX}"
                ),
            ],
            states.REG_WAITING_FAMILY: [
                CallbackQueryHandler(
                    register.receive_waiting_family,
                    pattern=f"^({inline.CB_WF_YES}|{inline.CB_WF_NO})$",
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", start.cancel),
            CallbackQueryHandler(start.cancel_callback, pattern=f"^{inline.CB_CANCEL}$"),
            CommandHandler("start", start.start),
        ],
        name="mhss_kidds_conversation",
        allow_reentry=True,
    )


def build_application() -> Application:
    """Validate config and build the configured Application instance."""
    settings.validate()

    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(_build_conversation())
    application.add_handler(CommandHandler("help", start.help_command))

    # After a conversation ends, any unhandled message shows the main menu.
    application.add_handler(
        MessageHandler(filters.ALL, start.idle_input), group=1
    )

    application.add_error_handler(_on_error)

    return application


def run() -> None:
    """Start long-polling."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting MHSS-KIDDS bot...")
    application = build_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
