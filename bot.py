import os
from datetime import datetime, date, time, timedelta, timezone

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")  # токен береться з середовища

KYIV_TZ = timezone(timedelta(hours=2))  # Київ (UTC+2)
TOTAL_YEARS = 100
TOTAL_DAYS = TOTAL_YEARS * 365 + 25


def life_stats(birth_date: date, today: date):
    lived_days = (today - birth_date).days
    left_days = max(TOTAL_DAYS - lived_days, 0)

    return {
        "years_lived": lived_days // 365,
        "years_left": TOTAL_YEARS - (lived_days // 365),
        "weeks_lived": lived_days // 7,
        "weeks_left": left_days // 7,
        "days_lived": lived_days,
        "days_left": left_days,
        "percent_lived": round(lived_days / TOTAL_DAYS * 100, 1),
        "percent_left": round(100 - (lived_days / TOTAL_DAYS * 100), 1),
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋\n"
        "Введи дату народження у форматі:\n"
        "ДД.ММ.РРРР"
    )


async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        birth_date = datetime.strptime(update.message.text, "%d.%m.%Y").date()
    except ValueError:
        await update.message.reply_text("❌ Формат: ДД.ММ.РРРР")
        return

    context.user_data["birth_date"] = birth_date
    context.user_data["last_week_sent"] = None

    today = datetime.now(KYIV_TZ).date()
    stats = life_stats(birth_date, today)

    text = (
        "📊 **Станом на сьогодні:**\n\n"
        f"Рік (прожив) — {stats['years_lived']} · лишилось — {stats['years_left']}\n"
        f"Неділя (прожив) — {stats['weeks_lived']} · лишилось — {stats['weeks_left']}\n"
        f"День (прожив) — {stats['days_lived']} · лишилось — {stats['days_left']}\n\n"
        "100 років життя = 100%\n\n"
        f"Прожито: **{stats['percent_lived']}%**\n"
        f"Залишилось: **{stats['percent_left']}%**"
    )

    await update.message.reply_text(text)


async def weekly_check(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(KYIV_TZ).date()

    for user_id, data in context.application.user_data.items():
        birth_date = data.get("birth_date")
        if not birth_date:
            continue

        lived_days = (today - birth_date).days
        if lived_days % 7 != 0:
            continue

        if data.get("last_week_sent") == lived_days:
            continue

        stats = life_stats(birth_date, today)

        text = (
            "🕰 **Твій життєвий тиждень**\n\n"
            f"Прожито тижнів: **{stats['weeks_lived']}**\n\n"
            f"Прожито: **{stats['percent_lived']}%**"
        )

        await context.bot.send_message(chat_id=user_id, text=text)
        data["last_week_sent"] = lived_days


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не заданий")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date))

    app.job_queue.run_daily(
        weekly_check,
        time=time(10, 0, tzinfo=KYIV_TZ),
    )

    print("Бот запущений...")
    app.run_polling()


if __name__ == "__main__":
    main()
