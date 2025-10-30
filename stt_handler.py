"""
Speech-to-text handler using OpenAI Whisper.

This module implements speech recognition using the open-source
Whisper model for accurate Spanish transcription.
"""

import torch
from pathlib import Path
from typing import Optional
from interfaces.stt_interface import STTInterface


class WhisperSTTHandler(STTInterface):
    """
    Speech-to-text implementation using OpenAI Whisper.

    Whisper is an open-source, state-of-the-art speech recognition model
    that works excellently with Spanish and other languages.

    Model sizes:
    - tiny: Fastest, least accurate (~1GB RAM)
    - base: Fast, good accuracy (~1GB RAM)
    - small: Balanced (~2GB RAM)
    - medium: High accuracy (~5GB RAM)
    - large: Best accuracy (~10GB RAM)

    Recommended: "base" or "small" for real-time Discord bot
    """

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT handler.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._ready = False

    async def initialize(self) -> bool:
        """
        Initialize Whisper model.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Import whisper
            try:
                import whisper
            except ImportError:
                print("Whisper not installed. Install with: pip install openai-whisper")
                return False

            # Load model
            print(f"Loading Whisper {self.model_size} model on {self.device}...")
            self.model = whisper.load_model(self.model_size, device=self.device)

            self._ready = True
            print(f"Whisper STT initialized successfully with {self.model_size} model")
            return True

        except Exception as e:
            print(f"Failed to initialize Whisper: {e}")
            self._ready = False
            return False

    async def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = "es"
    ) -> str:
        """
        Transcribe audio file to text using Whisper.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code hint (default "es" for Spanish)

        Returns:
            Transcribed text string

        Raises:
            Exception: If transcription fails
        """
        if not self._ready or not self.model:
            raise Exception("STT handler not initialized. Call initialize() first.")

        if not audio_path.exists():
            raise Exception(f"Audio file not found: {audio_path}")

        try:
            print(f"Transcribing audio: {audio_path}")

            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                fp16=(self.device == "cuda")  # Use FP16 on GPU for speed
            )

            text = result["text"].strip()
            print(f"Transcription: '{text}'")
            return text

        except Exception as e:
            raise Exception(f"Transcription failed: {e}")

    async def cleanup(self) -> None:
        """
        Clean up Whisper model resources.
        """
        if self.model:
            del self.model
            self.model = None

        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self._ready = False
        print("STT handler cleaned up")

    def is_ready(self) -> bool:
        """
        Check if STT system is ready.

        Returns:
            True if ready, False otherwise
        """
        return self._ready and self.model is not None


# ALTERNATIVE IMPLEMENTATION: Google Speech Recognition (Free, Cloud)
# Uncomment to use Google Speech Recognition (no GPU needed, but less accurate)

"""
import speech_recognition as sr
from pydub import AudioSegment

class GoogleSTTHandler(STTInterface):
    '''
    Alternative STT using Google Speech Recognition (FREE, CLOUD).

    Pros:
    - No GPU required
    - No model download
    - Fast

    Cons:
    - Requires internet
    - Less accurate than Whisper
    - May have rate limits

    Install: pip install SpeechRecognition pydub
    '''

    def __init__(self):
        self.recognizer = None
        self._ready = False

    async def initialize(self) -> bool:
        try:
            self.recognizer = sr.Recognizer()
            self._ready = True
            return True
        except Exception as e:
            print(f"Failed to initialize Google STT: {e}")
            return False

    async def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = "es"
    ) -> str:
        if not self._ready:
            raise Exception("STT not initialized")

        try:
            # Convert to WAV if needed
            if audio_path.suffix.lower() != '.wav':
                audio = AudioSegment.from_file(str(audio_path))
                wav_path = audio_path.with_suffix('.wav')
                audio.export(str(wav_path), format='wav')
                audio_path = wav_path

            # Transcribe
            with sr.AudioFile(str(audio_path)) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=language + "-ES"
                )
                return text.strip()

        except sr.UnknownValueError:
            return ""  # Could not understand audio
        except Exception as e:
            raise Exception(f"Google STT failed: {e}")

    async def cleanup(self) -> None:
        self._ready = False

    def is_ready(self) -> bool:
        return self._ready
"""
