import sys
import json
import pytest
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from Config import Config


@pytest.fixture
def mock(tmp_path):
    config_dir = tmp_path / "config"
    config_path = config_dir / "config.json"
    context_path = config_dir / "context.txt"

    return SimpleNamespace(
        config_dir=config_dir,
        config_path=config_path,
        context_path=context_path,
    )


def test_generate_default_config_creates_files(mock):
    cfg = Config()
    cfg.generate_default(str(mock.config_path))

    assert mock.config_path.exists()
    assert mock.context_path.exists()

    content = mock.config_path.read_text(encoding="utf-8")
    assert '"max_context_length"' in content
    assert '"max_tokens_response"' in content

    ctx = mock.context_path.read_text(encoding="utf-8")
    assert "Default initial context" in ctx

def test_read_generates_default_config_if_missing(mock):
    cfg = Config().read(str(mock.config_path))

    assert mock.config_path.exists()
    assert mock.context_path.exists()
    assert cfg.initial_context

def test_read_loads_basic_values(mock):
    mock.config_dir.mkdir()

    mock.config_path.write_text(
        json.dumps({
            "response_use_llm": True,
            "max_context_length": 42,
            "max_tokens_response": 123,
            "allowed_channels": ["general"],
            "test_channels": ["test"]
        }),
        encoding="utf-8"
    )
    cfg = Config().read(str(mock.config_path))

    assert cfg.response_use_llm is True
    assert cfg.max_context_length == 42
    assert cfg.max_tokens_response == 123
    assert cfg.allowed_channels == ["general"]
    assert cfg.test_channels == ["test"]

def test_read_loads_external_context_file(mock):
    mock.config_dir.mkdir()
    mock.context_path.write_text("HELLO CONTEXT\n", encoding="utf-8")
    mock.config_path.write_text(json.dumps({ "context_file": "context.txt" }), encoding="utf-8")
    cfg = Config().read(str(mock.config_path))

    assert cfg.initial_context == "HELLO CONTEXT\n"

def test_read_raises_if_context_file_missing(mock):
    mock.config_dir.mkdir()
    mock.config_path.write_text(
        json.dumps({"context_file": "missing.txt"}), encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        Config().read(str(mock.config_path))

