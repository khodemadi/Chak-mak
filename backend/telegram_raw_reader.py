import os
import asyncio
import json
import base64
from datetime import datetime, date
from typing import Any

from telethon import TelegramClient
from telethon.tl.types import TLObject

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

client = TelegramClient("chakmak_session", API_ID, API_HASH)


def to_jsonable(value: Any) -> Any:
    """
    تبدیل داده‌های Telethon/Python به انواع قابل‌سریال‌سازی JSON:
    dict, list, str, int, float, bool یا None.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, bytes):
        return {
            "__type__": "bytes",
            "encoding": "base64",
            "data": base64.b64encode(value).decode("ascii"),
        }

    if isinstance(value, TLObject):
        return to_jsonable(value.to_dict())

    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]

    # پشتیبان برای مقادیر خاصی که تبدیل استاندارد ندارند
    return str(value)


async def get_messages(channel_object: dict, limit: int = 50) -> dict:
    """
    ورودی:
        {"username": "channel_username", "source": "telegram"}

    خروجی:
        یک dict کاملاً JSON-compatible شامل پیام‌های کانال.
        دانلود رسانه انجام نمی‌شود؛ فقط metadata و داده خام پیام جمع می‌شود.
    """

    if not isinstance(channel_object, dict):
        raise TypeError("channel_object باید dict باشد.")

    channel = channel_object.get("username")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError("channel_object باید username معتبر داشته باشد.")

    channel = channel.strip().removeprefix("@")
    limit = max(1, min(int(limit), 50))

    await client.connect()

    try:
        if not await client.is_user_authorized():
            raise RuntimeError(
                "Telegram login required. ابتدا session تلگرام را احراز هویت کنید."
            )

        entity = await client.get_entity(channel)
        messages = await client.get_messages(entity, limit=limit)

        # خروجی را از قدیمی به جدید مرتب می‌کنیم.
        messages = list(reversed(messages))
        serialized_messages = []

        for msg in messages:
            serialized_messages.append({
                "id": msg.id,
                "text": msg.message or "",
                "date": msg.date.isoformat() if msg.date else None,
                "edit_date": (
                    msg.edit_date.isoformat()
                    if msg.edit_date
                    else None
                ),
                "sender_id": msg.sender_id,
                "channel_id": getattr(entity, "id", None),
                "media_present": msg.media is not None,
                # کل آبجکت پیام Telethon به شکل JSON-compatible
                "raw": to_jsonable(msg.to_dict()),
            })

        result = {
            "channel": to_jsonable(channel_object),
            "count": len(serialized_messages),
            "messages": serialized_messages,
        }

        # بررسی نهایی: اگر این خط اجرا شود، خروجی JSON-serializable است.
        json.dumps(result, ensure_ascii=False)

        return result

    finally:
        await client.disconnect()


if __name__ == "__main__":
    channel_object = {
        "username": "bbcpersian",
        "source": "telegram",
    }

    raw_data = asyncio.run(
        get_messages(channel_object, limit=50)
    )

    # خروجی JSON مناسب برای فایل، API یا ارسال به ماژول بعدی
    json_output = json.dumps(
        raw_data,
        ensure_ascii=False,
        indent=2,
    )

    print(json_output)

    # ذخیره خروجی در فایل JSON
    with open("telegram_raw_data.json", "w", encoding="utf-8") as file:
        file.write(json_output)
