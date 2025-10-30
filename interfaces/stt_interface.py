"""
Abstract interface for speech-to-text (STT) conversion.

This module defines the interface for converting audio to text.
Implementations can use various services (Whisper, Google STT, etc.).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class STTInterface(ABC):
    """
    Abstract interface for speech-to-text conversion.

    Implementations should convert audio files to text transcriptions.
    """

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the STT system.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = "es"
    ) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file to transcribe
            language: Language code hint (default "es" for Spanish)

        Returns:
            Transcribed text string

        Raises:
            Exception: If transcription fails
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if STT system is ready.

        Returns:
            True if ready, False otherwise
        """
        pass
