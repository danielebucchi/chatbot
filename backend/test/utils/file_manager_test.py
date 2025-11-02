import pytest
import hashlib
from fastapi import UploadFile
from io import BytesIO
import os

from utils.config import Settings
from utils.file_manager import FileManager


@pytest.mark.asyncio
class TestFileManager:

    async def test_save_files(self, tmp_path):
        settings = Settings()
        settings.APP_TMP_DIR = str(tmp_path)
        fm = FileManager(settings)

        content1 = b"hello world"
        content2 = b"pytest testing"
        files = [
            UploadFile(filename="file1.txt", file=BytesIO(content1)),
            UploadFile(filename="file2.txt", file=BytesIO(content2))
        ]
        request_id = "req123"

        saved_meta = await fm.save_files(request_id, files)

        assert len(saved_meta) == 2
        for meta, content, fname in zip(saved_meta, [content1, content2], ["file1.txt", "file2.txt"]):
            assert meta["filename"] == fname
            assert meta["size"] == len(content)
            assert meta["sha256"] == hashlib.sha256(content).hexdigest()
            assert os.path.isfile(meta["path"])

    async def test_save_files_no_filename(self, tmp_path):
        settings = Settings()
        settings.APP_TMP_DIR = str(tmp_path)
        fm = FileManager(settings)

        content = b"data without filename"
        file = UploadFile(filename="", file=BytesIO(content))
        request_id = "req456"

        saved_meta = await fm.save_files(request_id, [file])

        assert len(saved_meta) == 1
        assert saved_meta[0]["size"] == len(content)
        assert saved_meta[0]["sha256"] == hashlib.sha256(content).hexdigest()
        assert saved_meta[0]["filename"].startswith("upload-")
        assert os.path.isfile(saved_meta[0]["path"])

    def test_cleanup(self, tmp_path):
        settings = Settings()
        settings.APP_TMP_DIR = str(tmp_path)
        fm = FileManager(settings)

        request_id = "req789"
        test_dir = tmp_path / request_id
        test_dir.mkdir()
        test_file = test_dir / "dummy.txt"
        test_file.write_text("delete me")

        fm.cleanup(request_id)

        assert not test_dir.exists()

    def test_cleanup_nonexistent_dir(self, tmp_path):
        settings = Settings()
        settings.APP_TMP_DIR = str(tmp_path)
        fm = FileManager(settings)

        request_id = "nonexistent"

        fm.cleanup(request_id)
