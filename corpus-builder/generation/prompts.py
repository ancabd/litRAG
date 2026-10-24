"""Prompts, versioned. Bump a version whenever its text changes: versions are stored with every
answer and eval run, so results from different prompts are never silently compared."""

ANSWER_VERSION = "answer-v1"

ANSWER_SYSTEM = """You answer questions about scientific papers using only the passages you are given.

Rules:
1. Use only information stated in the passages. Do not add facts from your own knowledge, even if you are sure of them.
2. Cite every claim with the id of the passage that supports it, in square brackets, e.g. [W2025444507#003]. Use only ids that appear in the passages. A sentence may cite several passages: [W1#002][W2#010].
3. If the passages do not contain the answer, say so plainly and set "answerable" to false. Do not guess. If they answer only part of the question, answer that part and say what is missing.
4. Be concise: usually 1 to 4 sentences. Keep the paper's technical terms; write formulas in plain text.

Respond with only a JSON object, no other text:
{"answerable": true or false, "answer": "your answer with [passage-id] citations"}"""


def format_passages(passages: list[dict]) -> str:
    blocks = []
    for c in passages:
        where = c.get("section") or ""
        if c.get("page_start"):
            where += f", p. {c['page_start']}"
        head = f"[{c['chunk_id']}] {c.get('title') or c['paper_id']}"
        if c.get("year"):
            head += f" ({c['year']})"
        if where:
            head += f" - {where}"
        blocks.append(f"{head}\n{c['text']}")
    return "\n\n".join(blocks)


def answer_prompt(question: str, passages: list[dict]) -> str:
    return f"Question: {question}\n\nPassages:\n\n{format_passages(passages)}"


JUDGE_VERSION = "judge-v1"

CORRECTNESS_SYSTEM = """You grade answers to questions about scientific papers against a reference answer written by an expert.

Grade only factual agreement with the reference:
- "correct": contains the key facts of the reference and nothing that contradicts it. Extra correct detail, different wording or a different level of detail are fine.
- "partial": gets some key facts right but misses others, or is vague where the reference is specific.
- "incorrect": contradicts the reference, misses its main point, or declines to answer when the reference has an answer.

Ignore citations and style. Respond with only a JSON object:
{"verdict": "correct" | "partial" | "incorrect", "reason": "one sentence"}"""


def correctness_prompt(question: str, reference: str, answer: str) -> str:
    return f"Question: {question}\n\nReference answer: {reference}\n\nAnswer to grade: {answer}"


SUPPORT_SYSTEM = """You check whether an answer is supported by the passages it cites.

For each claim in the answer, check whether the cited passages state it. Judge only support by these passages, not whether the claim is true in general.
- "supported": every claim is stated in, or directly follows from, the cited passages.
- "partial": some claims are supported, others are not.
- "unsupported": the main claims are not in the cited passages, or nothing is cited.

Respond with only a JSON object:
{"verdict": "supported" | "partial" | "unsupported", "reason": "one sentence naming any unsupported claim"}"""


def support_prompt(answer: str, cited: list[dict]) -> str:
    passages = format_passages(cited) if cited else "(no passages cited)"
    return f"Answer: {answer}\n\nCited passages:\n\n{passages}"
