"""Offline regression for the Pydantic AI output API used by the examples."""

from __future__ import annotations

import importlib
import os
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


class PydanticAICompatibilityTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["OPENAI_API_KEY"] = "readme-refresh-not-a-real-key"

        from pydantic_ai import models
        from pydantic_ai.models.test import TestModel

        models.ALLOW_MODEL_REQUESTS = False
        cls.TestModel = TestModel
        cls.review = importlib.import_module("02_structured_output")
        cls.pipeline = importlib.import_module("07_agent_pipeline")
        cls.roast = importlib.import_module("08_roast_my_code")
        cls.whisper = importlib.import_module("09_whisper_agent")

    async def test_structured_review_returns_the_declared_model(self) -> None:
        with self.review.agent.override(model=self.TestModel()):
            result = await self.review.review(
                self.review.ReviewRequest(movie="Synthetic fixture film")
            )

        self.assertIsInstance(result, self.review.MovieReview)
        self.assertEqual(
            set(result.model_dump()),
            {"title", "rating", "pros", "cons", "one_liner"},
        )

    async def test_pipeline_reads_plain_text_agent_outputs(self) -> None:
        agents = (
            self.pipeline.researcher,
            self.pipeline.writer,
            self.pipeline.editor,
        )
        with ExitStack() as overrides:
            for agent in agents:
                overrides.enter_context(agent.override(model=self.TestModel()))
            result = await self.pipeline.blog(
                self.pipeline.BlogRequest(topic="Synthetic fixture topic")
            )

        self.assertEqual(set(result), {"facts", "draft", "final"})
        self.assertTrue(all(isinstance(value, str) for value in result.values()))

    async def test_roast_returns_the_declared_model(self) -> None:
        with self.roast.agent.override(model=self.TestModel()):
            result = await self.roast.roast(
                self.roast.CodeRequest(code="def add(a, b): return a + b")
            )

        self.assertIsInstance(result, self.roast.RoastResult)
        self.assertEqual(
            set(result.model_dump()),
            {"roast", "score", "issues", "compliment"},
        )

    async def test_transcription_route_uses_a_synthetic_audio_boundary(self) -> None:
        transcript_text = "Synthetic fixture transcript."
        create = AsyncMock(return_value=SimpleNamespace(text=transcript_text))
        fake_client = SimpleNamespace(
            audio=SimpleNamespace(
                transcriptions=SimpleNamespace(create=create),
            ),
        )

        class SyntheticUpload:
            filename = "fixture.wav"
            content_type = "audio/wav"

            async def read(self) -> bytes:
                return b"synthetic audio fixture"

        with patch.object(self.whisper, "openai_client", fake_client):
            with self.whisper.agent.override(model=self.TestModel()):
                result = await self.whisper.transcribe(SyntheticUpload())

        create.assert_awaited_once()
        self.assertEqual(result["transcript"], transcript_text)
        self.assertEqual(
            set(result),
            {"transcript", "summary", "action_items", "sentiment"},
        )
        self.assertIsInstance(result["summary"], str)
        self.assertIsInstance(result["action_items"], list)
        self.assertIsInstance(result["sentiment"], str)


if __name__ == "__main__":
    unittest.main()
