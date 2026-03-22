import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VERCEL_URL = os.getenv("VERCEL_BOT_URL")  # e.g. https://your-bot.vercel.app

res = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    params={"url": f"{VERCEL_URL}/webhook"}
)
print(res.json())
