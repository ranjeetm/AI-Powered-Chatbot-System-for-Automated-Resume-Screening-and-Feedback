import os
from openai import OpenAI
import json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def enrich_resume(resume_text):

    prompt = f"""
    Extract:
    - technical skills
    - frameworks
    - databases
    - cloud tools
    - seniority
    - short candidate summary

    Return STRICT JSON only.

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    return json.loads(content)

sample_resume = """
Python developer with FastAPI,
PostgreSQL, Docker,
Machine Learning and NLP experience.
"""

result = enrich_resume(sample_resume)

print(json.dumps(result, indent=2))