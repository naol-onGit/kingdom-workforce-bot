"""
Run this script ONCE after you deploy to GojoHost to register your webhook with Telegram.

Usage:
    python setup_webhook.py

Make sure your .env file has KINGDOM_WORKFORCE_TOKEN set, or set it manually below.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("KINGDOM_WORKFORCE_TOKEN")
YOUR_DOMAIN = input("Enter your GojoHost domain (e.g. https://yourdomain.com): ").strip().rstrip("/")

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={YOUR_DOMAIN}/{TOKEN}"

response = requests.get(url)
data = response.json()

if data.get("ok"):
    print("✅ Webhook set successfully!")
    print(f"   Telegram will now send updates to: {YOUR_DOMAIN}/{TOKEN}")
else:
    print("❌ Failed to set webhook:")
    print(data)

# Also print webhook info so you can verify
info_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
info = requests.get(info_url).json()
print("\n📋 Webhook Info:")
print(f"   URL: {info['result'].get('url')}")
print(f"   Pending updates: {info['result'].get('pending_update_count')}")
print(f"   Last error: {info['result'].get('last_error_message', 'None')}")