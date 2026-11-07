import os
import asyncio
from telethon import TelegramClient

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

client = TelegramClient(
    "chakmak_session",
    API_ID,
    API_HASH,
)


async def get_messages(channel: str, limit: int = 50):
    await client.connect()

    try:
        if not await client.is_user_authorized():
            raise RuntimeError("Telegram login required")

        messages = await client.get_messages(
            channel,
            limit=min(limit, 50),
        )

        results = []

        for msg in reversed(messages):
            media_type = "text"

            if msg.voice:
                media_type = "voice"

            elif msg.video_note:
                media_type = "round_video"

            elif msg.video:
                media_type = "video"

            elif msg.photo:
                media_type = "photo"

            elif msg.audio:
                media_type = "audio"

            elif msg.gif:
                media_type = "animation"

            elif msg.sticker:
                media_type = "sticker"

            elif msg.poll:
                media_type = "poll"

            elif msg.geo:
                media_type = "location"

            elif msg.contact:
                media_type = "contact"

            elif msg.game:
                media_type = "game"

            elif msg.document:
                mime_type = msg.document.mime_type or ""

                if mime_type == "application/pdf":
                    media_type = "pdf"

                elif mime_type.startswith("video/"):
                    media_type = "video"

                elif mime_type.startswith("audio/"):
                    media_type = "audio"

                elif mime_type.startswith("image/"):
                    media_type = "image"

                else:
                    media_type = "document"

            elif msg.message:
                media_type = "text"

            else:
                media_type = "unknown"

            results.append({
                "id": msg.id,
                "text": msg.message or "",
                "media_type": media_type,
                "date": msg.date.isoformat() if msg.date else None,
            })

        return results

    finally:
        await client.disconnect()


if __name__ == "main":
    channel = input("Enter Telegram channel: ")

    messages = asyncio.run(
        get_messages(channel)
    )

    for message in messages:
        print(message)