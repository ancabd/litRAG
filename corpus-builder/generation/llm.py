"""A minimal LLM interface, one provider (Anthropic), and an on-disk response cache.

Everything that calls a model (answering, judging, later the agent) goes through `LLM.complete`,
so swapping providers or models is one class, and every call is cached and accounted for.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path

# $ per million tokens (input, output), from the Claude models overview. Used for cost estimates only.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
}
DEFAULT_MODEL = "claude-sonnet-5-5"


class LLMNotConfigured(RuntimeError):
    """No API key (or SDK) for the selected provider."""


class LLMError(RuntimeError):
    """The provider returned an error."""


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    cached: bool = False

    @property
    def cost(self) -> float | None:
        price = PRICES.get(self.model)
        if price is None or self.cached:
            return 0.0 if self.cached else None
        return (self.input_tokens * price[0] + self.output_tokens * price[1]) / 1e6


class LLM(ABC):
    provider: str = "base"

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        ...

    def config(self) -> dict:
        return {"provider": self.provider, "model": self.model}


class AnthropicLLM(LLM):
    provider = "anthropic"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, timeout: float = 120.0):
        super().__init__(model)
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMNotConfigured("No ANTHROPIC_API_KEY set. Create a key at https://platform.claude.com and "
                                   "export ANTHROPIC_API_KEY=... before starting (or pass --api-key).")
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - dependency is in requirements.txt
            raise LLMNotConfigured("The anthropic package is missing: pip install anthropic") from exc
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=key, timeout=timeout, max_retries=3)

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        t0 = time.perf_counter()
        try:
            msg = self.client.messages.create(model=self.model, max_tokens=max_tokens, system=system,
                                              messages=[{"role": "user", "content": prompt}])
        except self._anthropic.APIError as exc:
            raise LLMError(f"Anthropic API error: {exc}") from exc
        text = "".join(getattr(b, "text", "") for b in msg.content)
        return LLMResponse(text=text, model=self.model, input_tokens=msg.usage.input_tokens,
                           output_tokens=msg.usage.output_tokens, seconds=time.perf_counter() - t0)


class CachedLLM(LLM):
    """Wraps an LLM; identical requests (model + prompts + max_tokens) are answered from disk.

    Makes re-running evals free and repeatable. Delete the cache folder to force fresh calls.
    """

    def __init__(self, inner: LLM, cache_dir: Path):
        super().__init__(inner.model)
        self.inner, self.cache_dir = inner, Path(cache_dir)
        self.provider = inner.provider
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, system: str, prompt: str, max_tokens: int) -> Path:
        key = json.dumps([self.inner.provider, self.inner.model, system, prompt, max_tokens])
        return self.cache_dir / f"{hashlib.sha256(key.encode()).hexdigest()[:32]}.json"

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        path = self._path(system, prompt, max_tokens)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return LLMResponse(**{**data, "cached": True, "seconds": 0.0})
            except (ValueError, TypeError):
                pass  # corrupt cache entry: fetch again
        r = self.inner.complete(system, prompt, max_tokens)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(r)), encoding="utf-8")
        tmp.replace(path)
        return r

    def config(self) -> dict:
        return self.inner.config()


class ScriptedLLM(LLM):
    """For tests: returns responses from a function of (system, prompt). No network."""

    provider = "scripted"

    def __init__(self, respond, model: str = "scripted"):
        super().__init__(model)
        self.respond = respond
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        self.calls.append((system, prompt))
        return LLMResponse(text=self.respond(system, prompt), model=self.model, input_tokens=len(prompt) // 4,
                           output_tokens=50)


def make_llm(model: str = DEFAULT_MODEL, cache_dir: Path | None = None, api_key: str | None = None) -> LLM:
    llm: LLM = AnthropicLLM(model, api_key=api_key)
    return CachedLLM(llm, cache_dir) if cache_dir else llm


def parse_json(text: str) -> dict | None:
    """The first JSON object in a model response (tolerates ```json fences and surrounding prose)."""
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                        return obj if isinstance(obj, dict) else None
                    except ValueError:
                        break
        start = text.find("{", start + 1)
    return None
