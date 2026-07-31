"""Shared OpenRouter model defaults for chat and enrichment."""

DEFAULT_FALLBACK_MODELS: tuple[str, ...] = (
    "meta-llama/llama-3-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free",
    "openrouter/free",
)
