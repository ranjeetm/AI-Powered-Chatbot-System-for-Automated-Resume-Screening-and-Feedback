import streamlit as st
import pandas as pd
import io
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.file_handler import extract_text_from_pdf
from utils.improved_similarity_checker import calculate_similarity_score, get_detailed_match_analysis
from utils.improved_metadata_extractor import extract_email_phone_location, get_comprehensive_metadata
from utils.ai_analysis_engine import generate_analysis
from utils.email_sender import send_feedback_email
from database import ResumeDatabase

st.set_page_config(page_title="Candidate Portal", page_icon="👤", layout="centered")

# Initialize database
@st.cache_resource
def get_database():
    return ResumeDatabase()

db = get_database()

# Get current match criteria from session state (set by recruiter)
if "match_criteria" not in st.session_state:
    st.session_state.match_criteria = 70  # Default

match_criteria = st.session_state.match_criteria

st.title("👤 Candidate Portal")

# Show current criteria
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <p style="margin: 0; font-size: 16px; color: #555;">
            Upload your resume and get instant AI-powered feedback submitted to recruiters!
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 10px; 
                background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
                color: white; text-align: center;">
        <div style="font-size: 12px; opacity: 0.9;">Qualification Target</div>
        <div style="font-size: 24px; font-weight: bold;">≥{match_criteria}%</div>
    </div>
    """, unsafe_allow_html=True)

# Personal Information Section
st.markdown("### 📝 Your Information")
col1, col2 = st.columns(2)

with col1:
    candidate_name = st.text_input(
        "Full Name *", 
        placeholder="John Doe",
        help="Enter your full name"
    )

with col2:
    candidate_email = st.text_input(
        "Email Address *", 
        placeholder="john@example.com",
        help="We'll use this to save your results"
    )

# Job selection: fetch jobs from DB and provide dropdown
st.markdown("### 💼 Choose Position to Apply For")
jobs_df = db.get_job_descriptions()
job_options = []
job_map = {}
for _, row in jobs_df.iterrows():
    label = f"{row['title']} (id:{int(row['id'])})"
    job_options.append(label)
    job_map[label] = int(row['id'])

if job_options:
    selected_job_label = st.selectbox("Select job position", ["-- Select a job --"] + job_options, index=0)
else:
    selected_job_label = None

if not job_options:
    st.info("No job postings are available at the moment. Please check back later or contact the recruiter.")

# Resume Upload Section
st.markdown("### 📎 Upload Resume(s)")
resume_files = st.file_uploader(
    "Choose your resume file(s) - PDF format only",
    type="pdf",
    accept_multiple_files=True,
    help="You can upload multiple resumes to apply for the selected job"
)

if resume_files:
    st.info(f"📄 {len(resume_files)} resume(s) uploaded")

# Process Button
st.markdown("---")
process_button = st.button(
    "🚀 Submit Application(s)", 
    use_container_width=True, 
    type="primary",
    disabled=not (selected_job_label and selected_job_label != "-- Select a job --" and resume_files and candidate_name and candidate_email)
)

# Validation and Processing
if process_button:
    if not candidate_name or not candidate_email:
        st.error("❌ Please fill in your name and email!")
    elif not selected_job_label or selected_job_label == "-- Select a job --":
        st.error("❌ Please select a job to apply for!")
    elif not resume_files:
        st.error("❌ Please upload at least one resume!")
    else:
        # Determine job id and job description text
        job_id = job_map[selected_job_label]
        job = db.get_job_description_by_id(job_id)
        if not job:
            st.error("❌ Selected job not found. Please refresh the page and try again.")
        else:
            jd_input = job['description'] or ""
            # Process resumes
            with st.spinner("🔍 Processing and submitting your application(s)..."):
                submitted_count = 0
                try:
                    # We'll capture the last analysis to use for the email preview
                    last_strengths = []
                    last_weaknesses = []
                    last_recommendations = []
                    for idx, file in enumerate(resume_files):
                        # Extract text
                        resume_text = extract_text_from_pdf(file)

                        # Calculate similarity using improved algorithm (kept for storing in DB)
                        score = calculate_similarity_score(jd_input, resume_text)
                        score_float = float(score)

                        # Get detailed analysis (for storing)
                        detailed_analysis = get_detailed_match_analysis(jd_input, resume_text)

                        # Extract contact information
                        email, phone, location = extract_email_phone_location(resume_text)

                        # Get comprehensive metadata
                        metadata = get_comprehensive_metadata(resume_text)

                        # Generate AI-powered analysis (strengths/weaknesses/recommendations)
                        strengths, weaknesses, recommendations = generate_analysis(
                            resume_text, 
                            jd_input, 
                            score_float
                        )

                        # Save to database
                        candidate_id = db.add_candidate(
                            name=candidate_name,
                            email=candidate_email,
                            phone=phone if phone else metadata.get('phone'),
                            resume_text=resume_text,
                            resume_filename=file.name
                        )

                        if candidate_id:
                            # Save screening results linked to job_description_id and also store job_description text (backward compat)
                            db.add_screening_result(
                                candidate_id=candidate_id,
                                job_description=jd_input,
                                match_score=score_float,
                                strengths=strengths,
                                weaknesses=weaknesses,
                                recommendations=recommendations,
                                job_description_id=job_id
                            )
                            submitted_count += 1
                            # store last feedback for email preview
                            last_strengths = strengths
                            last_weaknesses = weaknesses
                            last_recommendations = recommendations
                        else:
                            # If candidate couldn't be added (e.g., duplicate email), still attempt to find existing id and save screening
                            existing = db.search_candidates(candidate_email)
                            if not existing.empty:
                                existing_id = int(existing.iloc[0]['id'])
                                db.add_screening_result(
                                    candidate_id=existing_id,
                                    job_description=jd_input,
                                    match_score=score_float,
                                    strengths=strengths,
                                    weaknesses=weaknesses,
                                    recommendations=recommendations,
                                    job_description_id=job_id
                                )
                                submitted_count += 1
                                last_strengths = strengths
                                last_weaknesses = weaknesses
                                last_recommendations = recommendations
                            else:
                                st.warning(f"⚠️ Could not save {file.name}. Email may already exist.")

                    if submitted_count > 0:
                        st.success(f"✅ Application(s) submitted successfully for the position: **{job['title']}**.")
                        st.info("Your application has been recorded. Recruiters will be able to view the match score and analysis.")
                        st.balloons()
                        # Do not display scores or analysis to the candidate — only confirmation
                        # Update session state timestamp
                        st.session_state.last_updated = datetime.now()

                        # -------------------------
                        # Send feedback email (dry-run by default)
                        # -------------------------
                        try:
                            email_sent = send_feedback_email(
                                recipient_email=candidate_email,
                                candidate_name=candidate_name or "Candidate",
                                job_title=job['title'],
                                strengths=last_strengths,
                                weaknesses=last_weaknesses,
                                recommendations=last_recommendations,
                                dry_run=False  # <-- set to False to send real email after testing
                            )
                            if email_sent:
                                st.success("📧 Feedback email preview generated (dry-run).")
                            else:
                                st.warning("⚠️ Feedback email not generated. SMTP may not be configured or credentials may be wrong.")
                        except Exception as e:
                            st.error(f"⚠️ Error while attempting to generate/send feedback email: {e}")
                    else:
                        st.error("❌ No applications were submitted successfully.")
                except Exception as e:
                    st.error(f"❌ Error processing applications: {str(e)}")
                    st.exception(e)

# Show hints when fields are empty
elif not (selected_job_label and selected_job_label != "-- Select a job --" and resume_files):
    st.info("👆 Please select a job, fill in required fields and upload your resume(s) to apply.")

# Previous Submissions Section (candidate can lookup by email)
st.markdown("---")
st.markdown("### 📜 View Your Previous Submissions")

search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    search_email = st.text_input(
        "🔍 Enter your email to view submission history",
        placeholder="john@example.com",
        label_visibility="collapsed"
    )

with search_col2:
    search_button = st.button("Search", use_container_width=True)

if search_email and search_button:
    with st.spinner("Searching..."):
        results = db.search_candidates(search_email)

        if not results.empty:
            st.success(f"✅ Found {len(results)} submission(s) for {search_email}")

            for idx, row in results.iterrows():
                screening_results = db.get_screening_results(row['id'])

                if not screening_results.empty:
                    latest = screening_results.iloc[0]
                    # For candidates, we DO NOT show the numeric score prominently.
                    # But we can show metadata and the job they applied to (no score).
                    job_title = latest.get('job_title') or "Unknown Position"
                    with st.expander(f"{row['resume_filename']} - Applied: {job_title}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Name:** {row['name']}")
                            st.write(f"**Email:** {row['email']}")
                            if row['phone']:
                                st.write(f"**Phone:** {row['phone']}")

                        with col2:
                            st.write(f"**Uploaded:** {row['uploaded_at']}")
                            st.write(f"**Position:** {job_title}")

                        st.markdown("---")

                        # Show AI feedback but without the numeric score
                        tab1, tab2, tab3 = st.tabs(["✅ Strengths", "💡 Improvements", "🎯 Recommendations"])

                        with tab1:
                            for strength in latest['strengths']:
                                st.success(f"✓ {strength}")

                        with tab2:
                            for weakness in latest['weaknesses']:
                                st.warning(f"• {weakness}")

                        with tab3:
                            for rec in latest['recommendations']:
                                st.info(f"→ {rec}")
        else:
            st.warning("⚠️ No submissions found for this email address.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: #999; font-size: 13px;">
    <p>💡 <strong>Current Qualification Criteria: ≥{match_criteria}%</strong></p>
    <p>🔒 Your data is securely stored and kept confidential.</p>
    <p>📧 Access your results anytime using your email address!</p>
</div>
""", unsafe_allow_html=True)
