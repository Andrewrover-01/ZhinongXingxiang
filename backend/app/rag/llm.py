"""
Thin LLM wrapper.

When ``OPENAI_API_KEY`` is set the wrapper calls the OpenAI Chat API.
Otherwise it falls back to a *no-key* response that formats the retrieved
knowledge documents into a readable answer, making the system fully usable
even without an API key.
"""

from __future__ import annotations

import textwrap
from typing import Any, AsyncGenerator, Dict, List

from app.core.config import settings

# Maximum context window we send to the LLM
_MAX_CONTEXT_CHARS = 4000


def _format_sources(sources: List[Dict[str, Any]]) -> str:
    parts = []
    for i, src in enumerate(sources, 1):
        meta = src.get("metadata", {})
        title = meta.get("title", f"文档{i}")
        content = src.get("document", "")[:500]
        parts.append(f"【{i}】{title}\n{content}")
    return "\n\n".join(parts)


def _fallback_answer(query: str, sources: List[Dict[str, Any]]) -> str:
    """
    Format retrieved knowledge as a structured answer without an LLM.
    """
    if not sources:
        return (
            f"抱歉，暂未在知识库中检索到与"{query}"相关的内容。"
            "请尝试换一种描述方式或联系农业技术人员。"
        )
    header = f"根据知识库检索到以下与"{query}"相关的信息：\n"
    body = _format_sources(sources)
    footer = "\n\n以上信息仅供参考，具体防治措施请结合实地情况判断。"
    return header + body + footer


async def _fallback_stream(
    query: str, sources: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    """Yield the fallback answer character-by-character for SSE demo."""
    answer = _fallback_answer(query, sources)
    chunk_size = 10
    for i in range(0, len(answer), chunk_size):
        yield answer[i : i + chunk_size]


class LLMClient:
    """
    Async LLM client that supports both streaming and non-streaming calls.
    """

    def __init__(self) -> None:
        self._has_key = bool(settings.OPENAI_API_KEY)

    # ── Non-streaming ──────────────────────────────────────────────────────────

    async def complete(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        system_prompt: str | None = None,
    ) -> str:
        if not self._has_key:
            return _fallback_answer(query, sources)

        from openai import AsyncOpenAI  # lazy import

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        context = _format_sources(sources)[:_MAX_CONTEXT_CHARS]
        messages = [
            {
                "role": "system",
                "content": system_prompt
                or (
                    "你是一位专业的农业技术专家。请根据以下知识库内容回答农民的问题，"
                    "回答要准确、通俗易懂，并给出具体的操作建议。"
                    "若知识库内容不足，请如实告知并建议咨询专业人员。"
                ),
            },
            {
                "role": "user",
                "content": f"参考资料：\n{context}\n\n农民问题：{query}",
            },
        ]
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
            temperature=0.3,
            max_tokens=1024,
        )
        return resp.choices[0].message.content or ""

    # ── Streaming ─────────────────────────────────────────────────────────────

    async def stream(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        if not self._has_key:
            async for chunk in _fallback_stream(query, sources):
                yield chunk
            return

        from openai import AsyncOpenAI  # lazy import

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        context = _format_sources(sources)[:_MAX_CONTEXT_CHARS]
        messages = [
            {
                "role": "system",
                "content": system_prompt
                or (
                    "你是一位专业的农业政策顾问和技术专家。"
                    "请根据参考资料，用通俗易懂的语言回答农民的问题。"
                ),
            },
            {
                "role": "user",
                "content": f"参考资料：\n{context}\n\n问题：{query}",
            },
        ]
        async with await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        ) as stream_resp:
            async for chunk in stream_resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta


# Module-level singleton
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
