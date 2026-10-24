"""A minimal LLM interface, one provider (Anthropic), and an on-disk response cache.

Everything that calls a model goes through one of two methods, so swapping providers or models is
one class, and every call is cached and accounted for:

  complete(system, prompt)              one prompt in, text out (answering, judging)
  chat(system, messages, tools)         a conversation with tool use (the agent)

Messages and content blocks use the Anthropic shape, as plain dicts:
  {"role": "user" | "assistant", "content": str | [blocks]}
  blocks: {"type": "text", "text"} | {"type": "tool_use", "id", "name", "input"}
          | {"type": "tool_result", "tool_use_id", "content", "is_error"?}
Tools: {"name", "description", "input_schema": <JSON schema>}.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path

# $ per million tokens (input, output), from the Claude models overview. Used for cost estimates only.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
}
DEFAULT_MODEL = "claude-sonnet-5-5"
# Prompt caching (chat(..., cache=True)): writes cost 1.25x the input price (5-minute cache), reads a
# fraction of it, per the prompt caching docs. Haiku's prices for prompts over 100K tokens are ignored.
CACHE_WRITE = 1.25
CACHE_READ = {"claude-fable-5-1": 0.025, "claude-opus-5-5": 0.05, "claude-sonnet-5-5": 0.05, "claude-haiku-5-5": 0.1}


class LLMNotConfigured(RuntimeError):
    """No API key (or SDK) for the selected provider."""


class LLMError(RuntimeError):
    """The provider returned an error."""


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0          # all input tokens, including the cache reads and writes below
    output_tokens: int = 0
    seconds: float = 0.0
    cached: bool = False           # answered from our on-disk cache (free), not the provider's prompt cache
    cache_read_tokens: int = 0     # provider prompt cache: input tokens read from it (cheap)
    cache_write_tokens: int = 0    # ... and written to it (a little more than normal input)
    # chat() only: the assistant turn as content blocks (append it to the messages to continue),
    # the tool calls in it, and why the model stopped ("end_turn", "tool_use", "max_tokens", ...)
    content: list[dict] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str | None = None

    def message(self) -> dict:
        """This response as an assistant message, to append to the conversation."""
        blocks = [b for b in self.content if not (b.get("type") == "text" and not b.get("text"))]
        return {"role": "assistant", "content": blocks or [{"type": "text", "text": self.text or "(no answer)"}]}

    @property
    def cost(self) -> float | None:
        price = PRICES.get(self.model)
        if price is None or self.cached:
            return 0.0 if self.cached else None
        plain = self.input_tokens - self.cache_read_tokens - self.cache_write_tokens
        inp = (plain + self.cache_write_tokens * CACHE_WRITE
               + self.cache_read_tokens * CACHE_READ.get(self.model, 0.1)) * price[0]
        return (inp + self.output_tokens * price[1]) / 1e6


class LLM(ABC):
    provider: str = "base"

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        ...

    def chat(self, system: str, messages: list[dict], tools: list[dict] | None = None,
             max_tokens: int = 1024, cache: bool = False) -> LLMResponse:
        """One assistant turn. `cache=True` turns on the provider's prompt caching, so a growing
        conversation (an agent loop) pays full price for each part of it only once."""
        raise NotImplementedError(f"{type(self).__name__} does not support tool use")

    def config(self) -> dict:
        return {"provider": self.provider, "model": self.model}


def _block(b) -> dict:
    """An SDK content block as a plain dict (only the fields that are sent back)."""
    if b.type == "text":
        return {"type": "text", "text": b.text}
    if b.type == "tool_use":
        return {"type": "tool_use", "id": b.id, "name": b.name, "input": dict(b.input or {})}
    return b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else {"type": b.type}


def _from_blocks(blocks: list[dict]) -> tuple[str, list[ToolCall]]:
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    calls = [ToolCall(b["id"], b["name"], b.get("input") or {}) for b in blocks if b.get("type") == "tool_use"]
    return text, calls


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

    def chat(self, system: str, messages: list[dict], tools: list[dict] | None = None,
             max_tokens: int = 1024, cache: bool = False) -> LLMResponse:
        t0 = time.perf_counter()
        kwargs: dict = {"tools": tools} if tools else {}
        if cache:
            kwargs["cache_control"] = {"type": "ephemeral"}  # automatic caching: breakpoint moves with the conversation
        try:
            msg = self.client.messages.create(model=self.model, max_tokens=max_tokens, system=system,
                                              messages=messages, **kwargs)
        except self._anthropic.APIError as exc:
            raise LLMError(f"Anthropic API error: {exc}") from exc
        content = [_block(b) for b in msg.content]
        text, calls = _from_blocks(content)
        u = msg.usage
        read = getattr(u, "cache_read_input_tokens", 0) or 0
        write = getattr(u, "cache_creation_input_tokens", 0) or 0
        return LLMResponse(text=text, model=self.model, input_tokens=u.input_tokens + read + write,
                           output_tokens=u.output_tokens, seconds=time.perf_counter() - t0,
                           cache_read_tokens=read, cache_write_tokens=write,
                           content=content, tool_calls=calls, stop_reason=msg.stop_reason)


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

    def _get(self, path: Path) -> LLMResponse | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["tool_calls"] = [ToolCall(**t) for t in data.get("tool_calls") or []]
            return LLMResponse(**{**data, "cached": True, "seconds": 0.0})
        except (ValueError, TypeError):
            return None  # corrupt cache entry: fetch again

    def _put(self, path: Path, r: LLMResponse) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(r)), encoding="utf-8")
        tmp.replace(path)

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        path = self._path(system, prompt, max_tokens)
        r = self._get(path)
        if r is None:
            r = self.inner.complete(system, prompt, max_tokens)
            self._put(path, r)
        return r

    def chat(self, system: str, messages: list[dict], tools: list[dict] | None = None,
             max_tokens: int = 1024, cache: bool = False) -> LLMResponse:
        # `cache` doesn't change the response, so it isn't part of the key
        key = json.dumps(["chat", self.inner.provider, self.inner.model, system, messages, tools, max_tokens],
                         sort_keys=True)
        path = self.cache_dir / f"{hashlib.sha256(key.encode()).hexdigest()[:32]}.json"
        r = self._get(path)
        if r is None:
            r = self.inner.chat(system, messages, tools, max_tokens, cache)
            self._put(path, r)
        return r

    def config(self) -> dict:
        return self.inner.config()


class ScriptedLLM(LLM):
    """For tests: no network.

    complete(): `respond(system, prompt)` returns the text.
    chat():     `chat_respond(system, messages, tools)` returns a string (a final text answer), or
                {"text": ..., "tool_calls": [{"name": ..., "input": {...}}, ...]}; ids are generated.
    """

    provider = "scripted"

    def __init__(self, respond=None, model: str = "scripted", chat_respond=None):
        super().__init__(model)
        self.respond, self.chat_respond = respond, chat_respond
        self.calls: list[tuple[str, str]] = []
        self.chats: list[list[dict]] = []

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        self.calls.append((system, prompt))
        return LLMResponse(text=self.respond(system, prompt), model=self.model, input_tokens=len(prompt) // 4,
                           output_tokens=50)

    def chat(self, system: str, messages: list[dict], tools: list[dict] | None = None,
             max_tokens: int = 1024, cache: bool = False) -> LLMResponse:
        if self.chat_respond is None:
            raise NotImplementedError("ScriptedLLM was created without chat_respond")
        self.chats.append(json.loads(json.dumps(messages)))
        out = self.chat_respond(system, messages, tools)
        out = {"text": out} if isinstance(out, str) else out
        n = len(self.chats)
        content = [{"type": "text", "text": out["text"]}] if out.get("text") else []
        content += [{"type": "tool_use", "id": f"toolu_{n:03d}_{i}", "name": t["name"], "input": t.get("input") or {}}
                    for i, t in enumerate(out.get("tool_calls") or [])]
        text, calls = _from_blocks(content)
        size = len(json.dumps(messages)) // 4
        return LLMResponse(text=text, model=self.model, input_tokens=size, output_tokens=50, content=content,
                           tool_calls=calls, stop_reason="tool_use" if calls else "end_turn")


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
