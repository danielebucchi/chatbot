import pytest
from unittest.mock import patch

from utils.llm_generator import LLMGenerator

MODULE = LLMGenerator.__module__

@pytest.mark.asyncio
class TestLLMGenerator:

    @patch(f"{MODULE}.random.randint")
    @patch(f"{MODULE}.time.time")
    async def test_generate_no_files(self, mock_time, mock_randint):
        mock_randint.return_value = 2
        mock_time.return_value = 1234567890
        generator = LLMGenerator(settings=None)
        question = "What is AI?"
        files_meta = []

        result = await generator.generate(question, files_meta)

        assert "answer" in result
        assert result["answer"] == f'Mock: "{question}".'
        assert result["referenced_documents"] == []
        assert result["generated_at"] == 1234567890
        assert len(result["claims"]) == 2
        for k, claim in result["claims"].items():
            assert "text" in claim
            assert "weight" in claim


    @patch(f"{MODULE}.random.randint")
    @patch(f"{MODULE}.time.time")
    async def test_generate_with_files(self, mock_time, mock_randint):
        mock_randint.return_value = 1
        mock_time.return_value = 987654321
        generator = LLMGenerator(settings=None)
        question = "Summarize documents"
        files_meta = [
            {"filename": "doc1.txt", "sha256": "abc"},
            {"filename": "doc2.txt", "sha256": "def"}
        ]

        result = await generator.generate(question, files_meta)

        assert "answer" in result
        assert "I used documents: doc1.txt, doc2.txt." in result["answer"]
        assert result["referenced_documents"] == ["doc1.txt", "doc2.txt"]
        assert result["generated_at"] == 987654321
        assert len(result["claims"]) == 1
        for claim in result["claims"].values():
            assert "text" in claim
            assert "weight" in claim
