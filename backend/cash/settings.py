from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STORAGE_DIR = PROJECT_ROOT / "storage"
CACHE_DIR = STORAGE_DIR / "cache"
TEMP_DIR = CACHE_DIR / "temporary"
DATABASE_DIR = STORAGE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "cache.db"

CACHE_CONFIG = {
    "enabled": True,
    "max_size": 20 * 1024**3,
    "max_file_size": 10 * 1024**3,
    "ttl": 7 * 24 * 60 * 60,
    "cleanup_interval": 30 * 60,
}
