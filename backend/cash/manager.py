import asyncio
import hashlib
import os
import time
import uuid
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from .settings import CACHE_DIR, TEMP_DIR, DATABASE_DIR, DATABASE_PATH, CACHE_CONFIG
from .storage import CacheStorage


class CacheManager:
    """Temporary disk cache. Keep permanent user downloads outside this cache."""

    def __init__(self):
        self.config = CACHE_CONFIG
        self.cache_dir = CACHE_DIR / "telegram"
        self.temp_dir = TEMP_DIR

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)

        self.storage = CacheStorage(self.cache_dir)
        self._lock = asyncio.Lock()
        self._active = {}
        self._initialize_database()

    def _connect(self):
        db = sqlite3.connect(DATABASE_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    def _initialize_database(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS cache_files (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    category TEXT NOT NULL,
                    path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_access REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expiration
                ON cache_files(expires_at)
            """)

    @staticmethod
    def _key(file_id):
        return hashlib.sha256(file_id.encode("utf-8")).hexdigest()

    async def get(self, file_id):
        async with self._lock:
            with self._connect() as db:
                row = db.execute(
                    "SELECT * FROM cache_files WHERE file_id = ?", (file_id,)
                ).fetchone()

                if row is None:
                    return None

                path = Path(row["path"])
                if not path.is_file():
                    db.execute("DELETE FROM cache_files WHERE file_id = ?", (file_id,))
                    return None

                if row["expires_at"] <= time.time():
                    if self._active.get(file_id, 0):
                        return None
                    path.unlink(missing_ok=True)
                    db.execute("DELETE FROM cache_files WHERE file_id = ?", (file_id,))
                    return None

                db.execute(
                    "UPDATE cache_files SET last_access = ? WHERE file_id = ?",
                    (time.time(), file_id),
                )
                return path

    async def save(self, file_id, source_path, category="other"):
        if not self.config["enabled"]:
            raise RuntimeError("Cache is disabled")

        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(source)

        size = source.stat().st_size
        if size > self.config["max_file_size"]:
            raise ValueError("File exceeds maximum cache file size")

        filename = f"{self._key(file_id)}{source.suffix[:20]}"
        destination = self.storage.get_path(category, filename)
        temporary = self.temp_dir / f"{uuid.uuid4().hex}.part"

        async with self._lock:
            if self._active.get(file_id, 0):
                raise RuntimeError("Cannot replace an active cache file")

            await self._ensure_space(size, exclude_file_id=file_id)

            try:
                await self.storage.copy(source, temporary)
                if temporary.stat().st_size != size:
                    raise IOError("Incomplete cache copy")

                os.replace(temporary, destination)
                now = time.time()

                with self._connect() as db:
                    db.execute("""
                        INSERT OR REPLACE INTO cache_files
                        (file_id, filename, category, path, size,
                         created_at, last_access, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id, filename, category, str(destination),
                        size, now, now, now + self.config["ttl"],
                    ))
                return destination
            finally:
                temporary.unlink(missing_ok=True)

    async def _ensure_space(self, required_size, exclude_file_id=None):
        maximum = self.config["max_size"]
        if required_size > maximum:
            raise ValueError("File exceeds total cache capacity")

        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM cache_files ORDER BY last_access ASC"
            ).fetchall()

        total = sum(row["size"] for row in rows)

        for row in rows:
            if total + required_size <= maximum:
                break

            file_id = row["file_id"]
            if file_id == exclude_file_id or self._active.get(file_id, 0):
                continue

            Path(row["path"]).unlink(missing_ok=True)
            with self._connect() as db:
                db.execute("DELETE FROM cache_files WHERE file_id = ?", (file_id,))
            total -= row["size"]

        if total + required_size > maximum:
            raise OSError("Not enough cache space; files may be in use")

    async def delete(self, file_id):
        async with self._lock:
            if self._active.get(file_id, 0):
                return False

            with self._connect() as db:
                row = db.execute(
                    "SELECT path FROM cache_files WHERE file_id = ?", (file_id,)
                ).fetchone()
                if row is None:
                    return False
                Path(row["path"]).unlink(missing_ok=True)
                db.execute("DELETE FROM cache_files WHERE file_id = ?", (file_id,))
                return True

    @asynccontextmanager
    async def use(self, file_id):
        path = await self.get(file_id)
        if path is None:
            raise FileNotFoundError(f"Cache entry not found: {file_id}")

        async with self._lock:
            self._active[file_id] = self._active.get(file_id, 0) + 1

        try:
            yield path
        finally:
            async with self._lock:
                count = self._active.get(file_id, 0) - 1
                if count <= 0:
                    self._active.pop(file_id, None)
                else:
                    self._active[file_id] = count

    async def cleanup(self):
        async with self._lock:
            now = time.time()
            with self._connect() as db:
                rows = db.execute(
                    "SELECT file_id, path FROM cache_files WHERE expires_at <= ?",
                    (now,),
                ).fetchall()

                for row in rows:
                    if self._active.get(row["file_id"], 0):
                        continue
                    Path(row["path"]).unlink(missing_ok=True)
                    db.execute(
                        "DELETE FROM cache_files WHERE file_id = ?",
                        (row["file_id"],),
                    )

            cutoff = now - 24 * 60 * 60
            for item in self.temp_dir.iterdir():
                try:
                    if item.is_file() and item.stat().st_mtime < cutoff:
                        item.unlink(missing_ok=True)
                except OSError:
                    pass

    async def statistics(self):
        with self._connect() as db:
            row = db.execute("""
                SELECT COUNT(*) AS total_files,
                       COALESCE(SUM(size), 0) AS total_size
                FROM cache_files
            """).fetchone()

        used = row["total_size"]
        maximum = self.config["max_size"]
        return {
            "total_files": row["total_files"],
            "total_size_bytes": used,
            "max_size_bytes": maximum,
            "available_size_bytes": max(0, maximum - used),
        }

    async def run_cleanup(self):
        while True:
            try:
                await self.cleanup()
            except asyncio.CancelledError:
                raise
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Cache cleanup failed")
            await asyncio.sleep(self.config["cleanup_interval"])
