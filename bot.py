import os
import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print("TOKEN LETTO:", repr(TOKEN))
print("WEBHOOK_URL LETTO:", repr(WEBHOOK_URL))

CHAT_ID = "-1003789925325"

BACKLOG = """Backlog NOC Fastweb By Mecca  

Dato di aggiornamento ultimo ticket: 30/03/2026 20:46:43
Change: 114
TT sotto le 24 ore: 197
Totale TT: 653
TT da 1 a 2 gg: 7
TT da 2 a 3 gg: 11
TT da 3 a 4 gg: 69
TT da 4 a 5 gg: 72
TT da 5 a 6 gg: 48
TT da 6 a 7 gg: 35
Network: 97
Priorità alta: 2
TT da 7 a 10 gg: 37

Customer: 442
TT sopra i 30gg: 72
TT INFRATEL: 0
Priorità bassa: 56
Priorità media: 54
Priorità nulla: 525
TT da 10 a 15 gg: 54
TT da 15 a 30gg: 51
TT bloccanti: 86
Totali attesa: 592
Priorità critica: 0

Totale TT in attesa NMC: 15

TT totali disservizi: 85
Data attiv vuota: 653

Mission critical: 16
Data attiv entro 7 gg: 0
Dati: 46
Data attiv da 7 a 15 gg: 0
Data attiv oltre 30 gg: 0
TT > 3gg: 5
TT < 3gg: 10

Totale TT risposta da TIM: 94
Disservizio SI sino a 7gg: 73
Data attiv tra da 15 a 30 gg: 0
Data modif entro 6 hh: 236
NO PRES AXA: 35
NO CMC: 4
NO SME: 0
In riassegnamento: 56
Disservizio SI da 7 a 30gg: 11
Disservizio SI sopra i 30gg: 1
Data modif da 6 a 12 hh: 177
Data modif da 12 a 24 hh: 44
Data modif da 24 a 48 hh: 7
Data modif oltre 48 hh: 189

Totale TT in attesa di intervento: 27
Non aggiornati: 1

Totale TT in attesa PM: 23
TT > 3gg: 67
TT < 3gg: 27

Richieste di riassegnamento
NO CNA NORD: 7
TT > 3gg: 18
TT < 3gg: 9
Non aggiornati: 20
TT > 3gg: 19
TT < 3gg: 4

Proattività
Anelli aperti: 51

Totale TT verifica cliente: 191
Non aggiornati: 6
NO CMC NORD OVEST: 6
TT > 3gg: 119
TT < 3gg: 72
Non aggiornati: 46

Ticket aperti oggi: 314
Ticket chiusi oggi: 295
"""

async def backlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(BACKLOG)

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text=BACKLOG)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("backlog", backlog))

    app.job_queue.run_daily(
        send_daily_report,
        time=datetime.time(hour=8, minute=0),
        name="daily_report"
    )

    await app.initialize()
    await app.start()

    await app.bot.set_webhook(WEBHOOK_URL)
    print("Webhook impostato su:", WEBHOOK_URL)

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path="",
        webhook_url=WEBHOOK_URL,
    )

    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
