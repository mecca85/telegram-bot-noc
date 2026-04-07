import os
import json
import csv
from datetime import datetime, timedelta

REPORT_DIR = "reports"

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

LOG_FILE = "messages.log"

def log_message(text):
    """Registra ogni messaggio ricevuto dal bot."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {text}\n")

def load_messages(days=1):
    """Carica i messaggi degli ultimi X giorni."""
    if not os.path.exists(LOG_FILE):
        return []

    cutoff = datetime.now() - timedelta(days=days)
    messages = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                timestamp, text = line.split(" | ", 1)
                ts = datetime.fromisoformat(timestamp)
                if ts >= cutoff:
                    messages.append((ts, text.strip()))
            except:
                pass

    return messages

# ---------------------------------------------------------
# REPORT GIORNALIERO
# ---------------------------------------------------------
def generate_daily_report():
    msgs = load_messages(days=1)
    total = len(msgs)
    last5 = msgs[-5:]

    report = "📊 REPORT GIORNALIERO\n\n"
    report += f"• Messaggi ricevuti: {total}\n"
    report += f"• Ultimo update: {msgs[-1][0] if msgs else 'N/A'}\n\n"
    report += "Ultimi 5 messaggi:\n"

    for ts, msg in last5:
        report += f"- {msg}\n"

    return report

# ---------------------------------------------------------
# REPORT PERIODICO
# ---------------------------------------------------------
def generate_periodic_report():
    msgs = load_messages(days=1)
    total = len(msgs)

    report = "⏱ REPORT PERIODICO\n\n"
    report += f"• Messaggi oggi: {total}\n"
    report += f"• Ultimo messaggio: {msgs[-1][0] if msgs else 'N/A'}\n"

    return report

# ---------------------------------------------------------
# REPORT SETTIMANALE
# ---------------------------------------------------------
def generate_weekly_report():
    msgs = load_messages(days=7)

    per_day = {}
    for ts, msg in msgs:
        day = ts.strftime("%a")
        per_day[day] = per_day.get(day, 0) + 1

    report = "📅 REPORT SETTIMANALE\n\n"
    for day, count in per_day.items():
        bar = "█" * (count // 5)
        report += f"{day}: {bar} {count}\n"

    return report

# ---------------------------------------------------------
# REPORT MENSILE + CSV
# ---------------------------------------------------------
def generate_monthly_report():
    msgs = load_messages(days=30)

    total = len(msgs)
    avg = total // 30

    report = "📆 REPORT MENSILE\n\n"
    report += f"• Messaggi totali: {total}\n"
    report += f"• Media giornaliera: {avg}\n"

    # CSV
    csv_path = os.path.join(REPORT_DIR, f"{datetime.now().strftime('%Y-%m')}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "message"])
        for ts, msg in msgs:
            writer.writerow([ts.isoformat(), msg])

    report += f"\nCSV generato: {csv_path}"

    return report
