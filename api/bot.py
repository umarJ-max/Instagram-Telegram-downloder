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
    requests.post(f"{TELEGRAM_API}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    })


def get_bot_photo():
    try:
        me = requests.get(f"{TELEGRAM_API}/getMe").json()
        bot_id = me["result"]["id"]
        res = requests.get(f"{TELEGRAM_API}/getUserProfilePhotos", params={"user_id": bot_id})
        photos = res.json().get("result", {}).get("photos", [])
        if not photos:
            return None
        file_id = photos[0][0]["file_id"]
        file_res = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id})
        file_path = file_res.json()["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    except Exception:
        return None


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
            bot_photo = get_bot_photo()
            caption = (
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
            if bot_photo:
                send_photo_with_caption(chat_id, bot_photo, caption)
            else:
                send(chat_id, caption)
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
                    f"<i>Enjoyed the bot? Share it with friends 🚀</i>")
        except Exception as e:
            send(chat_id, f"❌ <b>Error:</b> <code>{str(e)}</code>")

        self._ok()

    def _ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass