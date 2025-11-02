import hashlib
import uuid
from typing import List, Dict, Any

from fastapi import UploadFile, Depends

from helpers.ask_helper import AskHelper, get_ask_helper
from utils.cache import AsyncCache, get_cache
from utils.file_manager import FileManager, get_file_manager
from utils.llm_generator import get_llm_generator, LLMGenerator


class ClaimHelper:
    def __init__(self, ask_helper: AskHelper = Depends(get_ask_helper),
                 cache: AsyncCache = Depends(get_cache)):
        self.ask_helper = ask_helper
        self.cache = cache


    async def save_claim(self,
                             question: str,
                             files: List[UploadFile],
                             claim_id: str,
                             ) -> None:
        response =  await self.ask_helper.handle_request(question, files)

        update_data = self.update_claim_weight(response, claim_id)
        cache_key, _ = await self.ask_helper.get_utils(question, files)
        await self.cache.set(cache_key, update_data)

    @staticmethod
    def update_claim_weight(response: dict, claim_id: str) -> dict:
        updated_data = response.copy()

        if int(claim_id) not in updated_data["claims"]:
            raise ValueError(f"Claim ID {claim_id} non trovato nella cache")

        updated_data["claims"][int(claim_id)]["weight"] = updated_data["claims"][int(claim_id)]["weight"] + 1

        return updated_data

def get_claim_helper(ask_helper: AskHelper = Depends(get_ask_helper), cache: AsyncCache = Depends(get_cache)) -> ClaimHelper:
    return ClaimHelper(ask_helper=ask_helper, cache=cache)
