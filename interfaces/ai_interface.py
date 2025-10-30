"""
Abstract interface for AI conversation handler.

This module defines the interface for AI models that generate responses
in David Bisbal's personality. Implementations can use local models (Ollama)
or cloud APIs (Anthropic, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class AIInterface(ABC):
    """
    Abstract interface for conversational AI.

    This interface allows swapping between different AI providers
    (Ollama, Anthropic, OpenAI, etc.) without changing the bot logic.
    """

    @abstractmethod
    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response in David Bisbal's personality.

        Args:
            user_message: The user's input message
            conversation_history: Optional list of previous messages in format
                                [{"role": "user", "content": "..."},
                                 {"role": "assistant", "content": "..."}]

        Returns:
            Response string in Bisbal's personality

        Raises:
            Exception: If AI generation fails
        """
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the AI model/connection.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources (close connections, etc.).
        """
        pass
