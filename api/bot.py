import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("INSTA_API_URL")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})


def send_video(chat_id, video_url):
    requests.post(f"{TELEGRAM_API}/sendVideo", json={"chat_id": chat_id, "video": video_url}, timeout=60)


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

        if text == "/start":
            send(chat_id, "👋 Welcome to Instagram Downloader Bot!\n\n"
                          "📥 Just send me any Instagram link and I'll download it for you.\n\n"
                          "Supports: Reels, Posts, Videos\n\n"
                          "Made by @umarj_1")
            self._ok()
            return

        if "instagram.com" not in text:
            send(chat_id, "⚠️ Please send a valid Instagram link.\n\nExample:\nhttps://www.instagram.com/reel/...")
            self._ok()
            return

        send(chat_id, "Downloading...")

        try:
            res = requests.get(f"{API_BASE}/igdl", params={"url": text}, timeout=30)
            data = res.json()
            items = data.get("data") or []
            video_url = items[0].get("url") if items else data.get("url")

            if not video_url:
                send(chat_id, "❌ Could not fetch the video. Make sure the link is correct and the account is public.")
            else:
                send_video(chat_id, video_url)
                send(chat_id, "✅ Downloaded!\n\nBot by @umarj_1")
        except Exception as e:
            send(chat_id, f"Error: {str(e)}")

        self._ok()

    def _ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass
