import asyncio
from typing import Dict, Any, List
from fastapi import Depends
from .config import Settings, get_settings

class AsyncCache:
    def __init__(self, settings = Depends(get_settings)):
        self._data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self.settings = settings

    async def get(self, key: str):
        async with self._lock:
            return self._data.get(key)

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._data[key] = value

    async def keys(self) -> List[str]:
        async with self._lock:
            return list(self._data.keys())

    async def delete(self, key: str):
        async with self._lock:
            if key in self._data:
                del self._data[key]

def get_cache(settings: Settings = Depends(get_settings)) -> AsyncCache:
    if not hasattr(get_cache, "_instance"):
        get_cache._instance = AsyncCache(settings=settings)
    return get_cache._instance
