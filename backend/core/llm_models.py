"""Shared OpenRouter model defaults for chat and enrichment."""

DEFAULT_FALLBACK_MODELS: tuple[str, ...] = (
    "google/gemma-4-31b-it:free",
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/free",
)
