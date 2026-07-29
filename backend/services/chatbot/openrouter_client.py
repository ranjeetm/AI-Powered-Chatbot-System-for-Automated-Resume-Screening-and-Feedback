from __future__ import annotations

import json
import os
from collections.abc import AsyncGenerator

import httpx
from dotenv import load_dotenv

from backend.core.llm_models import DEFAULT_FALLBACK_MODELS


load_dotenv()


class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ).rstrip("/")
        self.model = os.getenv(
            "OPENROUTER_CHAT_MODEL",
            os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        )
        self.timeout = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "45"))
        self.app_title = os.getenv(
            "OPENROUTER_APP_TITLE",
            "AI Resume Screening ATS",
        )
        self.http_referer = os.getenv(
            "OPENROUTER_HTTP_REFERER",
            "http://localhost:3000",
        )
        self.last_model_used: str | None = None
        self._fallback_models = self._parse_fallback_models()

    def _parse_fallback_models(self) -> list[str]:
        raw = os.getenv("OPENROUTER_FALLBACK_MODELS", "").strip()
        if raw:
            return [m.strip() for m in raw.split(",") if m.strip()]
        return list(DEFAULT_FALLBACK_MODELS)

    @property
    def model_chain(self) -> list[str]:
        chain: list[str] = []
        for model_name in [self.model, *self._fallback_models]:
            if model_name not in chain:
                chain.append(model_name)
        return chain

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        self.last_model_used = None
        last_error: Exception | None = None

        for model_name in self.model_chain:
            payload = self._build_payload(
                model_name,
                messages,
                temperature,
                max_tokens,
                stream=False,
            )
            try:
                data = await self._post(payload)
            except Exception as exc:
                if not self._is_retriable(exc):
                    raise
                last_error = exc
                continue

            choices = data.get("choices") or []
            if not choices:
                last_error = RuntimeError("OpenRouter returned no completion choices")
                continue

            self.last_model_used = model_name
            return self._extract_content(choices[0])

        models = ", ".join(self.model_chain)
        raise RuntimeError(
            f"All OpenRouter models failed ({models}). "
            "Check credits, rate limits, and model availability."
        ) from last_error

    async def stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> AsyncGenerator[str, None]:
        self.last_model_used = None
        last_error: Exception | None = None

        for model_name in self.model_chain:
            payload = self._build_payload(
                model_name,
                messages,
                temperature,
                max_tokens,
                stream=True,
            )
            yielded_any = False

            try:
                async for token in self._stream_payload(payload):
                    yielded_any = True
                    yield token
                self.last_model_used = model_name
                return
            except Exception as exc:
                if yielded_any or not self._is_retriable(exc):
                    raise
                last_error = exc

        models = ", ".join(self.model_chain)
        raise RuntimeError(
            f"All OpenRouter models failed ({models}). "
            "Check credits, rate limits, and model availability."
        ) from last_error

    def _build_payload(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        *,
        stream: bool,
    ) -> dict:
        chain = self.model_chain
        try:
            idx = chain.index(model_name)
            alternate_models = chain[idx + 1 :]
        except ValueError:
            alternate_models = []

        payload: dict = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if alternate_models:
            payload["models"] = alternate_models
        return payload

    async def _stream_payload(self, payload: dict) -> AsyncGenerator[str, None]:
        headers = self._headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break

                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    choices = event.get("choices") or []
                    if not choices:
                        continue

                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")

                    if content:
                        yield str(content)

    def _extract_content(self, choice: dict) -> str:
        message = choice.get("message") or {}
        content = message.get("content") or ""

        if isinstance(content, list):
            return "\n".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            ).strip()

        return str(content).strip()

    async def _post(self, payload: dict) -> dict:
        headers = self._headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    def _is_retriable(self, exc: Exception) -> bool:
        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.RequestError) and not isinstance(
            exc, httpx.HTTPStatusError
        ):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status in (401, 400):
                return False
            if status in (402, 429, 502, 503):
                return True
            if status >= 500:
                return True
            return False
        return False

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.http_referer,
            "X-Title": self.app_title,
        }
