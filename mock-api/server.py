"""Mock API that follows docs/api-contract.md, so the Rust side can work
before the real Telegram backend exists.   Run: python mock-api/server.py"""
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

CHANNELS = [("bbcpersian", "BBC Persian"), ("durov", "Durov's Channel"), ("techfeed", "Tech Feed")]
TEXTS = [
    "سلام! این یک پیام آزمایشی است.",
    "Breaking: mixed English and فارسی text in one message.",
    "",  # media-only
    "یک پیام طولانی‌تر برای تست شکستن خط و نمایش درست در پنجره.\nخط دوم پیام.",
    "Short one",
]


def make_messages(n=40):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    out = []
    for i in range(n):
        ch, title = CHANNELS[i % len(CHANNELS)]
        text = TEXTS[i % len(TEXTS)]
        out.append({
            "id": 5000 - i,
            "channel": ch,
            "sender": title,
            "text": text,
            "date": (now - timedelta(minutes=7 * i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "has_media": text == "" or i % 6 == 0,
        })
    return out


def error(status, code, message):
    return jsonify({"error": {"code": code, "message": message}}), status


@app.get("/api/messages")
def messages():
    raw = request.args.get("limit", "20")
    if not raw.isdigit() or not 1 <= int(raw) <= 100:
        return error(400, "bad_limit", "limit must be 1..100")
    msgs = make_messages()[: int(raw)]
    return jsonify({
        "version": 1,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(msgs),
        "messages": msgs,
    })


if __name__ == "__main__":
    app.run("127.0.0.1", 8000)
