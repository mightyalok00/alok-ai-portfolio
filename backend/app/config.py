from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """WHY: Keep local Ollama/model settings in one validated configuration object."""

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:latest"
    ollama_code_model: str = "qwen2.5-coder:7b"
    ollama_reasoning_model: str = "deepseek-r1:7b"
    frontend_origin: str = "http://localhost:5173"
    candidate_path: str = "data/candidate.json"
    documents_path: str = "data/documents"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
