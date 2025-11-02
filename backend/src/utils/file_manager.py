import aiofiles
import hashlib
import os
import uuid
from typing import List, Dict
from fastapi import UploadFile, Depends

from .config import Settings, get_settings

class FileManager:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings

    async def save_files(self, request_id: str, files: List[UploadFile]) -> List[Dict[str, str]]:
        out_dir = os.path.join(self.settings.APP_TMP_DIR, request_id)
        os.makedirs(out_dir, exist_ok=True)
        saved = []
        for f in files:
            filename = os.path.basename(f.filename) or f"upload-{uuid.uuid4()}"
            dest_path = os.path.join(out_dir, filename)
            async with aiofiles.open(dest_path, "wb") as out_file:
                content = await f.read()
                await out_file.write(content)
            sha = hashlib.sha256(content).hexdigest()
            saved.append({
                "path": dest_path,
                "filename": filename,
                "sha256": sha,
                "size": len(content)
            })
        return saved

    def cleanup(self, request_id: str):
        dirpath = os.path.join(self.settings.APP_TMP_DIR, request_id)
        if os.path.isdir(dirpath):
            try:
                import shutil
                shutil.rmtree(dirpath)
            except Exception:
                pass

def get_file_manager(settings: Settings = Depends(get_settings)) -> FileManager:
    return FileManager(settings=settings)