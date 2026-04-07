import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Chat dove inviare il backlog (AGGIORNALO con /id)
CHAT_ID = "-1003789925325"

# ---------------------------------------------------------
# COMANDI BASE
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot attivo! Usa /id per ottenere il chat_id.")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"CHAT ID RICHIESTO: {chat_id}")
    await update.message.reply_text(f"Chat ID: {chat_id}")

async def backlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Backlog generato correttamente.")

# ---------------------------------------------------------
# JOB: INVIO REPORT GIORNALIERO
# ---------------------------------------------------------
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    BACKLOG = "Questo è il report giornaliero."

    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=BACKLOG)
        logger.info(f"Backlog inviato a {CHAT_ID}")

    except Exception as e:
        logger.error(f"Errore inviando il backlog a {CHAT_ID}: {e}")

        # Gestione specifica
        if "Forbidden" in str(e):
            logger.error("Il bot è stato rimosso dalla chat.")
        if "Chat not found" in str(e):
            logger.error("Chat ID non valido o gruppo inesistente.")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
async def main():
    logger.info("Starting Container")

    if not TOKEN:
        raise RuntimeError("BOT_TOKEN non trovato nelle variabili d'ambiente")

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL non trovato nelle variabili d'ambiente")

    logger.info(f"WEBHOOK_URL LETTO: '{WEBHOOK_URL}'")
    logger.info(f"TOKEN LETTO: '{TOKEN}'")

    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLER COMANDI
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("backlog", backlog))

    # JOB GIORNALIERO (esempio: ogni giorno alle 09:00)
    app.job_queue.run_daily(send_daily_report, time=9*3600)

    # WEBHOOK
    webhook_path = f"/{TOKEN}"
    full_webhook_url = f"{WEBHOOK_URL}/{TOKEN}"

    logger.info(f"Webhook impostato su: {full_webhook_url}")

    await app.bot.set_webhook(url=full_webhook_url)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=full_webhook_url,
    )

# ---------------------------------------------------------
# AVVIO
# ---------------------------------------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
