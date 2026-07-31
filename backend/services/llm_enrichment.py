from openai import OpenAI
import json
import hashlib
import os
import time
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    if OPENROUTER_API_KEY
    else None
)

# --------------------------------
# FALLBACK MODELS
# --------------------------------

MODELS = [
    # Top tier and fast
    "google/gemma-4-31b-it:free",
    # Excellent code/tech reasoning
    "cohere/north-mini-code:free",
    # Good general purpose
    "poolside/laguna-s-2.1:free",
    # Robust fallback
    "nvidia/nemotron-3-super-120b-a12b:free",
    # Catch-all auto router
    "openrouter/free",
]

# --------------------------------
# SIMPLE MEMORY CACHE
# --------------------------------

LLM_CACHE = {}

# --------------------------------
# CLEAN SKILLS
# --------------------------------


def clean_skills(skills):

    cleaned = []

    seen = set()

    for skill in skills:

        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        # Skip invalid values
        if len(skill) < 2:
            continue

        if len(skill) > 40:
            continue

        # Normalize
        skill = skill.title()

        # Remove duplicates
        if skill in seen:
            continue

        seen.add(skill)

        cleaned.append(skill)

    return cleaned[:25]


# --------------------------------
# EMPTY FALLBACK RESPONSE
# --------------------------------


def empty_response():

    return {
        "technical_skills": [],
        "frameworks": [],
        "databases": [],
        "cloud_tools": [],
        "seniority": "Unknown",
        "summary": "",
    }


# --------------------------------
# ENRICH RESUME
# --------------------------------


def enrich_resume(resume_text):

    if client is None:

        print("\nOPENROUTER_API_KEY is not configured")

        return empty_response()

    # --------------------------------
    # CACHE KEY
    # --------------------------------

    resume_hash = hashlib.md5(resume_text.encode()).hexdigest()

    # --------------------------------
    # CACHE HIT
    # --------------------------------

    if resume_hash in LLM_CACHE:

        print("\nUsing cached LLM response")

        return LLM_CACHE[resume_hash]

    # --------------------------------
    # LIMIT RESUME SIZE
    # --------------------------------

    trimmed_resume = resume_text[:6000]

    # --------------------------------
    # PROMPT
    # --------------------------------

    prompt = f"""
You are an ATS resume parser.

Extract ONLY high-value resume intelligence.

IMPORTANT RULES:

- Maximum 25 technical skills
- No duplicate skills
- No repeated phrases
- No generic business words
- No hallucinated skills
- Keep skills concise
- Keep summary under 80 words
- Return STRICT valid JSON ONLY

Return format:

{{
  "technical_skills": [],
  "frameworks": [],
  "databases": [],
  "cloud_tools": [],
  "seniority": "",
  "summary": ""
}}

Resume:

{trimmed_resume}
"""

    # --------------------------------
    # TRY MODELS ONE BY ONE
    # --------------------------------

    for model_name in MODELS:

        try:

            print(f"\nTrying model: " f"{model_name}")

            start = time.time()

            response = client.chat.completions.create(
                model=model_name,
                temperature=0,
                max_tokens=400,
                timeout=25,
                messages=[{"role": "user", "content": prompt}],
            )

            end = time.time()

            latency = round(end - start, 2)

            print(f"\nLLM latency: " f"{latency}s")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Model returned empty or None content.")

            # --------------------------------
            # CLEAN RESPONSE & EXTRACT JSON
            # --------------------------------
            content_str = str(content)
            start_idx = content_str.find("{")
            end_idx = content_str.rfind("}")
            if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
                raise ValueError(f"Could not find valid JSON boundaries in response: {content_str}")

            json_str = content_str[start_idx:end_idx+1]

            # --------------------------------
            # PARSE JSON
            # --------------------------------

            parsed = json.loads(json_str)

            # --------------------------------
            # CLEAN OUTPUT
            # --------------------------------

            parsed["technical_skills"] = clean_skills(
                parsed.get("technical_skills", [])
            )

            parsed["frameworks"] = clean_skills(parsed.get("frameworks", []))

            parsed["databases"] = clean_skills(parsed.get("databases", []))

            parsed["cloud_tools"] = clean_skills(parsed.get("cloud_tools", []))

            # --------------------------------
            # CLEAN SUMMARY
            # --------------------------------

            parsed["summary"] = parsed.get("summary", "").strip()[:500]

            # --------------------------------
            # CACHE SUCCESS
            # --------------------------------

            LLM_CACHE[resume_hash] = parsed

            print(f"\nSUCCESS USING: " f"{model_name}")

            return parsed

        except Exception as e:

            print(f"\nFAILED MODEL: " f"{model_name}")

            print(e)

    # --------------------------------
    # ALL MODELS FAILED
    # --------------------------------

    return empty_response()
