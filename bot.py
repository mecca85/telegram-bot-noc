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
        logger.info("Backup config.json.bak creato")
    except Exception as e:
        logger.error(f"Errore backup config: {e}")


def save_config(data):
    backup_config()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


config = load_config()

# ---------------------------------------------------------
# COMANDI BASE
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot attivo!\n"
        "Comandi disponibili:\n"
        "/id → mostra chat_id\n"
        "/setchat <id> → imposta chat_id\n"
        "/setinterval <minuti> → imposta intervallo report\n"
        "/status → mostra configurazione\n"
        "/test → invia messaggio di test\n"
        "/debug → mostra l'update ricevuto\n"
        "/report_daily → report giornaliero\n"
        "/report_periodic → report periodico\n"
        "/report_weekly → report settimanale\n"
        "/report_monthly → report mensile\n"
    )


async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")


async def backlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Backlog generato correttamente.")


async def setchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Uso corretto: /setchat <chat_id>")

    new_id = context.args[0]
    config["chat_id"] = new_id
    save_config(config)

    await update.message.reply_text(f"Chat ID aggiornato a: {new_id}")
    logger.info(f"CHAT_ID aggiornato a {new_id}")


async def setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Uso: /setinterval <minuti>")

    try:
        minutes = int(context.args[0])
    except:
        return await update.message.reply_text("Inserisci un numero valido.")

    config["interval_minutes"] = minutes
    save_config(config)

    await update.message.reply_text(f"Intervallo aggiornato a {minutes} minuti.")
    logger.info(f"INTERVALLO aggiornato a {minutes} minuti")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    interval = config.get("interval_minutes")

    msg = (
        "📊 *Stato del bot*\n\n"
        f"• Chat configurata: `{chat_id}`\n"
        f"• Intervallo report: `{interval}` minuti\n"
        f"• Webhook: `{WEBHOOK_URL}`\n"
        "• Job giornaliero: 09:00\n"
        "• Job periodico: attivo\n"
    )

    await update.message.reply_markdown(msg)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return await update.message.reply_text("Nessun chat_id configurato. Usa /setchat")

    try:
        await context.bot.send_message(chat_id=chat_id, text="Messaggio di test inviato correttamente.")
        await update.message.reply_text("Test inviato.")
    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw = update.to_dict()
        text = json.dumps(raw, indent=2, ensure_ascii=False)
        await update.message.reply_text(f"DEBUG:\n\n{text[:3500]}")
    except Exception as e:
        await update.message.reply_text(f"Errore debug: {e}")

# ---------------------------------------------------------
# REPORT COMMAND HANDLERS
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
        logger.info(f"Report giornaliero inviato a {chat_id}")
    except Exception as e:
        logger.error(f"Errore invio report giornaliero: {e}")


async def send_interval_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_periodic_report())
        logger.info(f"Report periodico inviato a {chat_id}")
    except Exception as e:
        logger.error(f"Errore invio report periodico: {e}")


async def send_weekly_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_weekly_report())
        logger.info(f"Report settimanale inviato a {chat_id}")
    except Exception as e:
        logger.error(f"Errore invio report settimanale: {e}")


async def send_monthly_report_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_monthly_report())
        logger.info(f"Report mensile inviato a {chat_id}")
    except Exception as e:
        logger.error(f"Errore invio report mensile: {e}")

# ---------------------------------------------------------
# HANDLER MESSAGGI
# ---------------------------------------------------------
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    log_message(text)

    low = text.lower()
    if "ciao" in low:
        await update.message.reply_text("Ciao! Come posso aiutarti?")
    elif "buongiorno" in low:
        await update.message.reply_text("Buongiorno! Tutto bene?")
    else:
        await update.message.reply_text("Ho ricevuto il tuo messaggio.")

# ---------------------------------------------------------
# AVVIO BOT
# ---------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Container")

    if not TOKEN:
        raise RuntimeError("BOT_TOKEN non trovato")

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL non trovato")

    app = ApplicationBuilder().token(TOKEN).build()

    # COMANDI
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("backlog", backlog))
    app.add_handler(CommandHandler("setchat", setchat))
    app.add_handler(CommandHandler("setinterval", setinterval))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("debug", debug))

    app.add_handler(CommandHandler("report_daily", report_daily_cmd))
    app.add_handler(CommandHandler("report_periodic", report_periodic_cmd))
    app.add_handler(CommandHandler("report_weekly", report_weekly_cmd))
    app.add_handler(CommandHandler("report_monthly", report_monthly_cmd))

    # MESSAGGI
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # JOBS
    app.job_queue.run_daily(
        send_daily_report_job,
        time=time(hour=9, minute=0),
        name="daily_report"
    )

    app.job_queue.run_repeating(
        send_interval_report_job,
        interval=config["interval_minutes"] * 60,
        first=10,
        name="interval_report"
    )

    app.job_queue.run_daily(
        send_weekly_report_job,
        time=time(hour=9, minute=0),
        days=(0,),  # lunedì
        name="weekly_report"
    )

    app.job_queue.run_monthly(
        send_monthly_report_job,
        when=time(hour=9, minute=0),
        day=1,
        name="monthly_report"
    )

    # WEBHOOK — PORTA 8880 (quella esposta da Railway)
    full_webhook_url = f"{WEBHOOK_URL}/{TOKEN}"

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8880)),
        url_path=TOKEN,
        webhook_url=full_webhook_url,
        allowed_updates=["message", "chat_member", "my_chat_member"]
    )
