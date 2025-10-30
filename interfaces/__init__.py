"""
Interface definitions for the Bisbot Discord voice bot.

This package contains abstract interfaces that define the contract
for all major components of the bot.
"""

from .ai_interface import AIInterface
from .voice_interface import VoiceInterface
from .stt_interface import STTInterface

__all__ = ["AIInterface", "VoiceInterface", "STTInterface"]
