import re
from app.config import settings
from app.llm.ollama import OllamaProvider


class ModelRouter:
    """WHY: Select the installed model that best fits the recruiter's question."""

    def choose_model(self, query: str) -> str:
        text = query.lower()
        if re.search(r"\b(code|python|sql|fastapi|api|debug|algorithm|regression|architecture|github|implementation|technical|streamlit)\b", text):
            return settings.ollama_code_model
        if re.search(r"\b(job description|jd|requirements|match|suitable|compare|analyze|analysis|reason|why hire|interview)\b", text):
            return settings.ollama_reasoning_model
        return settings.ollama_chat_model

    def provider_for(self, query: str) -> OllamaProvider:
        """Return an Ollama provider configured with the routed model."""
        return OllamaProvider(settings.ollama_base_url, self.choose_model(query))
