import streamlit as st
import pandas as pd
import io
from utils.file_handler import extract_text_from_pdf
from utils.similarity_checker import calculate_similarity_score
from utils.metadata_extractor import extract_email_phone_location

# --------------------------
# PAGE CONFIGURATION
# --------------------------
st.set_page_config(page_title="Resume Screening AI Portal", layout="centered")

st.title("📑 Resume Screening AI Portal")

# --------------------------
# MAIN TABS
# --------------------------
tab_candidate, tab_recruiter = st.tabs(["👤 Candidate Portal", "🏢 Recruiter Portal"])

# ==========================================================
# TAB 1 — CANDIDATE PORTAL
# ==========================================================
with tab_candidate:
    st.subheader("👤 Candidate Portal - Upload Resume and Get Match Score")

    st.markdown("### 📝 Job Description")
    jd_input = st.text_area("Enter the job description (Max 1000 words)", height=250)

    # Check word limit
    word_count = len(jd_input.split())
    if word_count > 1000:
        st.warning(f"❗ Word limit exceeded ({word_count}/1000). Please reduce your job description.")
        jd_input = ""

    # Resume upload
    resume_files = st.file_uploader("📎 Upload your Resume (PDF format)", type="pdf", accept_multiple_files=True)

    df_results = pd.DataFrame()

    if jd_input and resume_files:
        st.markdown("## 📊 Match Results")

        results = []
        for file in resume_files:
            resume_text = extract_text_from_pdf(file)
            score = calculate_similarity_score(jd_input, resume_text)
            email, phone, location = extract_email_phone_location(resume_text)

            results.append({
                "Resume": file.name,
                "Score": f"{score}%",
                "Email": email,
                "Contact Number": phone,
                "Location": location
            })

        df_results = pd.DataFrame(results)
        st.table(df_results)

        # Save results to session_state for recruiter tab
        st.session_state.df_results = df_results

        # Download Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_results.to_excel(writer, index=False, sheet_name='Results')
        output.seek(0)

        st.download_button(
            label="📥 Download Results as Excel",
            data=output,
            file_name="resume_scores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif jd_input and not resume_files:
        st.info("Please upload at least one resume PDF.")
    elif resume_files and not jd_input:
        st.info("Please paste the job description above.")

# ==========================================================
# TAB 2 — RECRUITER PORTAL
# ==========================================================
with tab_recruiter:
    st.subheader("🏢 Recruiter Portal - Chat with the Resume Screening Bot 🤖")

    st.markdown("""
    **Ask the bot about:**
    - 🔹 Top candidates  
    - 🔹 Average scores  
    - 🔹 Total resumes processed  
    - 🔹 How to download results
    """)

    recruiter_query = st.chat_input("Ask something about candidate results...")

    if recruiter_query:
        with st.chat_message("user"):
            st.markdown(recruiter_query)

        response = ""
        results_df = st.session_state.get("df_results", pd.DataFrame())

        if "top" in recruiter_query.lower() and "candidate" in recruiter_query.lower():
            if not results_df.empty:
                top = results_df.sort_values(by="Score", ascending=False).head(3)
                response = "Here are the top candidates:\n\n" + "\n".join(
                    f"{row.Resume} — {row.Score}" for row in top.itertuples()
                )
            else:
                response = "No resume data available yet. Please ask candidates to upload first."

        elif "average" in recruiter_query.lower() and "score" in recruiter_query.lower():
            if not results_df.empty:
                avg_score = results_df["Score"].str.replace('%', '').astype(float).mean()
                response = f"The average candidate score is **{avg_score:.2f}%**."
            else:
                response = "No data available yet."

        elif "download" in recruiter_query.lower():
            response = "You can download the results from the Candidate Portal once uploaded."

        elif "how many" in recruiter_query.lower() and "resume" in recruiter_query.lower():
            count = len(results_df)
            response = f"There are currently **{count} resumes** processed." if count > 0 else "No resumes processed yet."

        else:
            response = (
                "Hi! I'm your Recruiter Assistant 🤖\n\n"
                "You can ask:\n"
                "- 'Show top candidates'\n"
                "- 'What is the average score?'\n"
                "- 'How many resumes are processed?'\n"
                "- 'How to download results?'"
            )

        with st.chat_message("assistant"):
            st.markdown(response)
