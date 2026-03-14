from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from flask import Flask, request

import sqlite3
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from google_sheets import append_worker_to_sheet

# Load environment variables
load_dotenv()

TOKEN = os.environ.get("KINGDOM_WORKFORCE_TOKEN")
if TOKEN is None:
    raise ValueError("Error: Bot token not found. Please set KINGDOM_WORKFORCE_TOKEN in your .env file.")

ADMINS = os.environ.get("KINGDOM_WORKFORCE_ADMINS", "")
ADMINS = [int(uid) for uid in ADMINS.split(",") if uid.strip()]

FULLNAME, PHONE, PROFESSION, EXPERIENCE = range(4)

# ================= FLASK APP =================
flask_app = Flask(__name__)

# ================= TELEGRAM APP =================
# We build the application once at module level so it's shared across requests
telegram_app = ApplicationBuilder().token(TOKEN).build()


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Welcome to Kingdom Workforce Registration\n"
        "እንኳን ወደ Kingdom Workforce መመዝገቢያ በደህና መጡ\n\n"
        "Please enter your full name / ሙሉ ስምዎን ያስገቡ:"
    )
    return FULLNAME


# ================= FULL NAME =================
async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text(
        "Enter your phone number / ስልክ ቁጥርዎን ያስገቡ: 09XXXXXXXX"
    )
    return PHONE


# ================= PHONE =================
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()

    if not (phone_number.isdigit() and len(phone_number) == 10 and phone_number.startswith("09")):
        await update.message.reply_text(
            "❌ Invalid phone number!\n"
            "Please enter correctly (Example: 09XXXXXXXX)"
        )
        return PHONE

    conn = sqlite3.connect("workers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM workers WHERE phone = ?", (phone_number,))
    existing_user = cursor.fetchone()
    conn.close()

    if existing_user:
        await update.message.reply_text(
            "⚠️ This phone number is already registered."
        )
        return ConversationHandler.END

    context.user_data["phone"] = phone_number
    await update.message.reply_text(
        "Enter your profession / የስራ ዘርፍዎትን ያስገቡ:"
    )
    return PROFESSION


# ================= PROFESSION =================
async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profession"] = update.message.text.strip()
    await update.message.reply_text(
        "How many years of experience? / የልምድ ዓመታት:"
    )
    return EXPERIENCE


# ================= EXPERIENCE =================
async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exp_text = update.message.text.strip()

    if not exp_text.isdigit():
        await update.message.reply_text(
            "Please enter a valid number for experience."
        )
        return EXPERIENCE

    experience_years = int(exp_text)
    context.user_data["experience_years"] = experience_years

    registration_date = datetime.now().strftime("%Y-%m-%d")

    # ===== SAVE TO SQLITE =====
    conn = sqlite3.connect("workers.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workers (full_name, phone, profession, experience_years, registration_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        context.user_data["full_name"],
        context.user_data["phone"],
        context.user_data["profession"],
        experience_years,
        registration_date
    ))

    worker_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # ===== SEND TO GOOGLE SHEETS =====
    try:
        append_worker_to_sheet([
            worker_id,
            context.user_data["full_name"],
            context.user_data["phone"],
            context.user_data["profession"],
            experience_years,
            registration_date
        ])
    except Exception as e:
        print("Google Sheets Error:", e)

    await update.message.reply_text(
        f"✅ Registration Successful!\n"
        f"Worker ID: {worker_id}\n\n"
        f"Thank you for joining Kingdom Workforce."
    )

    return ConversationHandler.END


# ================= EXPORT =================
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized.")
        return

    conn = sqlite3.connect("workers.db")
    df = pd.read_sql_query("SELECT * FROM workers", conn)
    conn.close()

    filename = "kingdom_workforce_workers.xlsx"
    df.to_excel(filename, index=False)

    with open(filename, "rb") as file:
        await update.message.reply_document(document=file)

    await update.message.reply_text("✅ Worker list exported successfully.")


# ================= REGISTER HANDLERS =================
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, fullname)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
        PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, profession)],
        EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
    },
    fallbacks=[]
)

telegram_app.add_handler(conv_handler)
telegram_app.add_handler(CommandHandler("export", export))


# ================= WEBHOOK ROUTES =================
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Telegram calls this URL every time a user sends a message."""
    import asyncio
    import json

    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, telegram_app.bot)

    # Run the async handler in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(telegram_app.process_update(update))
    finally:
        loop.close()

    return "OK", 200


@flask_app.route("/")
def index():
    """Health check — lets GojoHost know the app is alive."""
    return "👑 Kingdom Workforce Bot is running!", 200


# ================= ENTRY POINT =================
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))