import os
import httpx

class LLMClient:
    def __init__(self, config):
        self.provider = config.get("provider", "disabled")
        self.model = config.get("model", "")
        self.base_url = config.get("base_url", "")
        self.api_key = os.getenv(config.get("api_key_env", "OPENROUTER_API_KEY"), "")
        self.temperature = config.get("temperature", 0.2)
        self.max_tokens = config.get("max_tokens", 800)
        self.enabled = self.provider == "ollama" or (self.provider == "openrouter" and bool(self.api_key))

    async def complete(self, prompt: str) -> str:
        if not self.enabled:
            return ""
        async with httpx.AsyncClient(timeout=90) as client:
            if self.provider == "openrouter":
                r = await client.post(
                    self.base_url.rstrip("/") + "/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": [{"role": "user", "content": prompt}],
                          "temperature": self.temperature, "max_tokens": self.max_tokens},
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            r = await client.post(
                self.base_url.rstrip("/") + "/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json()["response"]
