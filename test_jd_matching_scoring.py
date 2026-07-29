from backend.services.jd_matching.matching_service import JDMatchingService


def test_jd_matching_score_combines_required_signals():
    service = JDMatchingService()
    row = {
        "id": 1,
        "skills": ["FastAPI", "Docker", "PostgreSQL"],
        "semantic_similarity": 0.8,
        "experience_years": 5,
        "recruiter_boost": 0.4,
    }

    scored = service._score_row(
        row,
        ["fastapi", "docker", "kubernetes"],
        5,
    )

    assert scored["matched_skills"] == ["FastAPI", "Docker"]
    assert scored["missing_skills"] == ["kubernetes"]
    assert round(scored["skill_score"], 4) == 0.6667
    assert scored["experience_score"] == 1.0
    assert round(scored["final_score"], 4) == 0.75


def test_jd_matching_experience_alignment_caps_at_one():
    service = JDMatchingService()

    assert service._experience_alignment(0, 5) == 0.0
    assert service._experience_alignment(2, 5) == 0.4
    assert service._experience_alignment(12, 5) == 1.0
    assert service._experience_alignment(0, 0) == 1.0


def test_required_experience_uses_jd_text_before_seniority_default():
    service = JDMatchingService()

    assert service._required_experience_from_jd("Requires 3+ years of experience", "Senior") == 3.0
    assert service._required_experience_from_jd("0-1 years experience or fresher", "Mid") == 0.0
    assert service._required_experience_from_jd("AI/ML Engineer Intern", "Mid") == 0.0
    assert service._required_experience_from_jd("Senior backend engineer", "Senior") == 5.0


def test_jd_matching_skill_score_normalizes_aliases():
    service = JDMatchingService()
    row = {
        "id": 1,
        "skills": ["React.js", "Scikit-Learn", "PostgreSQL", "Artificial Intelligence"],
        "semantic_similarity": 0.8,
        "experience_years": 0,
        "recruiter_boost": 0.0,
    }

    scored = service._score_row(
        row,
        ["react", "sklearn", "postgres", "ai"],
        0,
    )

    assert scored["skill_score"] == 1.0
    assert scored["experience_score"] == 1.0
