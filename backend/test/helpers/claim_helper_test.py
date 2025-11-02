import pytest
from unittest.mock import AsyncMock
from fastapi import UploadFile
from io import BytesIO

from helpers.claim_helper import ClaimHelper


class TestClaimHelper:

    def test_update_claim_weight_success(self):
        response = {
            "claims": {
                1: {"weight": 3},
                2: {"weight": 5}
            }
        }
        claim_id = "2"

        updated = ClaimHelper.update_claim_weight(response, claim_id)

        assert updated["claims"][2]["weight"] == 6
        assert response["claims"][1]["weight"] == 3

    def test_update_claim_weight_missing_claim(self):
        response = {"claims": {1: {"weight": 2}}}
        claim_id = "99"

        with pytest.raises(ValueError, match="Claim ID 99 non trovato nella cache"):
            ClaimHelper.update_claim_weight(response, claim_id)

    @pytest.mark.asyncio
    async def test_save_claim_success(self):
        mock_ask_helper = AsyncMock()
        mock_cache = AsyncMock()
        helper = ClaimHelper(mock_ask_helper, mock_cache)

        question = "What is a claim?"
        files = [UploadFile(filename="doc.txt", file=BytesIO(b"file content"))]
        claim_id = "1"

        fake_response = {
            "claims": {
                1: {"weight": 2}
            }
        }
        mock_ask_helper.handle_request.return_value = fake_response
        mock_ask_helper.get_utils.return_value = ("cache_key_123", [])

        await helper.save_claim(question, files, claim_id)

        mock_ask_helper.handle_request.assert_awaited_once_with(question, files)
        mock_ask_helper.get_utils.assert_awaited_once_with(question, files)
        mock_cache.set.assert_awaited_once()

        args, _ = mock_cache.set.call_args
        cache_key, update_data = args
        assert cache_key == "cache_key_123"
        assert update_data["claims"][1]["weight"] == 3

    @pytest.mark.asyncio
    async def test_save_claim_missing_claim(self):
        mock_ask_helper = AsyncMock()
        mock_cache = AsyncMock()
        helper = ClaimHelper(mock_ask_helper, mock_cache)

        question = "Missing claim test"
        files = [UploadFile(filename="f.txt", file=BytesIO(b"x"))]
        claim_id = "99"

        fake_response = {"claims": {1: {"weight": 1}}}
        mock_ask_helper.handle_request.return_value = fake_response
        mock_ask_helper.get_utils.return_value = ("cache_key_abc", [])

        with pytest.raises(ValueError, match="Claim ID 99 non trovato nella cache"):
            await helper.save_claim(question, files, claim_id)

        mock_ask_helper.handle_request.assert_awaited_once()
        mock_cache.set.assert_not_awaited()
