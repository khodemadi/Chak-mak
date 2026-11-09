# Chakmak Cache Module

Temporary disk cache for Telegram media, managed through a central `CacheManager`.

## Runtime storage layout

```text
storage/
├── cache/
│   ├── telegram/
│   │   ├── video/
│   │   ├── voice/
│   │   ├── audio/
│   │   ├── document/
│   │   ├── image/
│   │   └── other/
│   └── temporary/
└── database/
    └── cache.db
```

Keep permanent user downloads outside `storage/cache`.

## Basic usage

```python
from cash.manager import CacheManager
from cash.cleaner import CacheCleaner

cache = CacheManager()
cleaner = CacheCleaner(cache)

async def start_media_services():
    await cleaner.start()

async def save_download(file_id, downloaded_path, category="video"):
    cached = await cache.get(file_id)
    if cached:
        return cached
    return await cache.save(file_id, downloaded_path, category)

async def use_media(file_id):
    async with cache.use(file_id) as path:
        print("Use or stream:", path)
```

Call `cleaner.start()` once at application startup and `await cleaner.stop()` during shutdown.

This implementation uses Python's standard library only. Its locks protect a single Python process; multi-process deployments need inter-process locking. Before production, add crash-recovery/reconciliation, project logging, tests, and disk-space checks.
