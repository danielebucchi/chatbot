import hashlib
import uuid
from typing import List, Dict, Any, Tuple

from fastapi import UploadFile, Depends

from utils.cache import AsyncCache, get_cache
from utils.file_manager import FileManager, get_file_manager
from utils.llm_generator import get_llm_generator, LLMGenerator


class AskHelper:
    def __init__(self, cache: AsyncCache = Depends(get_cache),
                             file_manager: FileManager = Depends(get_file_manager),
                             llm_generator: LLMGenerator = Depends(get_llm_generator)):
        self.cache = cache
        self.file_manager = file_manager
        self.llm_generator = llm_generator


    async def get_utils(self, question: str, files: List[UploadFile]) -> Tuple[str, List[Dict[str, str]]]:
        request_id = str(uuid.uuid4())
        files_meta = await self.file_manager.save_files(request_id, files)
        return self._make_cache_key(question, files_meta), files_meta

    async def handle_request(self,
                             question: str,
                             files: List[UploadFile],
                             ) -> Dict[str, Any]:
        cache_key, files_meta = await self.get_utils(question, files)

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        response = await self.llm_generator.generate(question, files_meta)
        await self.cache.set(cache_key, response)
        return response

    @staticmethod
    def _make_cache_key(question: str, files_meta: List[Dict[str, Any]]) -> str:
        h = hashlib.sha256()
        h.update(question.encode("utf-8"))
        fingerprint = "".join(sorted(f["sha256"] + "::" + f["filename"] for f in files_meta))
        h.update(fingerprint.encode("utf-8"))
        return h.hexdigest()

def get_ask_helper(cache: AsyncCache = Depends(get_cache),
                             file_manager: FileManager = Depends(get_file_manager),
                             llm_generator: LLMGenerator = Depends(get_llm_generator)) -> AskHelper:
    return AskHelper(cache=cache, file_manager=file_manager, llm_generator=llm_generator)
