import os
from datetime import date

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

# === НАЛАШТУВАННЯ ===
MAX_YEARS = 100


def life_stats(birth: date) -> str:
    today = date.today()

    lived_days = (today - birth).days
    total_days = MAX_YEARS * 365
    left_days = total_days - lived_days

    lived_years = lived_days // 365
    lived_weeks = lived_days // 7

    percent_lived = lived_days / total_days * 100
    percent_left = 100 - percent_lived

    return (
        "📊 Станом на сьогодні:\n\n"
        f"Рік (прожив): {lived_years} — лишилось: {MAX_YEARS - lived_years}\n"
        f"Тиждень (прожив): {lived_weeks} — лишилось: {left_days // 7}\n"
        f"День (прожив): {lived_days} — лишилось: {left_days}\n\n"
        "100 років життя = 100%\n\n"
        f"Прожито: {percent_lived:.1f}%\n"
        f"Залишилось: {percent_left:.1f}%"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋\n"
        "Введи дату народження у форматі:\n"
        "ДД.ММ.РРРР\n\n"
        "Наприклад: 21.07.2005"
    )


async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        day, month, year = map(int, update.message.text.split("."))
        birth = date(year, month, day)
    except Exception:
        await update.message.reply_text("❌ Невірний формат. Спробуй ще раз.")
        return

    text = life_stats(birth)
    await update.message.reply_text(text)


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не заданий")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("date", handle_date))
    app.add_handler(CommandHandler("", handle_date))

    app.run_polling()


if __name__ == "__main__":
    main()
