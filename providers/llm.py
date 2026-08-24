import os
from typing import Any

import httpx


class LLMError(RuntimeError):
    """Raised when an LLM provider request cannot be completed."""


class LLMClient:
    """Provider-agnostic LLM client.

    The default protocol is OpenAI-compatible Chat Completions. This means
    the assistant can use OpenAI, OpenRouter, Groq, Together, Cerebras,
    local OpenAI-compatible servers, or any other compatible endpoint by
    changing only the base URL, model and API key environment variable.

    Ollama remains supported as a native protocol for local use.
    """

    def __init__(self, config: dict[str, Any]):
        self.provider = str(config.get("provider", "openai_compatible")).lower()
        self.protocol = str(config.get("protocol", "openai_chat")).lower()
        self.model = str(config.get("model", ""))
        self.base_url = str(config.get("base_url", "")).rstrip("/")
        self.endpoint = str(config.get("endpoint", ""))
        self.api_key_env = str(config.get("api_key_env", "AI_API_KEY"))
        self.api_key = os.getenv(self.api_key_env, "")
        self.temperature = config.get("temperature", 0.2)
        self.max_tokens = config.get("max_tokens", 800)
        self.timeout = float(config.get("timeout", 90))
        self.auth_type = str(config.get("auth_type", "bearer")).lower()
        self.auth_header = str(config.get("auth_header", "Authorization"))
        self.auth_prefix = str(config.get("auth_prefix", "Bearer"))
        self.extra_headers = dict(config.get("headers", {}) or {})

        self.enabled = self._is_enabled()

    def _is_enabled(self) -> bool:
        if not self.base_url or not self.model:
            return False
        if self.provider in {"ollama", "local_ollama"} or self.protocol == "ollama":
            return True
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        headers = {str(k): str(v) for k, v in self.extra_headers.items()}
        if self.provider in {"ollama", "local_ollama"} or self.protocol == "ollama":
            return headers
        if self.auth_type == "none":
            return headers
        if self.auth_type == "header":
            headers[self.auth_header] = self.api_key
        else:
            value = self.api_key
            if self.auth_prefix:
                value = f"{self.auth_prefix} {value}"
            headers[self.auth_header] = value
        return headers

    def _url(self) -> str:
        if self.endpoint:
            return self.base_url + "/" + self.endpoint.lstrip("/")
        if self.provider in {"ollama", "local_ollama"} or self.protocol == "ollama":
            return self.base_url + "/api/generate"
        return self.base_url + "/chat/completions"

    async def complete(self, prompt: str) -> str:
        if not self.enabled:
            return ""

        if self.provider in {"ollama", "local_ollama"} or self.protocol == "ollama":
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        else:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._url(),
                headers=self._headers(),
                json=payload,
            )

        if response.is_error:
            detail = response.text[:1000]
            raise LLMError(f"{self.provider} returned HTTP {response.status_code}: {detail}")

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError("LLM provider returned invalid JSON") from exc

        return self._extract_text(data)

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        # OpenAI-compatible Chat Completions response.
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts.append(item["text"])
                if parts:
                    return "".join(parts)

            # Some compatible APIs expose text directly on the first choice.
            text = choices[0].get("text") if isinstance(choices[0], dict) else None
            if isinstance(text, str):
                return text

        # Native Ollama /api/generate response.
        if isinstance(data.get("response"), str):
            return data["response"]

        # A few OpenAI-compatible gateways expose output_text.
        if isinstance(data.get("output_text"), str):
            return data["output_text"]

        raise LLMError("LLM provider response did not contain assistant text")
