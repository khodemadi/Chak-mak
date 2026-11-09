import asyncio
import shutil
from pathlib import Path


class CacheStorage:
    CATEGORIES = {"video", "voice", "audio", "document", "image", "other"}

    def __init__(self, root):
        self.root = Path(root)
        for category in self.CATEGORIES:
            (self.root / category).mkdir(parents=True, exist_ok=True)

    def get_path(self, category, filename):
        if category not in self.CATEGORIES:
            raise ValueError(f"Unsupported cache category: {category}")
        safe_name = Path(filename).name
        if not safe_name or safe_name in {".", ".."}:
            raise ValueError("Invalid filename")
        return self.root / category / safe_name

    async def copy(self, source, destination):
        await asyncio.to_thread(shutil.copyfile, source, destination)

    async def delete(self, path):
        await asyncio.to_thread(Path(path).unlink, missing_ok=True)
