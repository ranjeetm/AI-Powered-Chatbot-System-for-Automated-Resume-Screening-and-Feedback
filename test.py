from utils.file_handler import extract_text_from_file
from utils.similarity_checker import calculate_similarity_score
with open("sample_jd.txt", "r", encoding="utf-8") as jd:
    jd_text = jd.read()

with open("sample_resume.pdf", "rb") as resume:
    resume_text = extract_text_from_file(resume)

score = calculate_similarity_score(jd_text, resume_text)
print(f"Match Score: {score}%")
