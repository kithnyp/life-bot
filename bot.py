import os
import logging
from datetime import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =====================
# ЛОГИ
# =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =====================
# ТОКЕН
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# =====================
# КОМАНДИ
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот запущений і працює!")

# =====================
# ЩОДЕННЕ ЗАВДАННЯ
# =====================
async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("✅ Daily job executed")

# =====================
# MAIN
# =====================
def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # handlers
    app.add_handler(CommandHandler("start", start))

    # JobQueue (ПРАВИЛЬНО)
    app.job_queue.run_daily(
        daily_job,
        time=time(hour=10, minute=0)  # 10:00 UTC
    )

    logger.info("🚀 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
