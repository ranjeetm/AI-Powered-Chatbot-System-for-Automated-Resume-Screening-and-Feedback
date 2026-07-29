"""Shared OpenRouter model defaults for chat and enrichment."""

DEFAULT_FALLBACK_MODELS: tuple[str, ...] = (
    "openai/gpt-oss-20b:free",
    "z-ai/glm-4.5-air:free",
    "openrouter/free",
)
