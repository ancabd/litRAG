"""Keep tests away from your real API key: no environment key, no saved key, no session key."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def isolated_keys(tmp_path, monkeypatch):
    from generation import keys
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("LITRAG_KEY_FILE", str(tmp_path / "litrag-credentials.json"))
    monkeypatch.setattr(keys, "_session_key", None)
    yield keys
