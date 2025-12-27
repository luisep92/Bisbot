import json
from pathlib import Path

DEFAULT_CONFIG_PATH = "config/config.json"
DEFAULT_CONTEXT_PATH = "config/context.txt"

class Config:
    def __init__(self):
        # If disabled, send directly the info that is sent to the LLM.
        # This is meant to test the bot without consuming LLM tokens.
        self.response_use_llm: bool = False
        # Define the personality, who is the bot,the initial context and extra rules for the LLM.
        self.initial_context: str = ""
        # This does not affect any of the initial context or rules, just limits the size of the stored context.
        # When the limit is reached, the context is reset to initial_context.
        self.max_context_length: int = 12000
        # Maximum tokens for the LLM response.
        self.max_tokens_response: int = 500
        # Which channels the bot is allowed to operate in. Empty list means all channels are allowed.
        self.allowed_channels = []
        # Channels used for testing purposes.
        # You may want to include one to send private commands to the bot.
        self.test_channels = []


    def read(self, path: str = "config/config.json") -> "Config":
        config_path = Path(path)

        if not config_path.exists():
            return self.generate_default(path)

        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading config file: {e}")
            return Config()

        self.response_use_llm = data.get("response_use_llm", self.response_use_llm)
        self.max_context_length = data.get("max_context_length", self.max_context_length)
        self.max_tokens_response = data.get("max_tokens_response", self.max_tokens_response)
        self.allowed_channels = data.get("allowed_channels", self.allowed_channels)
        self.test_channels = data.get("test_channels", self.test_channels)

        # Load external context file if present
        context_file = data.get("context_file")
        if context_file:
            context_path = Path(config_path.parent / context_file)
            if not context_path.exists():
                raise FileNotFoundError(f"Context file not found: {context_path}")

            self.initial_context = context_path.read_text(encoding="utf-8")

        return self

    def generate_default(self, path: str = "config/config.json"):
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if not config_path.exists():
            config_path.write_text(self.to_json(), encoding="utf-8")
            print(f"[Config] Created default config at {config_path}")

        context_path = config_path.parent / "context.txt"
        if not context_path.exists():
            context_path.write_text("Default initial context.\n", encoding="utf-8")
            print(f"[Config] Created default context at {context_path}")

        self.initial_context = context_path.read_text(encoding="utf-8")

        return self

    def to_dict(self) -> dict:
        return {
            "response_use_llm": self.response_use_llm,
            "max_context_length": self.max_context_length,
            "max_tokens_response": self.max_tokens_response,
            "allowed_channels": self.allowed_channels,
            "test_channels": self.test_channels,
            "context_file": "context.txt",
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
