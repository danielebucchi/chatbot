import random
import time
from typing import List, Dict, Any

from fastapi import Depends

from utils.config import Settings, get_settings


class LLMGenerator:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings

    async def generate(self, question: str, files_meta: List[Dict[str, Any]]) -> Dict[str, Any]:
        referenced_docs = [f['filename'] for f in files_meta]
        answer = f"Mock: \"{question}\"."
        if referenced_docs:
            answer += f" I used documents: {', '.join(referenced_docs)}."
        claims = {}
        n = random.randint(1, 100)

        for i in range(n):
                claims[i] = {"text": f"Claim number {i}", "weight": random.randint(1, 100)}

        return {
            "answer": answer,
            "claims": claims,
            "referenced_documents": referenced_docs,
            "generated_at": int(time.time())
        }

def get_llm_generator(settings: Settings = Depends(get_settings)) -> LLMGenerator:
    return LLMGenerator(settings=settings)
