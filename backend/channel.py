#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from dataclasses import dataclass


USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{5,32}$")


@dataclass
class ChannelInput:
    username: str
    source: str = "telegram"


def get_channel_input() -> ChannelInput:
    """دریافت و اعتبارسنجی آیدی کانال؛ بدون جستجو یا پردازش اضافی."""
    while True:
        try:
            raw = input("اسم یا آیدی کانال تلگرام را وارد کنید: ").strip()
        except (KeyboardInterrupt, EOFError):
            raise SystemExit("\nبرنامه متوقف شد.")

        if raw.lower() in {"exit", "quit", "q", "خروج"}:
            raise SystemExit("خروج از برنامه.")

        if not raw:
            print("ورودی خالی است.")
            continue

        # حذف @ ابتدای ورودی
        username = raw.removeprefix("@").strip()

        if not USERNAME_RE.fullmatch(username):
            print("آیدی معتبر نیست. فقط حروف انگلیسی، اعداد و آندرلاین (_) مجاز هستند.")
            continue

        return ChannelInput(username=username.lower())


if __name__ == "__main__":
    channel = get_channel_input()

    # Object آماده برای ارسال به ماژول‌های بعدی
    channel_object = {
        "username": channel.username,
        "source": channel.source,
    }

    print(channel_object)
