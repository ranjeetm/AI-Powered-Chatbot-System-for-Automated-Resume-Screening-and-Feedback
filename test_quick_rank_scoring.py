from backend.scoring.profile_scorer import ProfileScorer


def test_skill_match_uses_extracted_skills_case_insensitively():
    scorer = ProfileScorer()
    candidate_skills = [
        "Python",
        "Scikit-Learn",
        "Pandas",
        "SQL",
    ]
    jd_text = "Looking for Python, SQL, Pandas and Scikit-learn experience."

    assert scorer.calculate_skill_match(candidate_skills, jd_text) == 1.0


def test_experience_match_uses_required_experience_from_jd():
    scorer = ProfileScorer()

    required = scorer.extract_required_experience(
        "Junior role for fresher or 0-1 years experience."
    )

    assert required == 0.0
    assert scorer.calculate_experience_match(0, required) == 1.0


def test_experience_match_for_senior_jd_requirement():
    scorer = ProfileScorer()

    required = scorer.extract_required_experience(
        "Requires at least 4 years of experience with backend APIs."
    )

    assert required == 4.0
    assert scorer.calculate_experience_match(2, required) == 0.5


def test_intern_jd_scores_zero_year_candidate_as_experience_fit():
    scorer = ProfileScorer()

    required = scorer.extract_required_experience(
        "AI/ML Engineer Intern with Python, SQL, NLP, Streamlit, and Scikit-learn."
    )

    assert required == 0.0
    assert scorer.calculate_experience_match(0, required) == 1.0


def test_skill_match_normalizes_common_ai_resume_aliases():
    scorer = ProfileScorer()
    candidate_skills = [
        "Python",
        "SQL",
        "Artificial Intelligence",
        "Machine Learning",
        "NLP",
        "Pandas",
        "NumPy",
        "Scikit-Learn",
        "Streamlit",
        "React.js",
        "PostgreSQL",
        "MySQL",
    ]
    jd_text = (
        "AI/ML Engineer Intern. Required Skills: Python, SQL, Machine Learning, "
        "Scikit-learn, Pandas, NumPy, NLP, Streamlit, React, PostgreSQL and MySQL."
    )

    assert scorer.calculate_skill_match(candidate_skills, jd_text) >= 0.85


def test_skill_match_uses_resume_text_when_saved_skills_are_incomplete():
    scorer = ProfileScorer()
    candidate_skills = [
        "Python",
        "SQL",
    ]
    resume_text = (
        "Built an AI chatbot with NLP, Streamlit, Pandas, NumPy, Scikit-learn, "
        "data preprocessing, model evaluation, MySQL and PostgreSQL."
    )
    jd_text = (
        "AI/ML Engineer Intern requiring Python, SQL, NLP, Streamlit, Pandas, "
        "NumPy, Scikit-learn, data preprocessing, model evaluation, MySQL and PostgreSQL."
    )

    assert scorer.calculate_skill_match(
        candidate_skills,
        jd_text,
        candidate_text=resume_text,
    ) >= 0.85


def test_title_match_uses_category_and_skills_for_ai_ml_roles():
    scorer = ProfileScorer()

    score = scorer.calculate_title_match(
        [],
        "AI/ML Engineer Intern",
        candidate_category="Junior ML Engineer",
        candidate_skills=["Artificial Intelligence", "Machine Learning"],
    )

    assert score > 0.0
