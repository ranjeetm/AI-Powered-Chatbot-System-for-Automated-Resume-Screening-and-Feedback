import streamlit as st
import pandas as pd
from home_ui import home_layout
from database import ResumeDatabase

# Set page config first
st.set_page_config(
    page_title="Resume Screening AI Portal",
    page_icon="📑",
    layout="centered"
)

# Initialize database connection (cached)
@st.cache_resource
def get_database():
    """Get database connection (cached across sessions)"""
    return ResumeDatabase()

# Initialize database
db = get_database()

# Initialize session state with database data
if "db_loaded" not in st.session_state:
    st.session_state.db_loaded = True
    # Load data from database instead of empty dataframe
    st.session_state.df_results = db.get_screening_results()

# Run the home page layout with updated stats from database
home_layout()

# Portal navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Go to Candidate Portal", use_container_width=True, type="primary"):
        st.switch_page("pages/candidate_portal.py")

with col2:
    if st.button("🚀 Go to Recruiter Portal", use_container_width=True, type="primary"):
        st.switch_page("pages/recruiter_portal.py")

st.markdown("---")

st.info("💡 **Tip:** All your data is automatically saved in the database!")

st.markdown("---")

# Display statistics from database
st.markdown("### 📊 Quick Stats")

stats = db.get_statistics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Resumes", stats['total_candidates'])

with col2:
    st.metric("Avg Score", f"{stats['avg_score']:.1f}%")

with col3:
    st.metric("Top Score", f"{stats['top_score']:.1f}%")

with col4:
    st.metric("Qualified", stats['qualified_candidates'])

# Admin section (optional)
with st.expander("🔧 Database Management"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export to CSV"):
            try:
                file_path = db.export_to_csv()
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f,
                        file_name=file_path,
                        mime="text/csv"
                    )
                st.success(f"✅ Exported to {file_path}")
            except Exception as e:
                st.error(f"Error exporting: {e}")
    
    with col2:
        if st.button("💾 Backup Database"):
            try:
                backup_path = db.backup_database()
                st.success(f"✅ Backup created: {backup_path}")
            except Exception as e:
                st.error(f"Error creating backup: {e}")
    
    with col3:
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                db.clear_all_data()
                st.session_state.df_results = pd.DataFrame()
                st.success("✅ All data cleared!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm deletion!")