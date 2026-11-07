# The Feed — روز اول (Rust / Tauri)

## ساختار

    docs/api-contract.md   قرارداد JSON (مرجع مشترک دو نفر)
    mock-api/server.py     API آزمایشی طبق قرارداد (تا بک‌اند واقعی آماده شود)
    mock-api/validate.py   بررسی خودکار هر API با قرارداد
    src-tauri/             پروژه Rust/Tauri v2 (دریافت از API با reqwest)
    ui/                    صفحه نمایش پیام‌ها (HTML/CSS/JS ساده، بدون bundler)

## اجرا

پیش‌نیاز: Rust و پیش‌نیازهای سیستمی Tauri v2 (https://v2.tauri.app/start/prerequisites/)

    pip install flask
    python mock-api/server.py                 # ترمینال ۱: API آزمایشی روی :8000

    cargo install tauri-cli --version "^2"    # یک‌بار
    cd src-tauri
    cargo tauri icon path/to/any-square.png   # یک‌بار؛ آیکن‌ها را می‌سازد (ویندوز بدون icon.ico بیلد نمی‌شود)
    cargo tauri dev                           # ترمینال ۲

API واقعی: `THEFEED_API=http://host:port cargo tauri dev`

## تست

    cd src-tauri && cargo test                # پارس نمونه قرارداد
    python mock-api/validate.py http://127.0.0.1:8000   # نفر Python با API واقعی خودش اجرا کند
