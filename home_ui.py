import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    """Initialize all session state variables"""
    if "df_results" not in st.session_state:
        st.session_state.df_results = pd.DataFrame()
    if "last_updated" not in st.session_state:
        st.session_state.last_updated = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None

def get_stats():
    """Calculate statistics from results dataframe"""
    if "df_results" not in st.session_state or st.session_state.df_results.empty:
        return {
            "total": 0,
            "avg_score": 0,
            "top_score": 0,
            "qualified": 0
        }
    
    df = st.session_state.df_results
    scores = df["Score"].str.replace('%', '').astype(float)
    
    return {
        "total": len(df),
        "avg_score": scores.mean(),
        "top_score": scores.max(),
        "qualified": len(scores[scores >= 70])  # Candidates with 70%+ score
    }

def render_portal_card(title, icon, description, gradient, benefits):
    """Render a portal card with consistent styling"""
    benefits_html = "<br>".join([f"✓ {benefit}" for benefit in benefits])
    
    st.markdown(f"""
    <div style="padding: 35px; border-radius: 15px;
                background: linear-gradient(135deg, {gradient[0]} 0%, {gradient[1]} 100%);
                color: white; text-align: center;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                margin-bottom: 20px;
                transition: transform 0.3s ease;
                border: 2px solid rgba(255,255,255,0.1);">
        <div style="font-size: 48px; margin-bottom: 15px;">{icon}</div>
        <h2 style="color: white; margin-bottom: 20px; font-size: 24px;">{title}</h2>
        <p style="font-size: 15px; line-height: 1.8; opacity: 0.95;">
        {benefits_html}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_stat_card(label, value, icon, color="#4a90e2"):
    """Render an animated statistics card"""
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 12px;
                background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                color: white; text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border: 1px solid rgba(255,255,255,0.2);">
        <div style="font-size: 32px; margin-bottom: 10px;">{icon}</div>
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{value}</div>
        <div style="font-size: 14px; opacity: 0.9;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def home_layout():
    """Main home page layout"""
    # Initialize session state
    initialize_session_state()
    
    # Header with animation
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 42px; font-weight: 700; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   margin-bottom: 10px;">
            📑 Resume Screening AI Portal
        </h1>
        <p style="font-size: 18px; color: #666; margin-top: 0;">
            Powered by Advanced AI • Fast • Accurate • Intelligent
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                padding: 25px; border-radius: 15px; margin: 20px 0;
                border-left: 4px solid #667eea;">
        <h2 style="margin-top: 0; color: #333;">👋 Welcome!</h2>
        <p style="font-size: 16px; line-height: 1.8; color: #555; margin-bottom: 0;">
            Transform your hiring process with AI-powered resume screening. 
            Whether you're a candidate looking to showcase your skills or a recruiter 
            searching for the perfect match, we've got you covered.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Choose Your Portal")
    
    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_portal_card(
            title="Candidate Portal",
            icon="👤",
            description="For job seekers",
            gradient=["#667eea", "#764ba2"],
            benefits=[
                "Upload your resume instantly",
                "Get AI-powered match scores",
                "Compare against job descriptions",
                "Receive improvement suggestions"
            ]
        )
        if st.button("🚀 Enter Candidate Portal", 
                    use_container_width=True, 
                    type="primary",
                    key="candidate_btn"):
            st.session_state.user_role = "candidate"
            st.switch_page("pages/candidate_portal.py")

    with col2:
        render_portal_card(
            title="Recruiter Portal",
            icon="🏢",
            description="For hiring managers",
            gradient=["#f093fb", "#f5576c"],
            benefits=[
                "View all candidate results",
                "Chat with AI assistant",
                "Get detailed analytics",
                "Export and manage data"
            ]
        )
        if st.button("🚀 Enter Recruiter Portal", 
                    use_container_width=True, 
                    type="primary",
                    key="recruiter_btn"):
            st.session_state.user_role = "recruiter"
            st.switch_page("pages/recruiter_portal.py")

    # Features section
    st.markdown("---")
    st.markdown("### ✨ Key Features")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 40px; margin-bottom: 10px;">⚡</div>
            <h4>Lightning Fast</h4>
            <p style="color: #666; font-size: 14px;">Process resumes in seconds with our optimized AI engine</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 40px; margin-bottom: 10px;">🎯</div>
            <h4>Highly Accurate</h4>
            <p style="color: #666; font-size: 14px;">Advanced matching algorithms ensure precise results</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
            <h4>Secure & Private</h4>
            <p style="color: #666; font-size: 14px;">Your data is encrypted and never shared</p>
        </div>
        """, unsafe_allow_html=True)

    
    # Info banner
    st.markdown("---")
    st.info("💡 **Pro Tip:** Use the sidebar navigation to quickly switch between portals and access additional features!")
    
    # Footer
    if st.session_state.last_updated:
        st.caption(f"📅 Last updated: {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #999; font-size: 13px;">
        <p>Made with ❤️ for better hiring decisions</p>
    </div>
    """, unsafe_allow_html=True)