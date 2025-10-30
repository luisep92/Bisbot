"""
Integration tests for voice synthesis handler.

These tests verify XTTS voice cloning functionality.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from voice_handler import XTTSVoiceHandler


class TestVoiceHandler:
    """Test suite for XTTS voice handler."""

    @pytest.fixture
    def test_output_dir(self, tmp_path):
        """Create temporary directory for test outputs."""
        output_dir = tmp_path / "audio_output"
        output_dir.mkdir()
        return output_dir

    @pytest.mark.asyncio
    async def test_initialization_without_reference(self):
        """
        Test that handler fails gracefully without reference audio.
        """
        handler = XTTSVoiceHandler()

        # Should fail without reference audio
        result = await handler.initialize(None)

        # We expect this to fail (no reference audio provided)
        assert not result, "Should fail without reference audio"
        assert not handler.is_ready(), "Handler should not be ready"

        await handler.cleanup()

    @pytest.mark.asyncio
    async def test_initialization_with_missing_reference(self):
        """
        Test that handler fails when reference audio doesn't exist.
        """
        handler = XTTSVoiceHandler()

        fake_path = Path("nonexistent_audio.wav")
        result = await handler.initialize(fake_path)

        assert not result, "Should fail with non-existent reference"
        assert not handler.is_ready(), "Handler should not be ready"

        await handler.cleanup()

    @pytest.mark.asyncio
    async def test_synthesis_without_initialization(self, test_output_dir):
        """
        Test that synthesis fails if not initialized.
        """
        handler = XTTSVoiceHandler()
        output_path = test_output_dir / "test.wav"

        with pytest.raises(Exception) as exc_info:
            await handler.synthesize_speech(
                "Test text",
                output_path
            )

        assert "not initialized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not Path("data/bisbal_voice_sample.wav").exists(),
        reason="Reference audio not available"
    )
    async def test_full_synthesis_pipeline(self, test_output_dir):
        """
        Full integration test with actual synthesis.

        REQUIRES: data/bisbal_voice_sample.wav to exist
        """
        handler = XTTSVoiceHandler()

        # Initialize with reference audio
        reference_path = Path("data/bisbal_voice_sample.wav")
        result = await handler.initialize(reference_path)

        if not result:
            pytest.skip("Failed to initialize XTTS - may need GPU or model download")

        assert handler.is_ready(), "Handler should be ready after initialization"

        # Synthesize test audio
        test_text = "Hola, soy David Bisbal!"
        output_path = test_output_dir / "bisbal_test.wav"

        success = await handler.synthesize_speech(test_text, output_path)

        assert success, "Synthesis should succeed"
        assert output_path.exists(), "Output file should exist"
        assert output_path.stat().st_size > 0, "Output file should not be empty"

        # Cleanup
        await handler.cleanup()
        assert not handler.is_ready(), "Handler should not be ready after cleanup"


def test_interface_implementation():
    """
    Test that XTTSVoiceHandler implements VoiceInterface correctly.
    """
    from interfaces.voice_interface import VoiceInterface

    assert issubclass(XTTSVoiceHandler, VoiceInterface), \
        "XTTSVoiceHandler must implement VoiceInterface"

    # Check required methods
    required_methods = ['initialize', 'synthesize_speech', 'cleanup', 'is_ready']
    for method in required_methods:
        assert hasattr(XTTSVoiceHandler, method), \
            f"XTTSVoiceHandler must implement {method}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
