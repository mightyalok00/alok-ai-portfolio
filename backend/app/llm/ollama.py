import json
from collections.abc import Iterator
import httpx


class OllamaProvider:
    """WHY: Use Ollama's native local HTTP API without another runtime dependency."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def stream(self, system: str, prompt: str) -> Iterator[str]:
        """Stream generated text from a local Ollama model."""
        payload = {"model": self.model, "system": system, "prompt": prompt, "stream": True, "options": {"temperature": 0.2}}
        with httpx.stream("POST", f"{self.base_url}/api/generate", json=payload, timeout=None) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("response"):
                    yield chunk["response"]
                if chunk.get("done"):
                    break

    def generate(self, system: str, prompt: str) -> str:
        """Generate a complete local response."""
        return "".join(self.stream(system, prompt))
