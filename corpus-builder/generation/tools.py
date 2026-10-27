"""The agent's tools: thin wrappers over Library methods that return text for the model.

Each tool has a name, a description and a JSON schema (what the model sees), and a `run` that
does the work and reports which passages the model has now read. Passages are shown to the
model in full once; if a later result contains a passage it already read, only its id and
heading are repeated, which keeps the conversation (and the cost) from growing needlessly.

To add a tool: write a Tool subclass and add it to TOOLS (and to AgentGenerator's default
list if it should be on by default).
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .prompts import format_passages

if TYPE_CHECKING:
    from library import Library

MAX_K = 10          # most passages one search may return
MAX_AROUND = 3      # most passages read_around may add on each side


def plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


@dataclass
class ToolContext:
    library: "Library"
    retriever: str = "bm25"
    k: int = 5                                   # default passages per search
    seen: set[str] = field(default_factory=set)  # chunk ids already shown in full


@dataclass
class ToolResult:
    text: str                                    # what the model sees
    chunks: list[str] = field(default_factory=list)  # passages in this result (new and repeated)
    new: list[str] = field(default_factory=list)     # passages shown in full for the first time
    scores: dict[str, float] = field(default_factory=dict)
    is_error: bool = False
    note: str = ""                               # one line for the trace, e.g. "5 passages, 3 new"


def show(ctx: ToolContext, chunks: list[dict]) -> tuple[str, list[str]]:
    """Format passages, in full the first time and as a one-line reminder after that."""
    parts, new = [], []
    for c in chunks:
        if c["chunk_id"] in ctx.seen:
            title = c.get("title") or c["paper_id"]
            parts.append(f"[{c['chunk_id']}] {title} - {c.get('section') or ''} (already shown above)")
        else:
            parts.append(format_passages([c]))
            new.append(c["chunk_id"])
            ctx.seen.add(c["chunk_id"])
    return "\n\n".join(parts), new


class Tool(ABC):
    name: str
    description: str
    input_schema: dict

    def spec(self, ctx: "ToolContext | None" = None) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}

    @abstractmethod
    def run(self, ctx: ToolContext, args: dict) -> ToolResult:
        ...


class Search(Tool):
    name = "search"
    description = ("Keyword search (BM25) over all passages of all papers. Returns the best-matching passages "
                   "with their ids. Use the words a paper would use. Optionally restrict to one paper or to "
                   "papers from a year onwards.")
    KIND = {"dense": "Semantic search", "hybrid": "Keyword and semantic search"}
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search terms."},
            "k": {"type": "integer", "minimum": 1, "maximum": MAX_K, "description": "Number of passages."},
            "paper_id": {"type": "string", "description": "Only search this paper (an id like W2042658765)."},
            "year_from": {"type": "integer", "description": "Only papers published in or after this year."},
        },
        "required": ["query"],
    }

    def spec(self, ctx=None):
        spec = super().spec()
        if ctx is not None:  # say what the default actually is in this run, and what kind of search it is
            kind = self.KIND.get(ctx.retriever.split(":")[0])
            if kind:
                spec["description"] = spec["description"].replace("Keyword search (BM25)", kind).replace(
                    " Use the words a paper would use.", "")
            schema = json.loads(json.dumps(spec["input_schema"]))
            schema["properties"]["k"]["description"] = f"Number of passages (default {min(ctx.k, MAX_K)})."
            spec["input_schema"] = schema
        return spec

    def run(self, ctx, args):
        query = str(args.get("query") or "").strip()
        if not query:
            return ToolResult("search needs a query.", is_error=True, note="no query")
        k = max(1, min(int(args.get("k") or ctx.k), MAX_K))  # default: the run's k, as for single shot
        paper = args.get("paper_id") or None
        if paper and ctx.library.paper(paper) is None:
            return ToolResult(f"No paper with id {paper}.", is_error=True, note=f"unknown paper {paper}")
        hits = ctx.library.search(query, k=k, retriever=ctx.retriever, paper=paper, year_from=args.get("year_from"))
        if not hits:
            return ToolResult("No passages matched. Try other words.", note="no results")
        chunks = [ctx.library.chunk(h.chunk_id) for h in hits]
        text, new = show(ctx, chunks)
        return ToolResult(text, [c["chunk_id"] for c in chunks], new,
                          {h.chunk_id: h.score for h in hits}, note=f"{plural(len(chunks), 'passage')}, {len(new)} new")


class ReadAround(Tool):
    name = "read_around"
    description = ("The passages just before and after a passage in the same paper, in reading order. Use it "
                   "when a passage is cut off or you need its context.")
    input_schema = {
        "type": "object",
        "properties": {
            "chunk_id": {"type": "string", "description": "A passage id from an earlier result."},
            "before": {"type": "integer", "minimum": 0, "maximum": MAX_AROUND, "description": "Default 1."},
            "after": {"type": "integer", "minimum": 0, "maximum": MAX_AROUND, "description": "Default 1."},
        },
        "required": ["chunk_id"],
    }

    def run(self, ctx, args):
        cid = str(args.get("chunk_id") or "").strip().strip("[]")
        if ctx.library.chunk(cid) is None:
            return ToolResult(f"No passage with id {cid}.", is_error=True, note=f"unknown passage {cid}")
        clamp = lambda v: max(0, min(int(v if v is not None else 1), MAX_AROUND))  # noqa: E731
        chunks = ctx.library.neighbours(cid, clamp(args.get("before")), clamp(args.get("after")))
        text, new = show(ctx, chunks)
        return ToolResult(text, [c["chunk_id"] for c in chunks], new, note=f"{plural(len(chunks), 'passage')}, {len(new)} new")


class OpenPaper(Tool):
    name = "open_paper"
    description = ("A paper's title, authors, year, abstract and its list of sections (each with the id of its "
                   "first passage, which read_around can continue from). Use it to find where in a paper to look.")
    input_schema = {
        "type": "object",
        "properties": {"paper_id": {"type": "string", "description": "A paper id like W2042658765."}},
        "required": ["paper_id"],
    }

    def run(self, ctx, args):
        pid = str(args.get("paper_id") or "").strip()
        if "#" in pid:            # a passage id was given: open its paper
            pid = pid.split("#")[0]
        p = ctx.library.paper(pid)
        if p is None:
            return ToolResult(f"No paper with id {pid}.", is_error=True, note=f"unknown paper {pid}")
        lines = [f"{p['title']} ({p.get('year')}), {p.get('authors') or 'unknown authors'}. Paper id {pid}.",
                 "Full text available." if p["source"] == "pdf" else "Only the abstract is available."]
        abstract = [c for c in ctx.library.section_chunks(pid, "Abstract")][:1]
        text, new = show(ctx, abstract) if abstract else ("", [])
        if text:
            lines += ["", "Abstract:", text]
        if p["source"] == "pdf":
            lines += ["", "Sections (first passage id, number of passages):"]
            lines += [f"- {s['section']} ({s['first_chunk']}, {s['n_chunks']})" for s in p["sections"]]
        return ToolResult("\n".join(lines), [c["chunk_id"] for c in abstract], new,
                          note=plural(len(p["sections"]), "section"))


GIVE_UP_TOOL = {
    "name": "give_up",
    "description": "Say that the papers do not answer the question, and why. Ends your work.",
    "input_schema": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]},
}

TOOLS: dict[str, Tool] = {t.name: t for t in (Search(), ReadAround(), OpenPaper())}

__all__ = ["GIVE_UP_TOOL", "TOOLS", "Tool", "ToolContext", "ToolResult"]
