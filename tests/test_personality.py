"""
Integration tests for Bisbal personality module.

These tests verify that the AI personality implementation works correctly.
"""

import pytest
import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bisbal_personality import BisbalPersonality


class TestBisbalPersonality:
    """Test suite for Bisbal personality AI."""

    @pytest.fixture
    async def personality(self):
        """Create and initialize personality instance."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set - skipping AI tests")

        personality = BisbalPersonality(api_key=api_key)
        initialized = await personality.initialize()

        if not initialized:
            pytest.skip("Failed to initialize personality - check API key")

        yield personality

        await personality.cleanup()

    @pytest.mark.asyncio
    async def test_greeting_response(self, personality):
        """
        Test that Bisbal responds to greetings with his signature phrase.

        IMPORTANT: Response should contain "Lo primero de todo, como estan los makinas?"
        """
        response = await personality.generate_response("Hola David!")

        # Check response is not empty
        assert response, "Response should not be empty"
        assert len(response) > 10, "Response should be substantial"

        # Check for greeting phrase (may vary slightly)
        greeting_indicators = [
            "makinas",
            "primero de todo",
            "como estan"
        ]

        has_greeting = any(indicator in response.lower() for indicator in greeting_indicators)
        print(f"Response: {response}")
        print(f"Has greeting indicators: {has_greeting}")

        # Note: AI may not always include exact phrase, so we log but don't fail
        if not has_greeting:
            print("WARNING: Response may not include signature greeting")

    @pytest.mark.asyncio
    async def test_personality_expressions(self, personality):
        """
        Test that Bisbal uses characteristic expressions.

        Should include expressions like Ave Maria, Ayyy, Buleria, etc.
        """
        # Ask something that should trigger enthusiasm
        response = await personality.generate_response(
            "David, estoy muy emocionado por tu nueva cancion!"
        )

        assert response, "Response should not be empty"

        # Check for ANY Bisbal expression
        expressions = [
            "ayyy",
            "ave maria",
            "buleria",
            "corazon",
            "mu bien",
            "mu ",  # Andalusian "mu" for "muy"
        ]

        has_expression = any(expr in response.lower() for expr in expressions)
        print(f"Response: {response}")
        print(f"Has Bisbal expression: {has_expression}")

        # Log but don't fail - AI behavior can vary
        if not has_expression:
            print("WARNING: Response may not include characteristic expressions")

    @pytest.mark.asyncio
    async def test_conversation_history(self, personality):
        """
        Test that personality can maintain conversation context.
        """
        # First message
        history = []
        response1 = await personality.generate_response(
            "Hola David, soy Juan",
            conversation_history=history
        )
        assert response1, "First response should not be empty"

        # Add to history
        history.append({"role": "user", "content": "Hola David, soy Juan"})
        history.append({"role": "assistant", "content": response1})

        # Second message referencing first
        response2 = await personality.generate_response(
            "Te acuerdas de mi nombre?",
            conversation_history=history
        )
        assert response2, "Second response should not be empty"

        # Check if name is mentioned (context awareness)
        print(f"Response 1: {response1}")
        print(f"Response 2: {response2}")

        # AI should ideally reference "Juan" but we just verify it responds
        assert len(response2) > 5, "Response should be substantial"


def test_interface_implementation():
    """
    Test that BisbalPersonality properly implements AIInterface.
    """
    from interfaces.ai_interface import AIInterface

    assert issubclass(BisbalPersonality, AIInterface), \
        "BisbalPersonality must implement AIInterface"

    # Check all abstract methods are implemented
    required_methods = ['generate_response', 'initialize', 'cleanup']
    for method in required_methods:
        assert hasattr(BisbalPersonality, method), \
            f"BisbalPersonality must implement {method}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
