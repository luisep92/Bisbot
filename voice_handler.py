"""
Voice synthesis handler using Coqui XTTS v2.

This module implements voice cloning and text-to-speech synthesis
using the open-source Coqui XTTS v2 model.
"""

import os
import torch
from pathlib import Path
from typing import Optional
from interfaces.voice_interface import VoiceInterface


class XTTSVoiceHandler(VoiceInterface):
    """
    Voice synthesis implementation using Coqui XTTS v2.

    XTTS v2 is an open-source voice cloning model that can generate
    high-quality speech in multiple languages from short reference audio.

    Requirements:
    - CUDA-capable GPU recommended (CPU works but is slow)
    - 10-30 seconds of clean reference audio
    - Model downloads ~2GB on first run
    """

    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize XTTS voice handler.

        Args:
            model_name: TTS model identifier for Coqui
        """
        self.model_name = model_name
        self.model = None
        self.reference_audio = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._ready = False

    async def initialize(self, reference_audio_path: Optional[Path] = None) -> bool:
        """
        Initialize XTTS model and load reference audio.

        Args:
            reference_audio_path: Path to Bisbal voice reference audio
                                 (10-30 seconds, WAV or MP3 format)

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Import TTS library
            try:
                from TTS.api import TTS
            except ImportError:
                print("TTS library not installed. Install with: pip install TTS")
                return False

            # Load XTTS model
            print(f"Loading XTTS model on {self.device}...")
            self.model = TTS(self.model_name).to(self.device)

            # Set reference audio
            if reference_audio_path:
                if not reference_audio_path.exists():
                    print(f"Reference audio not found: {reference_audio_path}")
                    return False
                self.reference_audio = str(reference_audio_path)
                print(f"Loaded reference audio: {reference_audio_path}")
            else:
                # Try default location
                default_path = Path("data/bisbal_voice_sample.wav")
                if default_path.exists():
                    self.reference_audio = str(default_path)
                    print(f"Using default reference audio: {default_path}")
                else:
                    print("WARNING: No reference audio provided. Voice cloning will not work.")
                    print("Please provide a 10-30 second audio sample of David Bisbal.")
                    return False

            self._ready = True
            print("XTTS voice handler initialized successfully")
            return True

        except Exception as e:
            print(f"Failed to initialize XTTS: {e}")
            self._ready = False
            return False

    async def synthesize_speech(
        self,
        text: str,
        output_path: Path,
        language: str = "es"
    ) -> bool:
        """
        Synthesize speech from text using Bisbal's cloned voice.

        Args:
            text: Spanish text to convert to speech
            output_path: Where to save the WAV file
            language: Language code (default "es")

        Returns:
            True if synthesis successful, False otherwise

        Raises:
            Exception: If synthesis fails
        """
        if not self._ready or not self.model:
            raise Exception("Voice handler not initialized. Call initialize() first.")

        if not self.reference_audio:
            raise Exception("No reference audio loaded for voice cloning.")

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Run XTTS synthesis
            print(f"Synthesizing: '{text[:50]}...'")
            self.model.tts_to_file(
                text=text,
                speaker_wav=self.reference_audio,
                language=language,
                file_path=str(output_path)
            )

            # Verify output file exists
            if not output_path.exists():
                raise Exception("Output file was not created")

            print(f"Synthesized audio saved to: {output_path}")
            return True

        except Exception as e:
            raise Exception(f"Speech synthesis failed: {e}")

    async def cleanup(self) -> None:
        """
        Clean up model resources and free GPU/CPU memory.
        """
        if self.model:
            del self.model
            self.model = None

        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self._ready = False
        print("Voice handler cleaned up")

    def is_ready(self) -> bool:
        """
        Check if voice system is ready to synthesize.

        Returns:
            True if ready, False otherwise
        """
        return self._ready and self.model is not None and self.reference_audio is not None


# ALTERNATIVE IMPLEMENTATION: Edge TTS (Free, No GPU needed)
# Uncomment to use Microsoft Edge TTS (no voice cloning, but Spanish voices available)

"""
import edge_tts
from interfaces.voice_interface import VoiceInterface

class EdgeTTSVoiceHandler(VoiceInterface):
    '''
    Alternative voice handler using Microsoft Edge TTS (FREE, CLOUD).

    Pros:
    - No GPU required
    - Fast synthesis
    - Good quality Spanish voices

    Cons:
    - No voice cloning (can't sound exactly like Bisbal)
    - Requires internet connection

    Best Spanish voices for male speaker:
    - "es-ES-AlvaroNeural" (Castilian Spanish, male)
    - "es-MX-JorgeNeural" (Mexican Spanish, male)
    '''

    def __init__(self, voice: str = "es-ES-AlvaroNeural"):
        self.voice = voice
        self._ready = False

    async def initialize(self, reference_audio_path: Optional[Path] = None) -> bool:
        # Edge TTS doesn't need initialization
        self._ready = True
        return True

    async def synthesize_speech(
        self,
        text: str,
        output_path: Path,
        language: str = "es"
    ) -> bool:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(output_path))

            return output_path.exists()
        except Exception as e:
            raise Exception(f"Edge TTS synthesis failed: {e}")

    async def cleanup(self) -> None:
        self._ready = False

    def is_ready(self) -> bool:
        return self._ready
"""
