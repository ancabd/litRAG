"""Where the Anthropic API key comes from, and saving one entered in the app.

Order (first one set wins):
  1. a key set in the running app ("this session"): replaces the others until the server restarts
  2. the ANTHROPIC_API_KEY environment variable
  3. a saved key: ~/.config/litrag/credentials.json (override with LITRAG_KEY_FILE)

The saved file lives in your user folder, not the repository, so it can't be committed by
accident, and it is written with permissions 600 (only you can read it). The key is never
sent anywhere except to Anthropic, and the app never shows it again after it is saved: status
calls return only where it came from and its last four characters.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

_session_key: str | None = None
_lock = threading.Lock()


def key_file() -> Path:
    override = os.environ.get("LITRAG_KEY_FILE")
    return Path(override).expanduser() if override else Path.home() / ".config" / "litrag" / "credentials.json"


def saved_key() -> str | None:
    try:
        data = json.loads(key_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    key = data.get("anthropic_api_key") if isinstance(data, dict) else None
    return key.strip() if isinstance(key, str) and key.strip() else None


def current_key() -> tuple[str | None, str | None]:
    """-> (key, source) with source "session", "environment", "saved" or None."""
    if _session_key:
        return _session_key, "session"
    env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env:
        return env, "environment"
    saved = saved_key()
    if saved:
        return saved, "saved"
    return None, None


def status() -> dict:
    key, source = current_key()
    return {"configured": bool(key), "source": source, "hint": f"…{key[-4:]}" if key and len(key) > 8 else None,
            "saved": saved_key() is not None, "environment": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
            "key_file": str(key_file())}


def set_key(key: str, remember: bool) -> None:
    """Use `key` from now on; with `remember`, also save it for later runs (the CLI uses it too)."""
    global _session_key
    key = key.strip()
    with _lock:
        _session_key = key
        if remember:
            path = key_file()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump({"anthropic_api_key": key}, fh)
            os.replace(tmp, path)
            os.chmod(path, 0o600)


def clear_key() -> None:
    """Forget the session key and delete the saved one. An environment variable can't be removed from here."""
    global _session_key
    with _lock:
        _session_key = None
        try:
            key_file().unlink()
        except FileNotFoundError:
            pass


def check_key(key: str, timeout: float = 15.0) -> None:
    """Ask Anthropic whether the key works (lists models: no tokens, no cost).

    Raises ValueError if the key is rejected, LLMError if Anthropic can't be reached.
    """
    from .llm import LLMError, LLMNotConfigured
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise LLMNotConfigured("The anthropic package is missing: pip install anthropic") from exc
    client = anthropic.Anthropic(api_key=key.strip(), timeout=timeout, max_retries=1)
    try:
        client.models.list(limit=1)
    except anthropic.AuthenticationError as exc:
        raise ValueError("Anthropic rejected this key. Check that you copied all of it and that it hasn't been revoked.") from exc
    except anthropic.PermissionDeniedError as exc:
        raise ValueError("This key isn't allowed to use the API (permission denied).") from exc
    except anthropic.APIError as exc:
        raise LLMError(f"Couldn't reach Anthropic to check the key: {exc}") from exc


__all__ = ["check_key", "clear_key", "current_key", "key_file", "saved_key", "set_key", "status"]
