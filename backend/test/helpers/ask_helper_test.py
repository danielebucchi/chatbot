import pytest
from unittest.mock import AsyncMock
from fastapi import UploadFile
from io import BytesIO

from helpers.ask_helper import AskHelper


@pytest.fixture
def ask_helper():
    mock_cache = AsyncMock()
    mock_file_manager = AsyncMock()
    mock_llm = AsyncMock()
    helper = AskHelper(mock_cache, mock_file_manager, mock_llm)
    return helper, mock_cache, mock_file_manager, mock_llm



class TestAskHelper:

    @pytest.mark.asyncio
    async def test_make_cache_key(self):
        question = "What is AI?"
        files_meta = [
            {"sha256": "abc123", "filename": "file1.txt"},
            {"sha256": "def456", "filename": "file2.txt"},
        ]

        result = AskHelper._make_cache_key(question, files_meta)

        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hash length
        result2 = AskHelper._make_cache_key(question, files_meta)
        assert result == result2

    @pytest.mark.asyncio
    async def test_get_utils(self):
        mock_cache = AsyncMock()
        mock_file_manager = AsyncMock()
        mock_llm = AsyncMock()

        mock_file_manager.save_files.return_value = [
            {"sha256": "xyz789", "filename": "input.txt"}
        ]

        helper = AskHelper(mock_cache, mock_file_manager, mock_llm)
        files = [UploadFile(filename="input.txt", file=BytesIO(b"data"))]
        question = "Explain quantum computing"

        cache_key, files_meta = await helper.get_utils(question, files)

        mock_file_manager.save_files.assert_awaited_once()
        assert isinstance(cache_key, str)
        assert isinstance(files_meta, list)
        assert files_meta[0]["filename"] == "input.txt"
        assert len(cache_key) == 64

    @pytest.mark.asyncio
    async def test_handle_request_cache_hit(self):
        mock_cache = AsyncMock()
        mock_file_manager = AsyncMock()
        mock_llm = AsyncMock()

        helper = AskHelper(mock_cache, mock_file_manager, mock_llm)

        cached_value = {"answer": "cached response"}
        mock_cache.get.return_value = cached_value
        mock_file_manager.save_files.return_value = [
            {"sha256": "abc", "filename": "doc.txt"}
        ]

        question = "What is Python?"
        files = [UploadFile(filename="doc.txt", file=BytesIO(b"test"))]

        response = await helper.handle_request(question, files)

        assert response == cached_value
        mock_cache.get.assert_awaited()
        mock_llm.generate.assert_not_awaited()
        mock_cache.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_request_cache_miss(self):
        mock_cache = AsyncMock()
        mock_file_manager = AsyncMock()
        mock_llm = AsyncMock()

        helper = AskHelper(mock_cache, mock_file_manager, mock_llm)

        mock_cache.get.return_value = None
        mock_file_manager.save_files.return_value = [
            {"sha256": "abc", "filename": "file.txt"}
        ]
        mock_llm.generate.return_value = {"answer": "fresh response"}

        question = "What is caching?"
        files = [UploadFile(filename="file.txt", file=BytesIO(b"dummy"))]

        response = await helper.handle_request(question, files)

        mock_file_manager.save_files.assert_awaited_once()
        mock_cache.get.assert_awaited_once()
        mock_llm.generate.assert_awaited_once_with(
            question, [{"sha256": "abc", "filename": "file.txt"}]
        )
        mock_cache.set.assert_awaited_once()
        assert response == {"answer": "fresh response"}
