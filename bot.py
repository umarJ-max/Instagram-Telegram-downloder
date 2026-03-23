import os
import requests
from dotenv import load_dotenv

load_dotenv()
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("VERCEL_API_URL")  # e.g. https://your-app.vercel.app


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == "/start":
        first_name = update.message.from_user.first_name
        welcome_message = (
            f"╔══════════════════╗\n"
            f"   🎬 <b>Insta Downloader</b>\n"
            f"╚══════════════════╝\n\n"
            f"👋 Hey <b>{first_name}</b>, welcome!\n\n"
            f"📲 Send me any <b>Instagram</b> link and I'll\n"
            f"fetch the video for you instantly.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅  Reels  •  Posts  •  Videos\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 Just paste the link below ↓\n\n"
            f"<i>Made with ❤️ by <a href='https://t.me/umarj_1'>@umarj_1</a></i>"
        )
        
        # Get bot's profile picture and send with caption
        try:
            bot_info = await context.bot.get_me()
            bot_profile_photos = await context.bot.get_user_profile_photos(user_id=bot_info.id, limit=1)
            if bot_profile_photos.photos:
                # Get the highest resolution photo
                photo_file = bot_profile_photos.photos[0][-1]
                await update.message.reply_photo(photo=photo_file, caption=welcome_message, parse_mode="HTML")
            else:
                # Fallback to text message if no profile picture
                await update.message.reply_text(welcome_message, parse_mode="HTML")
        except:
            # Fallback to text message if error
            await update.message.reply_text(welcome_message, parse_mode="HTML")
        return

    url = text

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
