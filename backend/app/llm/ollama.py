import json
from collections.abc import Iterator

import httpx


class OllamaProvider:
    """WHY: Use Ollama's native local HTTP API without another runtime dependency."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def stream(self, system: str, prompt: str) -> Iterator[str]:
        """Stream generated text from a local Ollama model.

        Raises a normal RuntimeError when Ollama is unreachable or returns an
        invalid stream so the API can surface a useful recruiter-facing error
        instead of leaving the chat in an endless loading state.
        """
        payload = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.2},
        }
        timeout = httpx.Timeout(connect=8.0, read=120.0, write=15.0, pool=8.0)
        try:
            with httpx.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError("Ollama returned an invalid streaming response.") from exc
                    if chunk.get("error"):
                        raise RuntimeError(str(chunk["error"]))
                    if chunk.get("response"):
                        yield chunk["response"]
                    if chunk.get("done"):
                        break
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Cannot reach Ollama at {self.base_url}. Start Ollama and retry."
            ) from exc
        except httpx.ReadTimeout as exc:
            raise RuntimeError(
                f"Ollama model '{self.model}' did not respond within 120 seconds."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}: {detail}"
            ) from exc

    def generate(self, system: str, prompt: str) -> str:
        """Generate a complete local response."""
        return "".join(self.stream(system, prompt))
