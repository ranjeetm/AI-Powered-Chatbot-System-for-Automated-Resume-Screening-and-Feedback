from backend.parser.parser import extract_text_from_pdf
from pathlib import Path


resume_dir = Path("datasets/resumes/data science")

for pdf_file in resume_dir.glob("*.pdf"):
    result = extract_text_from_pdf(pdf_file)

    print("=" * 50)
    print("FILE:", result["file_name"])
    print("PAGES:", result.get("pages"))

    text_preview = result.get("text", "")[:500]

    print(repr(text_preview))