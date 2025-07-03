import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json

DATA_FILE = "reminders.json"
TOKEN = os.getenv("BOT_TOKEN")

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào! Gõ /add để thêm nhắc nhở.\nVD: /add Netflix 2025-07-10 200000")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = str(update.effective_chat.id)
        args = context.args
        name, date_str, amount = args[0], args[1], args[2]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        data = load_data()
        if chat_id not in data:
            data[chat_id] = []

        data[chat_id].append({
            "name": name,
            "date": date_str,
            "amount": amount
        })

        save_data(data)
        await update.message.reply_text(f"✅ Đã lưu nhắc nhở: {name} - {date_str} - {amount} VND")
    except:
        await update.message.reply_text("❌ Sai cú pháp! Dùng: /add <tên> <YYYY-MM-DD> <số tiền>")

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = load_data()
    reminders = data.get(chat_id, [])
    if not reminders:
        await update.message.reply_text("📭 Không có nhắc nhở nào.")
        return

    text = "📋 Danh sách nhắc nhở:\n"
    for r in reminders:
        text += f"- {r['name']} | {r['date']} | {r['amount']} VND\n"
    await update.message.reply_text(text)

async def remind_users():
    data = load_data()
    now = datetime.now()
    for chat_id, reminders in data.items():
        for r in reminders:
            due_date = datetime.strptime(r['date'], "%Y-%m-%d")
            if due_date - now <= timedelta(days=1) and due_date >= now:
                await application.bot.send_message(
                    chat_id=int(chat_id),
                    text=f"🔔 Nhắc: {r['name']} đến hạn {r['date']} ({r['amount']} VND)"
                )

scheduler = BackgroundScheduler()
application = ApplicationBuilder().token(TOKEN).build()
scheduler.add_job(lambda: application.create_task(remind_users()), 'interval', hours=24)
scheduler.start()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("list", list_reminders))

if __name__ == "__main__":
    application.run_polling()
