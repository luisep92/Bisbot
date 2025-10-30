# Bisbot - Discord Voice Bot with David Bisbal's Personality

A Discord bot that joins voice channels and has spoken conversations with the voice and personality of Spanish singer David Bisbal. Built with Python, using open-source AI models for voice cloning and speech recognition.

## Features

- Joins Discord voice channels on command
- Listens to voice chat and transcribes speech (Spanish)
- Generates responses in David Bisbal's personality with characteristic expressions
- Speaks responses using cloned voice synthesis
- Maintains conversation context
- Modular architecture with swappable components

## David Bisbal Personality

The bot speaks with:
- Passionate enthusiasm and warmth
- Andalusian expressions ("mu", "to", "zeaza")
- Characteristic phrases: "Ayyy!", "Buleria!", "Ave Maria!", "Corazon partio!"
- Signature greeting: "Lo primero de todo, como estan los makinas?"
- References to Almeria and his songs

## Architecture

The project follows a clean, modular architecture:

```
Bisbot/
├── interfaces/              # Abstract interfaces
│   ├── ai_interface.py      # AI conversation interface
│   ├── voice_interface.py   # Voice synthesis interface
│   └── stt_interface.py     # Speech-to-text interface
├── bisbal_personality.py    # Bisbal AI implementation
├── voice_handler.py         # XTTS voice synthesis
├── stt_handler.py          # Whisper speech recognition
├── bot.py                  # Main Discord bot
├── tests/                  # Integration tests
├── requirements.txt        # Python dependencies
└── .env.example           # Configuration template
```

Each component has:
1. Abstract interface defining the contract
2. Concrete implementation
3. Integration tests to verify functionality

## Requirements

### System Requirements

- Python 3.9 or higher
- FFmpeg (for audio processing)
- CUDA-capable GPU (recommended but not required)
- 4GB+ RAM (8GB+ recommended for voice synthesis)

### Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### API Keys / Services

Choose ONE AI option:

**Option 1: Anthropic Claude (Recommended)**
- Best quality responses
- Free tier available at https://console.anthropic.com/
- Requires API key

**Option 2: Ollama (Free, Local)**
- No API key needed
- Runs locally on your machine
- Install from https://ollama.ai/
- Run: `ollama pull llama2`

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/luisep92/Bisbot.git
cd Bisbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will download:
- Discord.py with voice support
- Coqui XTTS v2 (~2GB model)
- OpenAI Whisper (~1-5GB depending on model size)
- PyTorch and other dependencies

**Note:** First run will download AI models automatically.

### 4. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Enable these Privileged Gateway Intents:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
   - PRESENCE INTENT
6. Copy bot token

### 5. Invite Bot to Server

Generate invite URL with these permissions:
- Read Messages/View Channels
- Send Messages
- Connect (voice)
- Speak (voice)
- Use Voice Activity

Permissions integer: `36768768`

Invite URL template:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=36768768&scope=bot
```

### 6. Configure Environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Set required variables:
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
ANTHROPIC_API_KEY=your_anthropic_key_here  # or use Ollama
BISBAL_VOICE_SAMPLE=data/bisbal_voice_sample.wav
WHISPER_MODEL=base
```

### 7. Prepare Voice Sample

**IMPORTANT:** You must provide a David Bisbal voice sample for voice cloning.

Requirements:
- 10-30 seconds of clean speech
- WAV or MP3 format
- No background music/noise
- Spanish language

Where to find:
1. YouTube interviews (extract audio)
2. Acapella recordings
3. Speech-only clips

Save as: `data/bisbal_voice_sample.wav`

```bash
mkdir -p data
# Place your audio file here
```

### 8. Run Tests

Verify installation:

```bash
pytest tests/ -v
```

Tests will verify:
- All interfaces are properly implemented
- Components initialize correctly
- Basic functionality works

**Note:** Some tests may be skipped if:
- API keys not configured
- Voice sample not provided
- Models not downloaded yet

## Usage

### Start the Bot

```bash
python bot.py
```

Expected output:
```
Loading XTTS model on cuda...
Loading Whisper base model on cuda...
Bisbal Bot logged in as BisbalBot#1234
Bot is in 1 guild(s)
Ready to join voice channels!
```

### Discord Commands

Once bot is online:

**!join** - Bot joins your current voice channel
```
User: !join
Bot: "Lo primero de todo, como estan los makinas? Ya estoy aqui en General!"
```

**!leave** - Bot leaves voice channel
```
User: !leave
Bot: "Hasta luego, makinas! Que vaya bien!"
```

### Voice Interaction

1. Use `!join` command while in a voice channel
2. Speak in Spanish
3. Bot will:
   - Transcribe your speech
   - Generate a Bisbal-style response
   - Speak the response in cloned voice
4. Continue conversation naturally

### Example Conversation

```
User (speaks): "Hola David!"
Bot (speaks): "Lo primero de todo, como estan los makinas? Ayyy, que alegria!"

User (speaks): "Como estas?"
Bot (speaks): "Pues mu bien, con una energia que no veas! Esto es pura buleria!"

User (speaks): "Que calor hace hoy"
Bot (speaks): "Ave Maria, zeaza uno aqui! Esto me recuerda a Almeria en verano!"
```

## Configuration Options

### Whisper Model Sizes

Trade-off between speed and accuracy:

| Model  | Size | RAM   | Speed | Accuracy |
|--------|------|-------|-------|----------|
| tiny   | 39M  | ~1GB  | Fast  | Low      |
| base   | 74M  | ~1GB  | Fast  | Good     |
| small  | 244M | ~2GB  | Med   | Better   |
| medium | 769M | ~5GB  | Slow  | Great    |
| large  | 1550M| ~10GB | Slow  | Best     |

**Recommended:** `base` or `small` for real-time Discord bot

### Alternative Implementations

The modular architecture allows swapping components:

#### Use Ollama (Local AI)

1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama2`
3. Edit `bisbal_personality.py`: uncomment Ollama implementation
4. No API key needed

#### Use Edge TTS (No GPU)

1. Install: `pip install edge-tts`
2. Edit `voice_handler.py`: uncomment Edge TTS implementation
3. Faster but no voice cloning (Spanish accent only)

#### Use Google STT (Cloud)

1. Install: `pip install SpeechRecognition`
2. Edit `stt_handler.py`: uncomment Google STT implementation
3. No GPU needed but requires internet

## Troubleshooting

### Bot doesn't respond to voice

Discord.py voice receiving requires additional setup:
- Install PyNaCl: `pip install PyNaCl`
- May need custom voice sink implementation
- See: https://github.com/Rapptz/discord.py/blob/master/examples/voice_receive.py

Current implementation has placeholder for voice receiving.

### CUDA out of memory

Solutions:
1. Use smaller Whisper model (`tiny` or `base`)
2. Use CPU instead: Comment out CUDA device selection
3. Use alternative implementations (Edge TTS, Google STT)

### Voice synthesis is slow

Options:
1. Use GPU instead of CPU (10x faster)
2. Switch to Edge TTS (faster, no cloning)
3. Pre-generate common responses

### Poor transcription quality

Improvements:
1. Use larger Whisper model (`medium` or `large`)
2. Ensure clean audio input (no background noise)
3. Check microphone quality in Discord settings

### Bot disconnects randomly

Check:
1. Voice channel permissions
2. Discord voice server stability
3. Bot logs for errors

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_personality.py -v

# With output
pytest tests/ -v -s
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New AI Provider:** Implement `AIInterface`
2. **New Voice System:** Implement `VoiceInterface`
3. **New STT System:** Implement `STTInterface`

Example: Adding GPT-4 support

```python
from interfaces.ai_interface import AIInterface

class GPT4Personality(AIInterface):
    # Implement abstract methods
    async def initialize(self): ...
    async def generate_response(self, message, history): ...
    async def cleanup(self): ...
```

Then swap in `bot.py`:
```python
self.ai_handler = GPT4Personality()  # Instead of BisbalPersonality()
```

### Code Style

- All code, comments, and docstrings in English
- No emojis in code
- Follow PEP 8 style guide
- Type hints encouraged
- Comprehensive docstrings required

## Performance Tips

### For Low-End Systems

```bash
# Use minimal models
WHISPER_MODEL=tiny

# Use cloud alternatives in .env
USE_EDGE_TTS=true
USE_GOOGLE_STT=true
```

### For High-End Systems

```bash
# Use best quality models
WHISPER_MODEL=large

# Enable GPU acceleration (automatic if available)
```

### Memory Usage

Typical memory footprint:
- Bot core: ~200MB
- Whisper base: ~1GB
- XTTS: ~2GB
- **Total: ~3-4GB RAM minimum**

## License

This project is for educational purposes. Ensure you have rights to use:
- David Bisbal's voice (voice sample)
- Any audio you process
- Discord's Terms of Service

## Credits

Built with:
- [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Coqui XTTS](https://github.com/coqui-ai/TTS) - Voice cloning
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Anthropic Claude](https://www.anthropic.com/) - Conversational AI

## Support

For issues or questions:
1. Check this README
2. Review test files for examples
3. Check Discord.py documentation
4. Open an issue on GitHub

## Roadmap

Potential improvements:
- [ ] Full voice receiving implementation
- [ ] Multiple personality modes
- [ ] Voice command detection
- [ ] Audio effects (reverb, echo)
- [ ] Web dashboard for configuration
- [ ] Docker containerization
- [ ] Multi-language support
- [ ] Voice activity detection optimization

## Contributing

Contributions welcome! Please:
1. Follow code style guidelines
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

---

Made with passion and enthusiasm... Ave Maria! Buleria!