import os
import json
import logging
from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ---------------------------------------------------------
# LOGGING AVANZATO
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

# ---------------------------------------------------------
# STORAGE JSON
# ---------------------------------------------------------
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
    )

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

async def backlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Backlog generato correttamente.")

# ---------------------------------------------------------
# COMANDO: SETCHAT
# ---------------------------------------------------------
async def setchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Uso corretto: /setchat <chat_id>")

    new_id = context.args[0]
    config["chat_id"] = new_id
    save_config(config)

    await update.message.reply_text(f"Chat ID aggiornato a: {new_id}")
    logger.info(f"CHAT_ID aggiornato a {new_id}")

# ---------------------------------------------------------
# COMANDO: SETINTERVAL
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# COMANDO: STATUS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# COMANDO: TEST
# ---------------------------------------------------------
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return await update.message.reply_text("Nessun chat_id configurato. Usa /setchat")

    try:
        await context.bot.send_message(chat_id=chat_id, text="Messaggio di test inviato correttamente.")
        await update.message.reply_text("Test inviato.")
    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")

# ---------------------------------------------------------
# JOB: INVIO REPORT GIORNALIERO
# ---------------------------------------------------------
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return logger.warning("Nessun chat_id configurato.")

    BACKLOG = "Questo è il report giornaliero."

    try:
        await context.bot.send_message(chat_id=chat_id, text=BACKLOG)
        logger.info(f"Backlog inviato a {chat_id}")

    except Exception as e:
        logger.error(f"Errore inviando il backlog a {chat_id}: {e}")

# ---------------------------------------------------------
# JOB: INVIO OGNI X MINUTI
# ---------------------------------------------------------
async def send_interval_report(context: ContextTypes.DEFAULT_TYPE):
    chat_id = config.get("chat_id")
    if not chat_id:
        return

    BACKLOG = "Report periodico."

    try:
        await context.bot.send_message(chat_id=chat_id, text=BACKLOG)
        logger.info(f"Report periodico inviato a {chat_id}")

    except Exception as e:
        logger.error(f"Errore invio report periodico: {e}")

# ---------------------------------------------------------
# AVVIO BOT (NO ASYNCIO.RUN!)
# ---------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Container")

    if not TOKEN:
        raise RuntimeError("BOT_TOKEN non trovato")

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL non trovato")

    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLER COMANDI
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("backlog", backlog))
    app.add_handler(CommandHandler("setchat", setchat))
    app.add_handler(CommandHandler("setinterval", setinterval))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))

    # JOB GIORNALIERO
    app.job_queue.run_daily(
        send_daily_report,
        time=time(hour=9, minute=0),
        name="daily_report"
    )

    # JOB OGNI X MINUTI
    app.job_queue.run_repeating(
        send_interval_report,
        interval=config["interval_minutes"] * 60,
        first=10,
        name="interval_report"
    )

    # WEBHOOK (gestito automaticamente da PTB)
    full_webhook_url = f"{WEBHOOK_URL}/{TOKEN}"

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=full_webhook_url,
    )
