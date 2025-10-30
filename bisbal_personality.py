"""
David Bisbal personality implementation.

This module implements the AI interface with David Bisbal's personality traits,
expressions, and conversational style.
"""

import os
from typing import Optional, List, Dict
from interfaces.ai_interface import AIInterface


class BisbalPersonality(AIInterface):
    """
    Implementation of David Bisbal's personality using Anthropic API.

    This class uses Claude to generate responses with Bisbal's characteristic
    expressions, Andalusian style, and passionate personality.

    To use Ollama instead, see the commented alternative implementation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Bisbal personality AI.

        Args:
            api_key: Anthropic API key (or None to use ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines Bisbal's personality.

        Returns:
            System prompt string
        """
        return """You are David Bisbal, the famous Spanish singer from Almeria.

PERSONALITY TRAITS:
- Speak with passion and enthusiasm about everything
- You're warm, friendly, and expressive
- You love music and often reference your songs
- You're proud of your Andalusian roots, especially Almeria

LANGUAGE STYLE:
- Use Andalusian Spanish expressions naturally:
  - "mu" instead of "muy"
  - "to" instead of "todo"
  - "zeaza" for "se asa" (it's hot)
- Drop characteristic expressions:
  - "Ayyy!" when excited or surprised
  - "Buleria!" when enthusiastic
  - "Ave Maria!" for surprise
  - "Corazon partio!" when emotional or dramatic
- Mention Almeria occasionally when relevant
- Reference your songs when appropriate (Ave Maria, Buleria, Corazon Partio, etc.)

IMPORTANT RULES:
- ALWAYS start greetings with: "Lo primero de todo, como estan los makinas?"
- Be a bit exaggerated and meme-like but still believable
- Keep responses conversational and natural (2-4 sentences usually)
- Use Spanish language
- Show enthusiasm and energy in your responses
- Be friendly and approachable

EXAMPLES:
User: "Hola David!"
You: "Lo primero de todo, como estan los makinas? Ayyy, que alegria verte por aqui! Como estas tu, corazon?"

User: "Como estas?"
You: "Pues mira, aqui estoy mu bien, con una energia que no veas! Esto es pura buleria, tio!"

User: "Que calor hace"
You: "Ave Maria, zeaza uno aqui! Esto me recuerda a Almeria en verano, que aquello si que es calor de verdad!"

Remember: You ARE David Bisbal. Respond naturally as him, not as an AI pretending to be him."""

    async def initialize(self) -> bool:
        """
        Initialize Anthropic API client.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try importing anthropic
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
                return True
            except ImportError:
                print("Anthropic library not installed. Install with: pip install anthropic")
                return False
        except Exception as e:
            print(f"Failed to initialize Anthropic client: {e}")
            return False

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response in Bisbal's personality using Anthropic Claude.

        Args:
            user_message: User's message
            conversation_history: Previous conversation context

        Returns:
            Bisbal's response

        Raises:
            Exception: If generation fails
        """
        if not self.client:
            raise Exception("Client not initialized. Call initialize() first.")

        try:
            # Build messages array
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            # Call Anthropic API
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=self.system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Failed to generate response: {e}")

    async def cleanup(self) -> None:
        """
        Clean up Anthropic client resources.
        """
        # Anthropic client doesn't require explicit cleanup
        self.client = None


# ALTERNATIVE IMPLEMENTATION: Ollama (Free, Local)
# Uncomment this class and comment out BisbalPersonality above to use Ollama

"""
class BisbalPersonality(AIInterface):
    '''
    Ollama-based implementation of Bisbal personality (FREE, LOCAL).

    Requires Ollama installed locally with a model like llama2 or mistral.
    Install: https://ollama.ai/
    Then run: ollama pull llama2
    '''

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        '''
        Initialize Ollama-based personality.

        Args:
            model: Ollama model name (e.g., "llama2", "mistral")
            base_url: Ollama server URL
        '''
        self.model = model
        self.base_url = base_url
        self.client = None
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        # Same as above
        return '''[Same system prompt as Anthropic version]'''

    async def initialize(self) -> bool:
        try:
            import httpx
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
            # Test connection
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            return False

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not self.client:
            raise Exception("Client not initialized")

        # Build prompt with conversation history
        prompt = f"{self.system_prompt}\n\n"
        if conversation_history:
            for msg in conversation_history:
                role = "User" if msg["role"] == "user" else "Bisbal"
                prompt += f"{role}: {msg['content']}\n"
        prompt += f"User: {user_message}\nBisbal:"

        # Call Ollama API
        response = await self.client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.8, "num_predict": 150}
            }
        )

        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            raise Exception(f"Ollama API error: {response.status_code}")

    async def cleanup(self) -> None:
        if self.client:
            await self.client.aclose()
"""
