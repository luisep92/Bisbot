"""
Abstract interface for voice synthesis and cloning.

This module defines the interface for text-to-speech systems with voice cloning.
Primary implementation uses Coqui XTTS v2, but interface allows for alternatives.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class VoiceInterface(ABC):
    """
    Abstract interface for voice synthesis with cloning.

    Implementations should support voice cloning from reference audio samples
    and generate natural-sounding speech.
    """

    @abstractmethod
    async def initialize(self, reference_audio_path: Optional[Path] = None) -> bool:
        """
        Initialize the voice synthesis system.

        Args:
            reference_audio_path: Path to reference audio for voice cloning.
                                 Should be 10-30 seconds of clean speech.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        output_path: Path,
        language: str = "es"
    ) -> bool:
        """
        Synthesize speech from text using cloned voice.

        Args:
            text: Text to convert to speech
            output_path: Where to save the generated audio file
            language: Language code (default "es" for Spanish)

        Returns:
            True if synthesis successful, False otherwise

        Raises:
            Exception: If synthesis fails
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources (unload models, free memory, etc.).
        """
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if voice system is ready to synthesize.

        Returns:
            True if ready, False if still initializing or failed
        """
        pass
