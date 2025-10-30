"""
Integration tests for speech-to-text handler.

These tests verify Whisper STT functionality.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stt_handler import WhisperSTTHandler


class TestSTTHandler:
    """Test suite for Whisper STT handler."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """
        Test that handler initializes correctly.
        """
        handler = WhisperSTTHandler(model_size="tiny")  # Use smallest model for testing

        result = await handler.initialize()

        # May fail if Whisper not installed or first-time model download
        if not result:
            pytest.skip("Whisper initialization failed - check installation")

        assert handler.is_ready(), "Handler should be ready after initialization"

        await handler.cleanup()
        assert not handler.is_ready(), "Handler should not be ready after cleanup"

    @pytest.mark.asyncio
    async def test_transcription_without_initialization(self):
        """
        Test that transcription fails if not initialized.
        """
        handler = WhisperSTTHandler()

        with pytest.raises(Exception) as exc_info:
            await handler.transcribe(Path("test.wav"))

        assert "not initialized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_transcription_missing_file(self):
        """
        Test that transcription fails with missing audio file.
        """
        handler = WhisperSTTHandler(model_size="tiny")
        result = await handler.initialize()

        if not result:
            pytest.skip("Whisper not available")

        fake_path = Path("nonexistent_audio.wav")

        with pytest.raises(Exception) as exc_info:
            await handler.transcribe(fake_path)

        assert "not found" in str(exc_info.value).lower()

        await handler.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not Path("tests/test_audio.wav").exists(),
        reason="Test audio file not available"
    )
    async def test_transcription_with_audio(self):
        """
        Test transcription with actual audio file.

        REQUIRES: tests/test_audio.wav with Spanish speech
        """
        handler = WhisperSTTHandler(model_size="tiny")

        result = await handler.initialize()
        if not result:
            pytest.skip("Whisper initialization failed")

        audio_path = Path("tests/test_audio.wav")
        transcription = await handler.transcribe(audio_path, language="es")

        assert isinstance(transcription, str), "Transcription should be a string"
        # Don't assert specific content - just that it returns something
        print(f"Transcription: {transcription}")

        await handler.cleanup()


def test_interface_implementation():
    """
    Test that WhisperSTTHandler implements STTInterface correctly.
    """
    from interfaces.stt_interface import STTInterface

    assert issubclass(WhisperSTTHandler, STTInterface), \
        "WhisperSTTHandler must implement STTInterface"

    # Check required methods
    required_methods = ['initialize', 'transcribe', 'cleanup', 'is_ready']
    for method in required_methods:
        assert hasattr(WhisperSTTHandler, method), \
            f"WhisperSTTHandler must implement {method}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
