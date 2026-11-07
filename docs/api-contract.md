# قرارداد API — Chak Mak (v1)

نفر Python این را پیاده می‌کند، نفر Rust مصرف می‌کند.
هر تغییری در این فایل باید با هر دو نفر هماهنگ شود.

## درخواست

    GET /api/messages?limit=20

- `limit`: عدد صحیح ۱ تا ۱۰۰، پیش‌فرض ۲۰
- ترتیب خروجی: **جدیدترین اول**

## پاسخ موفق (HTTP 200)

```json
{
  "version": 1,
  "fetched_at": "2026-11-06T10:00:00Z",
  "count": 2,
  "messages": [
    {
      "id": 4821,
      "channel": "bbcpersian",
      "sender": "BBC Persian",
      "text": "متن پیام",
      "date": "2026-11-06T09:58:12Z",
      "has_media": false
    },
    {
      "id": 4820,
      "channel": "durov",
      "sender": "Durov's Channel",
      "text": "",
      "date": "2026-11-06T09:40:00Z",
      "has_media": true
    }
  ]
}
```

## فیلدها

| فیلد | نوع | توضیح |
|---|---|---|
| `version` | int | همیشه `1`. کلاینت اگر چیز دیگری دید خطا می‌دهد |
| `fetched_at` | string | زمان ساخت پاسخ، ISO 8601 به UTC با پسوند `Z` |
| `count` | int | برابر طول `messages` |
| `id` | int | شناسه پیام در همان کانال (یکتا فقط همراه `channel`) |
| `channel` | string | یوزرنیم کانال بدون `@` |
| `sender` | string | **هیچ‌وقت null نیست.** نام نویسنده؛ اگر پست کانال بدون نویسنده بود، عنوان کانال |
| `text` | string | ممکن است خالی باشد (پیام فقط مدیا). هیچ‌وقت null نیست |
| `date` | string | زمان ارسال، ISO 8601 به UTC (`YYYY-MM-DDTHH:MM:SSZ`) |
| `has_media` | bool | عکس/ویدیو/فایل دارد یا نه (در v1 خود مدیا ارسال نمی‌شود) |

## قواعد

- کدگذاری UTF-8؛ متن خام است (HTML نیست). کلاینت باید با `textContent` نمایش دهد.
- فیلد اضافه مجاز است و کلاینت نادیده‌اش می‌گیرد. حذف یا تغییر نوع فیلد = نسخه جدید.
- اگر پیامی نبود: `"messages": []` و `count: 0` (نه خطا).

## خطا

```json
{ "error": { "code": "bad_limit", "message": "limit must be 1..100" } }
```

| وضعیت | `code` | معنی |
|---|---|---|
| 400 | `bad_limit` | limit نامعتبر |
| 502 | `telegram_unavailable` | اتصال به تلگرام ناموفق |
| 500 | `internal` | خطای غیرمنتظره |
