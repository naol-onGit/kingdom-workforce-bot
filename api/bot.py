import asyncio
import json

from telegram import Update
from bot import telegram_app, TOKEN


def handler(request):
    """Vercel serverless handler for Telegram updates."""
    if request.method not in ("POST", "GET"):
        return {
            "statusCode": 405,
            "body": "Method Not Allowed",
        }

    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": "Kingdom Workforce Bot is running.",
        }

    # POST: Telegram webhook payload
    try:
        payload = request.get_json(force=True)
    except Exception:
        return {
            "statusCode": 400,
            "body": "Bad Request: invalid JSON",
        }

    # Optional token path validation
    token_from_path = request.path.replace("/api/bot/", "").strip("/")
    if token_from_path and token_from_path != TOKEN:
        return {
            "statusCode": 403,
            "body": "Forbidden: token mismatch",
        }

    update = Update.de_json(payload, telegram_app.bot)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(telegram_app.process_update(update))
    finally:
        loop.close()

    return {
        "statusCode": 200,
        "body": "OK",
    }
