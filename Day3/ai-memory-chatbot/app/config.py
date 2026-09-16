import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
	groq_api_key: str
	groq_model: str
	redis_url: str
	memory_ttl_seconds: int


def get_settings() -> Settings:
	groq_api_key = os.getenv("GROQ_API_KEY", "")
	if not groq_api_key:
		raise RuntimeError("GROQ_API_KEY is missing from .env")

	return Settings(
		groq_api_key=groq_api_key,
		groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
		redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
		memory_ttl_seconds=int(os.getenv("MEMORY_TTL_SECONDS", "0")),
	)
