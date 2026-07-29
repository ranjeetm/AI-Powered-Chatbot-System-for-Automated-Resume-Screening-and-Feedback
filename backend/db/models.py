from sqlalchemy import DateTime
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Float,
    JSON,
    Text
)

from .database import Base

from pgvector.sqlalchemy import (
    Vector
)




class CandidateProfile(Base):

    __tablename__ = (
        "candidate_profiles"
    )

    # --------------------------------
    # PRIMARY KEY
    # --------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------
    # BASIC INFO
    # --------------------------------

    file_name = Column(
        String
    )

    candidate_name = Column(
        String
    )

    email = Column(
        String
    )

    phone = Column(
        String
    )

    location = Column(
        String
    )

    linkedin_url = Column(
        String
    )

    github_url = Column(
        String
    )

    category = Column(
        String
    )

    # --------------------------------
    # STRUCTURED EXTRACTION
    # --------------------------------

    skills = Column(
        JSON
    )

    job_titles = Column(
        JSON
    )

    degrees = Column(
        JSON
    )

    specializations = Column(
        JSON
    )

    certifications = Column(
        JSON
    )

    education = Column(
        JSON
    )

    projects = Column(
        JSON
    )

    experience = Column(
        JSON
    )

    sections = Column(
        JSON
    )

    # --------------------------------
    # EXPERIENCE
    # --------------------------------

    experience_years = Column(
        Integer
    )

    # --------------------------------
    # TEXT STORAGE
    # --------------------------------

    resume_summary = Column(Text)

    resume_text = Column(Text)

    cleaned_text = Column(Text)

    resume_file_path = Column(Text)

    # --------------------------------
    # SCORING
    # --------------------------------

    semantic_score = Column(
        Float
    )

    weighted_score = Column(
        Float
    )

    recruiter_score = Column(
        Float
    )

    # --------------------------------
    # SHORTLIST
    # --------------------------------

    is_shortlisted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    shortlist_updated_at = Column(
        DateTime,
    )

    rejection_feedback = Column(
        Text,
    )

    # --------------------------------
    # VECTOR EMBEDDING
    # --------------------------------

    embedding = Column(
        Vector(384)
    )
    
    parsed_at = Column(
    DateTime,
    default=datetime.utcnow
)


class JobPosting(Base):

    __tablename__ = "job_postings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    department = Column(
        String
    )

    location = Column(
        String
    )

    type = Column(
        String
    )

    description = Column(
        Text,
        nullable=False
    )

    skills = Column(
        JSON
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class JobDescription(Base):

    __tablename__ = "job_descriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    extracted_skills = Column(
        JSON
    )

    inferred_category = Column(
        String
    )

    inferred_seniority = Column(
        String
    )

    embedding = Column(
        Vector(384)
    )

    created_by = Column(
        Integer
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class MatchResult(Base):

    __tablename__ = "match_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        index=True,
        nullable=False
    )

    job_description_id = Column(
        Integer,
        index=True,
        nullable=False
    )

    semantic_score = Column(
        Float
    )

    skill_score = Column(
        Float
    )

    experience_score = Column(
        Float
    )

    final_score = Column(
        Float
    )

    strengths = Column(
        JSON
    )

    matched_skills = Column(
        JSON
    )

    missing_skills = Column(
        JSON
    )

    ai_feedback = Column(
        JSON
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
