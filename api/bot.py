import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("INSTA_API_URL")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def send_video(chat_id, video_url):
    requests.post(f"{TELEGRAM_API}/sendVideo", json={"chat_id": chat_id, "video": video_url}, timeout=60)


def send_photo_with_caption(chat_id, photo_url, caption):
    requests.post(f"{TELEGRAM_API}/sendPhoto", json={"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}, timeout=60)


def get_bot_profile_pic():
    try:
        # Get bot's own profile photos using the bot's user ID
        bot_user_id = BOT_TOKEN.split(":")[0]
        response = requests.post(f"{TELEGRAM_API}/getUserProfilePhotos", json={"user_id": bot_user_id}, timeout=5)
        data = response.json()
        if data.get("ok") and data.get("result", {}).get("photos"):
            photos = data["result"]["photos"]
            if photos and photos[0]:
                # Get the highest resolution photo
                file_id = photos[0][-1]["file_id"]
                file_info = requests.post(f"{TELEGRAM_API}/getFile", json={"file_id": file_id}, timeout=5).json()
                if file_info.get("ok"):
                    file_path = file_info["result"]["file_path"]
                    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    except Exception as e:
        print(f"Error getting bot profile pic: {e}")
    return None


def send_profile_pic_with_welcome(chat_id, welcome_message):
    # Try to get and send profile picture with caption
    try:
        bot_profile_pic = get_bot_profile_pic()
        if bot_profile_pic:
            send_photo_with_caption(chat_id, bot_profile_pic, welcome_message)
        else:
            send(chat_id, welcome_message)
    except:
        # Fallback to text message if anything fails
        send(chat_id, welcome_message)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not chat_id or not text:
            self._ok()
            return

        first_name = message.get("from", {}).get("first_name", "there")

        if text == "/start":
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
            
            # Send profile picture with welcome message as caption
            try:
                # Get bot's profile picture
                bot_info = requests.post(f"{TELEGRAM_API}/getMe").json()
                if bot_info.get("ok"):
                    bot_user_id = bot_info["result"]["id"]
                    profile_photos = requests.post(f"{TELEGRAM_API}/getUserProfilePhotos", json={"user_id": bot_user_id, "limit": 1}).json()
                    if profile_photos.get("ok") and profile_photos.get("result", {}).get("photos"):
                        file_id = profile_photos["result"]["photos"][0][0]["file_id"]
                        # Send photo with caption
                        requests.post(f"{TELEGRAM_API}/sendPhoto", json={
                            "chat_id": chat_id, 
                            "photo": file_id, 
                            "caption": welcome_message,
                            "parse_mode": "HTML"
                        }, timeout=10)
                    else:
                        # No profile picture found, send text message
                        send(chat_id, welcome_message)
                else:
                    send(chat_id, welcome_message)
            except:
                # Fallback to text message if anything fails
                send(chat_id, welcome_message)
            
            self._ok()
            return

        if "instagram.com" not in text:
            send(chat_id,
                 f"⚠️ <b>Invalid Link!</b>\n\n"
                 f"Please send a valid Instagram link.\n\n"
                 f"<i>Example:</i>\n"
                 f"<code>https://www.instagram.com/reel/...</code>")
            self._ok()
            return

        send(chat_id, "⏳ <b>Downloading your video...</b>\nPlease wait a moment!")

        try:
            res = requests.get(f"{API_BASE}/igdl", params={"url": text}, timeout=30)
            data = res.json()
            items = data.get("data") or []
            video_url = items[0].get("url") if items else data.get("url")

            if not video_url:
                send(chat_id,
                     "❌ <b>Download Failed!</b>\n\n"
                     "Couldn't fetch the video. Make sure:\n"
                     "• The link is correct\n"
                     "• The account is <b>public</b>\n"
                     "• The post still exists")
            else:
                send_video(chat_id, video_url)
                send(chat_id,
                     f"✅ <b>Here's your video, {first_name}!</b>\n\n"
                     f"<i>Enjoyed the bot? Share it with friends 🚀</i>\n"
                     f"<i>Made by <a href='https://t.me/umarj_1'>@umarj_1</a></i>")
        except Exception as e:
            send(chat_id, f"❌ <b>Error:</b> <code>{str(e)}</code>")

        self._ok()

    def _ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass