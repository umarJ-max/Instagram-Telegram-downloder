import os
import requests
from dotenv import load_dotenv

load_dotenv()
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("VERCEL_API_URL")  # e.g. https://your-app.vercel.app


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram link.")
        return

    msg = await update.message.reply_text("Downloading...")

    try:
        res = requests.get(f"{API_BASE}/igdl", params={"url": url}, timeout=30)
        data = res.json()

        video_url = data.get("url")
        if not video_url:
            await msg.edit_text("Could not fetch the video. Try again.")
            return

        await msg.edit_text("Sending video...")
        await update.message.reply_video(video=video_url)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")


# If Telegram is blocked, set PROXY in .env like: PROXY=socks5://user:pass@host:port
PROXY = os.getenv("PROXY")
builder = ApplicationBuilder().token(BOT_TOKEN)
if PROXY:
    builder = builder.proxy(PROXY).get_updates_proxy(PROXY)
app = builder.build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
