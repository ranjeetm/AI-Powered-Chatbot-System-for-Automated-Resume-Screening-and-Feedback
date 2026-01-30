import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database import ResumeDatabase

st.set_page_config(page_title="Recruiter Portal", page_icon="🏢", layout="wide")

# Set seaborn style
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

# Initialize database
@st.cache_resource
def get_database():
    return ResumeDatabase()

db = get_database()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "match_criteria" not in st.session_state:
    st.session_state.match_criteria = 70  # Default 70%

# Header with Match Criteria Slider
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 42px; font-weight: 700; 
                   background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🏢 Recruiter Portal
        </h1>
        <p style="font-size: 18px; color: #666;">Your AI-Powered Hiring Command Center</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🎯 Match Criteria")
    match_criteria = st.slider(
        "Minimum Match %",
        min_value=0,
        max_value=100,
        value=st.session_state.match_criteria,
        step=5,
        help="Set the minimum match percentage to qualify candidates"
    )
    st.session_state.match_criteria = match_criteria

    # Color-coded badge
    if match_criteria >= 80:
        badge_color = "#22c55e"
        badge_text = "High Standard"
    elif match_criteria >= 60:
        badge_color = "#fbbf24"
        badge_text = "Moderate"
    else:
        badge_color = "#ef4444"
        badge_text = "Low Standard"

    st.markdown(f"""
    <div style="text-align: center; padding: 10px; border-radius: 8px; 
                background: {badge_color}; color: white; font-weight: bold;">
        {badge_text}: ≥{match_criteria}%
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Job selector (All Jobs or specific job)
jobs_df = db.get_job_descriptions()
job_options = ["All Jobs"]
job_map = {"All Jobs": None}
for _, r in jobs_df.iterrows():
    label = f"{r['title']} (id:{int(r['id'])})"
    job_options.append(label)
    job_map[label] = int(r['id'])

selected_job_label = st.selectbox("🔎 Filter analytics / candidates by job", job_options, index=0)
selected_job_id = job_map[selected_job_label]

# Get filtered data based on criteria and selected job
stats = db.get_statistics()
all_screening_results = db.get_screening_results(job_id=selected_job_id)
qualified_candidates = all_screening_results[all_screening_results['match_score'] >= match_criteria] if not all_screening_results.empty else pd.DataFrame()

# Show quick stats with criteria applied
st.markdown("### 📊 Quick Overview")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Candidates", stats['total_candidates'])

with col2:
    st.metric("Avg Score", f"{stats['avg_score']:.1f}%")

with col3:
    st.metric("Top Score", f"{stats['top_score']:.1f}%")

with col4:
    qualified_count = len(qualified_candidates)
    st.metric(f"Qualified (≥{match_criteria}%)", qualified_count)

with col5:
    if stats['total_candidates'] > 0:
        qual_rate = (qualified_count / stats['total_candidates']) * 100
        st.metric("Qualification Rate", f"{qual_rate:.1f}%")
    else:
        st.metric("Qualification Rate", "N/A")

st.markdown("---")

# Main tabs (added Job Management tab)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Assistant", "📊 Analytics Dashboard", "👥 Qualified Candidates", "🧾 Job Management", "⚙️ Settings"])

# ==================== TAB 1: AI ASSISTANT ====================
with tab1:
    st.markdown("### 💬 Chat with AI Recruiter Assistant")

    # Display current criteria
    st.info(f"🎯 Current Match Criteria: **{match_criteria}%** | Qualified Candidates: **{len(qualified_candidates)}** | Filter: **{selected_job_label}**")

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Quick action buttons
    st.markdown("#### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏆 Top Qualified", use_container_width=True):
            st.session_state.quick_query = "Show me top qualified candidates"

    with col2:
        if st.button("📈 Statistics", use_container_width=True):
            st.session_state.quick_query = "Give me overall statistics"

    with col3:
        if st.button("🔍 Recent Uploads", use_container_width=True):
            st.session_state.quick_query = "Show recent uploads"

    with col4:
        if st.button("💡 Insights", use_container_width=True):
            st.session_state.quick_query = "Give me hiring insights"

    # Chat input
    recruiter_query = st.chat_input("Ask me anything about candidates, scores, or hiring insights...")

    # Handle quick query buttons
    if "quick_query" in st.session_state:
        recruiter_query = st.session_state.quick_query
        del st.session_state.quick_query

    if recruiter_query:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": recruiter_query})

        # Get data from database (respect selected job)
        all_candidates = db.get_all_candidates()

        # Generate response based on query
        response = ""
        query_lower = recruiter_query.lower()

        # Top qualified candidates query
        if any(word in query_lower for word in ["top", "best", "highest", "qualified"]) and "candidate" in query_lower:
            if not qualified_candidates.empty:
                top_qualified = qualified_candidates.nlargest(5, 'match_score')
                response = f"## 🏆 Top 5 Qualified Candidates (≥{match_criteria}%) - Filter: {selected_job_label}\n\n"
                for idx, (_, row) in enumerate(top_qualified.iterrows(), 1):
                    response += f"**{idx}. {row['name']}**\n"
                    response += f"   - 📧 Email: {row['email']}\n"
                    response += f"   - ⭐ Score: **{row['match_score']:.1f}%**\n"
                    response += f"   - 📅 Screened: {row['screened_at']}\n\n"
            else:
                response = f"❌ No candidates meet the current criteria of {match_criteria}%. Consider lowering the threshold."

        # Statistics query with criteria
        elif any(word in query_lower for word in ["statistics", "stats", "overall", "summary"]):
            qual_rate = (len(qualified_candidates) / stats['total_candidates'] * 100) if stats['total_candidates'] > 0 else 0

            response = f"""
## 📊 Overall Statistics (Criteria: {match_criteria}% | Filter: {selected_job_label})

**Total Metrics:**
- 📄 Total Resumes: **{stats['total_candidates']}**
- ✅ Qualified Candidates: **{len(qualified_candidates)}** ({qual_rate:.1f}%)
- ⭐ Average Score: **{stats['avg_score']:.1f}%**
- 🏆 Top Score: **{stats['top_score']:.1f}%**
"""

        # Criteria adjustment suggestions
        elif "criteria" in query_lower or "threshold" in query_lower or "adjust" in query_lower:
            qual_rate = (len(qualified_candidates) / stats['total_candidates'] * 100) if stats['total_candidates'] > 0 else 0
            response = f"""
## 🎯 Match Criteria Analysis (Filter: {selected_job_label})

**Current Settings:**
- Threshold: **{match_criteria}%**
- Qualified: **{len(qualified_candidates)}** candidates
- Qualification Rate: **{qual_rate:.1f}%**
"""
            if qual_rate < 10:
                response += "\n⚠️ **Very Few Qualified Candidates** - Suggested: Lower threshold to 60-70%\n"
            elif qual_rate < 30:
                response += "\n💡 **Below Target Range** - Consider lowering criteria slightly (5-10%)\n"
            elif qual_rate < 60:
                response += "\n✅ **Good Balance** - Current criteria working well\n"
            else:
                response += "\n🌟 **Excellent Pool** - Consider raising criteria to 75-80%\n"

        # Count query with criteria
        elif any(phrase in query_lower for phrase in ["how many", "number of", "count"]):
            response = f"""
📊 **Candidate Count Analysis (Filter: {selected_job_label})**

- Total Candidates: **{stats['total_candidates']}**
- Qualified (≥{match_criteria}%): **{len(qualified_candidates)}**
- Not Qualified (<{match_criteria}%): **{stats['total_candidates'] - len(qualified_candidates)}**
"""

        # Recent uploads query
        elif "recent" in query_lower or "latest" in query_lower:
            all_candidates = db.get_all_candidates()
            if not all_candidates.empty:
                recent = all_candidates.head(5)
                response = "## 📅 Recent Uploads (Last 5)\n\n"
                for idx, row in recent.iterrows():
                    candidate_results = all_screening_results[all_screening_results['email'] == row['email']]
                    if not candidate_results.empty:
                        best_score = candidate_results['match_score'].max()
                        status = "✅ Qualified" if best_score >= match_criteria else "❌ Not Qualified"
                        response += f"**{row['name']}** {status}\n"
                        response += f"   - 📧 {row['email']}\n"
                        response += f"   - 📄 {row['resume_filename']}\n"
                        response += f"   - ⭐ Best Score: {best_score:.1f}%\n"
                        response += f"   - 🕐 {row['uploaded_at']}\n\n"
            else:
                response = "❌ No uploads yet."

        # Insights query with criteria consideration
        elif "insight" in query_lower or "recommendation" in query_lower or "advice" in query_lower:
            if stats['total_candidates'] > 0:
                qual_rate = (len(qualified_candidates) / stats['total_candidates']) * 100
                response = f"## 💡 AI-Powered Hiring Insights (Filter: {selected_job_label})\n\n"
                response += f"**Current Status (Criteria: {match_criteria}%):**\n"
                response += f"- {stats['total_candidates']} total candidates\n"
                response += f"- {len(qualified_candidates)} qualified ({qual_rate:.1f}%)\n"
                response += f"- Average score: {stats['avg_score']:.1f}%\n\n"
                if qual_rate >= 50:
                    response += "🎯 **Strong Pipeline:** Fast-track top candidates.\n"
                elif qual_rate >= 25:
                    response += "⚖️ **Moderate Pipeline:** Consider expanding search.\n"
                else:
                    response += "🔍 **Limited Pipeline:** Lower criteria to 60-65% or expand recruiting.\n"
            else:
                response = "❌ Not enough data yet for insights."

        # Default response with criteria info
        else:
            response = f"""
🤖 I'm your AI Recruiter Assistant! 

**Current Settings:**
- Match Criteria: **{match_criteria}%**
- Qualified Candidates: **{len(qualified_candidates)}**
- Filter: **{selected_job_label}**

I can help with:
- 'Show me top qualified candidates'
- 'What are the overall stats?'
- 'Should I adjust my criteria?'
"""

        # Add assistant response to chat
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ==================== TAB 2: ANALYTICS DASHBOARD ====================
with tab2:
    st.markdown("### 📊 Analytics Dashboard")

    # Criteria indicator
    st.info(f"🎯 Showing data with match criteria: **≥{match_criteria}%** | Qualified: **{len(qualified_candidates)}** | Filter: {selected_job_label}")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="font-size: 32px; margin-bottom: 10px;">📄</div>
            <div style="font-size: 28px; font-weight: bold;">{stats['total_candidates']}</div>
            <div style="font-size: 14px; opacity: 0.9;">Total Resumes</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%); 
                    color: white; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="font-size: 32px; margin-bottom: 10px;">✅</div>
            <div style="font-size: 28px; font-weight: bold;">{len(qualified_candidates)}</div>
            <div style="font-size: 14px; opacity: 0.9;">Qualified (≥{match_criteria}%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    color: white; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="font-size: 32px; margin-bottom: 10px;">📈</div>
            <div style="font-size: 28px; font-weight: bold;">{stats['avg_score']:.1f}%</div>
            <div style="font-size: 14px; opacity: 0.9;">Average Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        qual_rate = (len(qualified_candidates) / stats['total_candidates'] * 100) if stats['total_candidates'] > 0 else 0
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); 
                    color: white; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="font-size: 32px; margin-bottom: 10px;">📊</div>
            <div style="font-size: 28px; font-weight: bold;">{qual_rate:.1f}%</div>
            <div style="font-size: 14px; opacity: 0.9;">Qualification Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if not all_screening_results.empty:
        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Score Distribution with Criteria Line")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(data=all_screening_results, x='match_score', bins=20, kde=True, ax=ax, color='#667eea')
            ax.axvline(match_criteria, color='red', linestyle='--', linewidth=2, label=f'Criteria: {match_criteria}%')
            ax.set_xlabel('Match Score (%)', fontsize=12)
            ax.set_ylabel('Number of Candidates', fontsize=12)
            ax.set_title('Candidate Score Distribution', fontsize=14, fontweight='bold')
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            st.markdown("#### 🏆 Top 10 Qualified Candidates")
            if not qualified_candidates.empty:
                top_10 = qualified_candidates.nlargest(10, 'match_score')

                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(data=top_10.sort_values('match_score'), y='name', x='match_score', ax=ax, palette='viridis')
                ax.axvline(match_criteria, color='red', linestyle='--', linewidth=2, alpha=0.7)
                ax.set_xlabel('Match Score (%)', fontsize=12)
                ax.set_ylabel('Candidate', fontsize=12)
                ax.set_title(f'Top Candidates (≥{match_criteria}%)', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.warning(f"No candidates meet the {match_criteria}% criteria yet for this filter.")

        # Qualification breakdown
        st.markdown("---")
        st.markdown("#### 🎯 Qualification Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            qualified_count = len(qualified_candidates)
            not_qualified_count = stats['total_candidates'] - qualified_count

            fig, ax = plt.subplots(figsize=(6, 6))
            colors = ['#22c55e', '#ef4444']
            labels = [f'Qualified (≥{match_criteria}%)', f'Not Qualified (<{match_criteria}%)']
            sizes = [qualified_count, not_qualified_count]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 11}
            )
            ax.set_title('Qualification Status', fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            st.markdown("**Breakdown:**")
            st.success(f"✅ Qualified: {qualified_count} ({(qualified_count/stats['total_candidates']*100):.1f}%)")
            st.error(f"❌ Not Qualified: {not_qualified_count} ({(not_qualified_count/stats['total_candidates']*100):.1f}%)")

            st.markdown("**Criteria Impact:**")
            if qual_rate >= 50:
                st.info("🎯 Good pool size - criteria is working well")
            elif qual_rate >= 25:
                st.warning("⚖️ Moderate pool - consider if sufficient")
            else:
                st.error("⚠️ Small pool - consider lowering criteria")

        # Export section
        st.markdown("---")
        st.markdown("### 📥 Export Qualified Candidates")

        col1, col2 = st.columns(2)

        with col1:
            if not qualified_candidates.empty:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    qualified_candidates.to_excel(writer, index=False, sheet_name='Qualified')
                output.seek(0)

                st.download_button(
                    label=f"📊 Download Qualified (≥{match_criteria}%) as Excel",
                    data=output,
                    file_name=f"qualified_candidates_{match_criteria}pct_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.info("No qualified candidates to export")

        with col2:
            if not qualified_candidates.empty:
                csv = qualified_candidates.to_csv(index=False)
                st.download_button(
                    label=f"📄 Download Qualified as CSV",
                    data=csv,
                    file_name=f"qualified_candidates_{match_criteria}pct_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("📭 No data available yet for this filter.")

# ==================== TAB 3: QUALIFIED CANDIDATES ====================
with tab3:
    st.markdown(f"### 👥 Qualified Candidates (≥{match_criteria}%) - Filter: {selected_job_label}")

    if not qualified_candidates.empty:
        # Additional filters
        col1, col2 = st.columns(2)

        with col1:
            search_name = st.text_input("🔍 Search by Name")

        with col2:
            sort_by = st.selectbox("Sort By", ["Score (High to Low)", "Score (Low to High)", "Name (A-Z)", "Date (Recent First)"])

        # Apply filters
        filtered_df = qualified_candidates.copy()

        if search_name:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]

        # Apply sorting
        if sort_by == "Score (High to Low)":
            filtered_df = filtered_df.sort_values('match_score', ascending=False)
        elif sort_by == "Score (Low to High)":
            filtered_df = filtered_df.sort_values('match_score', ascending=True)
        elif sort_by == "Name (A-Z)":
            filtered_df = filtered_df.sort_values('name')
        else:
            filtered_df = filtered_df.sort_values('screened_at', ascending=False)

        st.success(f"✅ Showing {len(filtered_df)} qualified candidates")

        # Display candidates
        for idx, row in filtered_df.iterrows():
            score = row['match_score']
            score_emoji = "🌟" if score >= 85 else "⭐" if score >= 75 else "✅"

            with st.expander(f"{score_emoji} **{row['name']}** - {score:.1f}%", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"📧 **Email:** {row['email']}")
                    st.write(f"📅 **Screened:** {row['screened_at']}")
                    # Show how much above criteria
                    above_criteria = score - match_criteria
                    st.write(f"📈 **Above Criteria:** +{above_criteria:.1f}%")

                with col2:
                    st.metric("Match Score", f"{score:.1f}%")

                st.markdown("---")

                # Tabs for details
                tab_a, tab_b, tab_c = st.tabs(["✅ Strengths", "💡 Improvements", "🎯 Recommendations"])

                with tab_a:
                    if row['strengths']:
                        for strength in row['strengths']:
                            st.success(f"✓ {strength}")
                    else:
                        st.info("No strengths data available")

                with tab_b:
                    if row['weaknesses']:
                        for weakness in row['weaknesses']:
                            st.warning(f"• {weakness}")
                    else:
                        st.info("No weaknesses data available")

                with tab_c:
                    if row['recommendations']:
                        for rec in row['recommendations']:
                            st.info(f"→ {rec}")
                    else:
                        st.info("No recommendations available")
    else:
        st.warning(f"⚠️ No candidates meet the current criteria of {match_criteria}% for this filter.")
        st.info("💡 Try selecting a different job or lowering the match criteria using the slider at the top of the page")

# ==================== TAB 4: JOB MANAGEMENT ====================
with tab4:
    st.markdown("### 🧾 Job Management")

    # Add new job
    st.markdown("#### ➕ Create New Job Posting")
    new_title = st.text_input("Position Title", key="new_job_title")
    new_description = st.text_area("Job Description", key="new_job_desc", height=160)
    new_requirements = st.text_area("Requirements (optional)", key="new_job_reqs", height=80)

    if st.button("Create Job Posting", use_container_width=True):
        if not new_title.strip() or not new_description.strip():
            st.error("Title and Description are required to create a job posting.")
        else:
            db.add_job_description(new_title.strip(), new_description.strip(), new_requirements.strip() if new_requirements else None)
            st.success(f"✅ Job '{new_title.strip()}' created.")
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### 📝 Existing Job Postings")
    jobs = db.get_job_descriptions()
    if jobs.empty:
        st.info("No job postings available yet.")
    else:
        for _, job in jobs.iterrows():
            jid = int(job['id'])
            with st.expander(f"{job['title']} (id:{jid})", expanded=False):
                st.write(f"**Created:** {job['created_at']}")
                st.write("**Description:**")
                st.write(job['description'])
                if job['requirements']:
                    st.write("**Requirements:**")
                    st.write(job['requirements'])

                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    edit_title = st.text_input(f"Edit Title {jid}", value=job['title'], key=f"edit_title_{jid}")
                    edit_desc = st.text_area(f"Edit Description {jid}", value=job['description'], key=f"edit_desc_{jid}", height=150)
                    edit_reqs = st.text_area(f"Edit Requirements {jid}", value=job['requirements'] or "", key=f"edit_reqs_{jid}", height=80)
                with col2:
                    if st.button("Update", key=f"update_job_{jid}"):
                        db.update_job_description(jid, title=edit_title.strip(), description=edit_desc.strip(), requirements=edit_reqs.strip())
                        st.success("✅ Job updated.")
                        st.experimental_rerun()
                with col3:
                    if st.button("Delete", key=f"delete_job_{jid}"):
                        if st.session_state.get(f"confirm_delete_{jid}", False):
                            db.delete_job_description(jid)
                            st.success("✅ Job deleted.")
                            st.experimental_rerun()
                        else:
                            st.session_state[f"confirm_delete_{jid}"] = True
                            st.warning("⚠️ Click again to confirm deletion of this job posting.")

# ==================== TAB 5: SETTINGS ====================
with tab5:
    st.markdown("### ⚙️ Settings & Database Management")

    # Criteria management
    st.markdown("#### 🎯 Match Criteria Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Set to High (80%)", use_container_width=True):
            st.session_state.match_criteria = 80
            st.rerun()

    with col2:
        if st.button("Set to Medium (70%)", use_container_width=True):
            st.session_state.match_criteria = 70
            st.rerun()

    with col3:
        if st.button("Set to Low (60%)", use_container_width=True):
            st.session_state.match_criteria = 60
            st.rerun()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💾 Backup & Export")

        if st.button("🔄 Create Database Backup", use_container_width=True):
            backup_path = db.backup_database()
            st.success(f"✅ Backup created: {backup_path}")

        if st.button("📥 Export All Data (CSV)", use_container_width=True):
            csv_path = db.export_to_csv()
            st.success(f"✅ Exported to: {csv_path}")

    with col2:
        st.markdown("#### 📊 Database Statistics")
        stats = db.get_statistics()

        st.metric("Total Candidates", stats['total_candidates'])
        st.metric("Total Screenings", stats['total_screenings'])

        try:
            db_size = Path('resume_screening.db').stat().st_size / 1024
            st.metric("Database Size", f"{db_size:.2f} KB")
        except:
            st.metric("Database Size", "N/A")

    st.markdown("---")

    st.markdown("#### 🗑️ Danger Zone")
    st.warning("⚠️ The following actions are irreversible!")

    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.session_state.get('confirm_clear_recruiter', False):
            db.clear_all_data()
            st.session_state.chat_history = []
            st.success("✅ All data cleared!")
            st.session_state.confirm_clear_recruiter = False
            st.rerun()
        else:
            st.session_state.confirm_clear_recruiter = True
            st.error("⚠️ Click again to confirm deletion of ALL data!")
