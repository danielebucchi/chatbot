from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException
from typing import List, Optional, Union

from helpers.ask_helper import AskHelper, get_ask_helper
from helpers.claim_helper import ClaimHelper, get_claim_helper
from utils.cache import get_cache, AsyncCache

router = APIRouter()

@router.post("/ask", response_model=None)
async def ask(
    question: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    ask_helper: AskHelper = Depends(get_ask_helper)
):
    files = files or []
    try:
        return await ask_helper.handle_request(question, files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/claim", response_model=None)
async def claim(
    question: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    claim_id: str = Form(...),
    claim_helper: ClaimHelper = Depends(get_claim_helper)
):
    files = files or []
    try:
        return await claim_helper.save_claim(question, files, claim_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache")
async def list_cache(cache: AsyncCache = Depends(get_cache)):
    keys = await cache.keys()
    return {"count": len(keys), "keys": keys}

@router.get("/cache/{key}")
async def get_cache_key(key: str, cache: AsyncCache = Depends(get_cache)):
    value = await cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' didn't find in Cache")
    return {"key": key, "value": value}

@router.delete("/cache")
async def list_cache(key: str, cache: AsyncCache = Depends(get_cache)):
    await cache.delete(key)
