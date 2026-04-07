import os
import json
import logging
from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from reports_manager import (
    log_message,
    generate_daily_report,
    generate_periodic_report,
    generate_weekly_report,
    generate_monthly_report
)

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CONFIG_FILE = "config.json"


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {"chat_id": None, "interval_minutes": 60}


def backup_config():
    try:
        import shutil
        shutil.copy(CONFIG_FILE, CONFIG_FILE + ".bak")
        logger.info("Backup config.json.bak created")
    except Exception as e:
        logger.error(f"Backup error: {e}")


def save_config(data):
    backup_config()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


config = load_config()

# ---------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot active!\n"
        "Available commands:\n"
        "/id → show chat_id\n"
        "/setchat <id> → set chat_id\n"
        "/setinterval <minutes> → set periodic report interval\n"
        "/status → show configuration\n"
        "/test → send test message\n"
        "/debug → show raw update\n"
        "/report_daily → daily report\n"
        "/report_periodic → periodic report\n"
        "/report_weekly → weekly report\n"
        "/report_monthly → monthly report\n"
    )


async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")


async def setchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /setchat <chat_id>")

    new_id = context.args[0]
    config["chat_id"] = new_id
    save_config(config)

    await update.message.reply_text(f"Chat ID updated to: {new_id}")
    logger.info(f"CHAT_ID updated to {new_id}")


async def setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /setinterval <minutes>")

    try:
        minutes = int(context.args[0])
    except:
        return await update.message.reply_text("Please enter a valid number.")

    config["interval_minutes"] = minutes
    save_config(config)

    await update.message.reply_text(f"Interval updated to {minutes} minutes.")
    logger.info(f"INTERVAL updated to {minutes} minutes")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    interval = config.get("interval_minutes")

    msg = (
        "📊 *Bot Status*\n\n"
        f"• Chat configured: `{chat_id}`\n"
        f"• Interval report: `{interval}` minutes\n"
        f"• Webhook: `{WEBHOOK_URL}`\n"
        "• Daily job: 09:00\n"
        "• Weekly job: Monday 09:00\n"
    )

    await update.message.reply_markdown(msg)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return await update.message.reply_text("No chat_id configured. Use /setchat")

    try:
        await context.bot.send_message(chat_id=chat_id, text="Test message sent successfully.")
        await update.message.reply_text("Test sent.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw = update.to_dict()
        text = json.dumps(raw, indent=2, ensure_ascii=False)
        await update.message.reply_text(f"DEBUG:\n\n{text[:3500]}")
    except Exception as e:
        await update.message.reply_text(f"Debug error: {e}")

# ---------------------------------------------------------
# REPORT COMMANDS
# ---------------------------------------------------------
async def report_daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_daily_report())


async def report_periodic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_periodic_report())


async def report_weekly_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_weekly_report())


async def report_monthly_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_monthly_report())

# ---------------------------------------------------------
# JOBS
# ---------------------------------------------------------
async def send_daily_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_daily_report())
    except Exception as e:
        logger.error(f"Daily report error: {e}")


async def send_interval_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_periodic_report())
    except Exception as e:
        logger.error(f"Periodic report error: {e}")


async def send_weekly_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_weekly_report())
    except Exception as e:
        logger.error(f"Weekly report error: {e}")


async def send_monthly_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_monthly_report())
    except Exception as e:
        logger.error(f"Monthly report error: {e}")

# ---------------------------------------------------------
# MESSAGE HANDLER
# ---------------------------------------------------------
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    log_message(text)

    low = text.lower()
    if "hello" in low:
        await update.message.reply_text("Hello! How can I help?")
    elif "good morning" in low:
        await update.message.reply_text("Good morning!")
