import pytest
import asyncio

from utils.cache import AsyncCache


@pytest.mark.asyncio
class TestAsyncCache:

    async def test_set_and_get(self):
        cache = AsyncCache(settings=None)
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    async def test_get_nonexistent_key(self):
        cache = AsyncCache(settings=None)
        result = await cache.get("missing")
        assert result is None

    async def test_keys_method(self):
        cache = AsyncCache(settings=None)
        await cache.set("a", 1)
        await cache.set("b", 2)
        keys = await cache.keys()
        assert set(keys) == {"a", "b"}

    async def test_delete_existing_key(self):
        cache = AsyncCache(settings=None)
        await cache.set("to_delete", 123)
        await cache.delete("to_delete")
        result = await cache.get("to_delete")
        assert result is None

    async def test_delete_nonexistent_key(self):
        cache = AsyncCache(settings=None)
        await cache.delete("missing")

    async def test_concurrent_set_and_get(self):
        cache = AsyncCache(settings=None)

        async def writer():
            for i in range(100):
                await cache.set(f"key{i}", i)

        async def reader():
            await asyncio.sleep(0.01)
            for i in range(100):
                val = await cache.get(f"key{i}")
                if val is not None:
                    assert isinstance(val, int)

        await asyncio.gather(writer(), reader())
