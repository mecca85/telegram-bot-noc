import os
import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Leggo le variabili d'ambiente
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print("TOKEN LETTO:", repr(TOKEN))
print("WEBHOOK_URL LETTO:", repr(WEBHOOK_URL))

# Chat dove inviare il backlog
CHAT_ID = "-1003789925325"

# Testo del backlog
BACKLOG = (
    "Backlog NOC Fastweb By Mecca\n\n"
    "Dato di aggiornamento ultimo ticket: 30/03/2026 20:46:43\n"
    "Change: 114\n"
    "TT sotto le 24 ore: 197\n"
    "Totale TT: 653\n"
    "TT da 1 a 2 gg: 7\n"
    "TT da 2 a 3 gg: 11\n"
    "TT da 3 a 4 gg: 69\n"
    "TT da 4 a 5 gg: 72\n"
    "TT da 5 a 6 gg: 48\n"
    "TT da 6 a 7 gg: 35\n"
    "Network: 97\n"
    "Priorità alta: 2\n"
    "TT da 7 a 10 gg: 37\n\n"
    "Customer: 442\n"
    "TT sopra i 30gg: 72\n"
    "TT INFRATEL: 0\n"
    "Priorità bassa: 56\n"
    "Priorità media: 54\n"
    "Priorità nulla: 525\n"
    "TT da 10 a 15 gg: 54\n"
    "TT da 15 a 30gg: 51\n"
    "TT bloccanti: 86\n"
    "Totali attesa: 592\n"
    "Priorità critica: 0\n\n"
    "Totale TT in attesa NMC: 15\n\n"
    "TT totali disservizi: 85\n"
    "Data attiv vuota: 653\n\n"
    "Mission critical: 16\n"
    "Data attiv entro 7 gg: 0\n"
    "Dati: 46\n"
    "Data attiv da 7 a 15 gg: 0\n"
    "Data attiv oltre 30 gg: 0\n"
    "TT > 3gg: 5\n"
    "TT < 3gg: 10\n\n"
    "Totale TT risposta da TIM: 94\n"
    "Disservizio SI sino a 7gg: 73\n"
    "Data attiv tra da 15 a 30 gg: 0\n"
    "Data modif entro 6 hh: 236\n"
    "NO PRES AXA: 35\n"
    "NO CMC: 4\n"
    "NO SME: 0\n"
    "In riassegnamento: 56\n"
    "Disservizio SI da 7 a 30gg: 11\n"
    "Disservizio SI sopra i 30gg: 1\n"
    "Data modif da 6 a 12 hh: 177\n"
    "Data modif da 12 a 24 hh: 44\n"
    "Data modif da 24 a 48 hh: 7\n"
    "Data modif oltre 48 hh: 189\n\n"
    "Totale TT in attesa di intervento: 27\n"
    "Non aggiornati: 1\n\n"
    "Totale TT in attesa PM: 23\n"
    "TT > 3gg: 67\n"
    "TT < 3gg: 27\n\n"
    "Richieste di riassegnamento\n"
    "NO CNA NORD: 7\n"
    "TT > 3gg: 18\n"
    "TT < 3gg: 9\n"
    "Non aggiornati: 20\n"
    "TT > 3gg: 19\n"
    "TT < 3gg: 4\n\n"
    "Proattività\n"
    "Anelli aperti: 51\n\n"
    "Totale TT verifica cliente: 191\n"
    "Non aggiornati: 6\n"
    "NO CMC NORD OVEST: 6\n"
    "TT > 3gg: 119\n"
    "TT < 3gg: 72\n"
    "Non aggiornati: 46\n\n"
    "Ticket aperti oggi: 314\n"
    "Ticket chiusi oggi: 295\n"
)

# Comando /backlog
async def backlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Comando /backlog ricevuto da:", update.effective_chat.id)
    await update.message.reply_text(BACKLOG)

# Job giornaliero
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text=BACKLOG)

# MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("backlog", backlog))

    # Job giornaliero
    app.job_queue.run_daily(
        send_daily_report,
        time=datetime.time(hour=8, minute=0),
        name="daily_report"
    )

    # Webhook
    webhook_full_url = f"{WEBHOOK_URL}/{TOKEN}"
    print("Webhook impostato su:", webhook_full_url)

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=webhook_full_url,
    )

if __name__ == "__main__":
    main()
