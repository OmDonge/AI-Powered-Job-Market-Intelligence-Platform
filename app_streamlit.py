import os
import mysql.connector
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from google import genai

# ==========================================
# 1. APPLICATION LEVEL CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Career Intelligence Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, corporate-ready typography and interface styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1 { color: #0f172a; font-family: 'Segoe UI', sans-serif; font-weight: 700; letter-spacing: -0.5px; }
    h3 { color: #475569; font-weight: 500; }
    .status-badge {
        background-color: #f0fdf4; color: #166534; padding: 12px 16px; 
        border-radius: 8px; border: 1px solid #bbf7d0; font-weight: 600; font-size: 14px;
        text-align: center; margin-bottom: 16px; margin-top: 10px;
    }
    .metric-box {
        background-color: #ffffff; padding: 24px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; border-top: 4px solid #2563eb; text-align: center;
    }
    .metric-val { font-size: 38px; font-weight: 800; color: #1e40af; margin-top: 4px; }
    .report-container {
        background-color: #ffffff; padding: 35px; border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; margin-top: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Instantiating clean application state memory blocks
if "saved_pwd" not in st.session_state:
    st.session_state["saved_pwd"] = ""
if "saved_key" not in st.session_state:
    st.session_state["saved_key"] = ""


# ==========================================
# 2. DATA EXTRACTION LAYER (HOISTED FOR INSTANT VERIFICATION)
# ==========================================
@st.cache_data(show_spinner=False)
def fetch_market_analytics(pwd):
    try:
        db_connection = mysql.connector.connect(
            host="localhost", user="root", password=pwd, database="job_market_db"
        )

        query_skills = """
        SELECT s1.Skill_Name AS Skill_A, s2.Skill_Name AS Skill_B, COUNT(*) AS Combination_Count
        FROM Bridge_Job_Skills js1
        JOIN Bridge_Job_Skills js2 ON js1.Job_ID = js2.Job_ID AND js1.Skill_ID < js2.Skill_ID
        JOIN Dim_Skills s1 ON js1.Skill_ID = s1.Skill_ID
        JOIN Dim_Skills s2 ON js2.Skill_ID = s2.Skill_ID
        GROUP BY s1.Skill_Name, s2.Skill_Name
        ORDER BY Combination_Count DESC;
        """
        df_skills = pd.read_sql(query_skills, db_connection)

        query_salaries = """
        SELECT l.City, ROUND(AVG(f.Salary_Max_LPA), 2) AS Avg_Max_Salary_LPA, ROUND(AVG(f.Applications_Received), 0) AS Avg_Applications
        FROM Fact_Jobs f
        JOIN Dim_Locations l ON f.Location_ID = l.Location_ID
        GROUP BY l.City ORDER BY Avg_Max_Salary_LPA DESC;
        """
        df_salaries = pd.read_sql(query_salaries, db_connection)

        db_connection.close()
        return df_skills, df_salaries, None
    except Exception as e:
        return None, None, str(e)


# Run connectivity verification passes before mounting UI elements
df_skills, df_salaries, db_error = None, None, None
db_verified = False
ai_verified = False

if st.session_state["saved_pwd"]:
    df_skills, df_salaries, db_error = fetch_market_analytics(st.session_state["saved_pwd"])
    if db_error is None:
        db_verified = True

if st.session_state["saved_key"]:
    ai_verified = True

# ==========================================
# 3. SIDEBAR CREDENTIAL HANDLING (AUTO-MASKING)
# ==========================================
st.sidebar.header("⚙️ Connection Configuration")

# Secure layout masking logic for MySQL parameters
if not db_verified:
    input_pwd = st.sidebar.text_input("MySQL Root Password", type="password", value=st.session_state["saved_pwd"])
    if input_pwd != st.session_state["saved_pwd"]:
        st.session_state["saved_pwd"] = input_pwd
        st.rerun()
else:
    st.sidebar.markdown("<div class='status-badge'>🔒 Database Connected</div>", unsafe_allow_html=True)

# Secure layout masking logic for Gemini parameters
if not ai_verified:
    input_key = st.sidebar.text_input("Gemini API Key", type="password", value=st.session_state["saved_key"])
    if input_key != st.session_state["saved_key"]:
        st.session_state["saved_key"] = input_key
        st.rerun()
else:
    st.sidebar.markdown("<div class='status-badge'>⚡ Gemini Connected</div>", unsafe_allow_html=True)

# Session Reset Controller Node
if db_verified or ai_verified:
    st.sidebar.markdown(" ")
    if st.sidebar.button("Reset Secure Connections", use_container_width=True):
        st.session_state["saved_pwd"] = ""
        st.session_state["saved_key"] = ""
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Active Warehouse Layer")
st.sidebar.info("Database Scope: `job_market_db` \n\nConnection Mode: Python DBAPI Driver")

# ==========================================
# 4. MAIN INTERFACE TYPOGRAPHY & LAYOUT
# ==========================================
st.title("💼 AI-Powered Job Market Intelligence Platform")
st.markdown("### SQL + GenAI Career Recommendation System")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🛠️ Candidate Profile Options")

    available_skills = ["SQL", "Power BI", "Python", "Excel", "Tableau", "MySQL", "Azure", "AWS", "GCP",
                        "Machine Learning", "GenAI"]
    selected_skills = st.multiselect("Select your active skills:", available_skills, default=["SQL", "Power BI"])

    custom_skills = st.text_input("Add extra skills manually (comma-separated):", "")

    final_skills = [s.strip() for s in selected_skills]
    if custom_skills:
        final_skills.extend([s.strip() for s in custom_skills.split(",") if s.strip()])
    skills_string = ", ".join(final_skills)

    # SYSTEM PROFILE FIT RATING CALIBRATION
    st.markdown("---")
    st.markdown("#### 🧠 Profile Evaluation")

    if df_skills is not None and not df_skills.empty and len(final_skills) > 0:
        top_pairs = df_skills.head(10)
        total_top_volume = top_pairs['Combination_Count'].sum()

        user_matched_volume = 0
        for _, row in top_pairs.iterrows():
            has_a = row['Skill_A'] in final_skills
            has_b = row['Skill_B'] in final_skills

            if has_a and has_b:
                user_matched_volume += row['Combination_Count']
            elif has_a or has_b:
                user_matched_volume += row['Combination_Count'] * 0.4

        calculated_score = int((user_matched_volume / total_top_volume) * 100) if total_top_volume > 0 else 0
        calculated_score = max(5, min(calculated_score, 82))  # Set realistic ceiling index boundary

        st.markdown(f"""
            <div class='metric-box'>
                <div style='font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase;'>Calculated Market Fit Score</div>
                <div class='metric-val'>{calculated_score}%</div>
                <div style='font-size: 12px; color: #64748b; margin-top: 6px;'>Weighted against top core recruiter co-occurrence trends</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Select active skills to initialize real-time profile analytics ranking.")

    if df_salaries is not None and not df_salaries.empty:
        st.markdown("---")
        st.markdown("#### 🔍 Filter Regions")
        city_options = ["All Regions"] + list(df_salaries['City'].unique())
        selected_city = st.selectbox("Select target market view:", city_options)

with col2:
    st.markdown("### 📊 Live Analytics View")

    if not st.session_state["saved_pwd"]:
        st.warning("ℹ️ System Status: Awaiting valid database connection strings inside secure sidebar.")
    elif db_error:
        st.error(f"❌ Connection Error: {db_error}")
    else:
        # DATA PRESENTATION ELEMENT A: REGIONAL COMPARATIVE SCALE
        if df_salaries is not None and not df_salaries.empty:
            if selected_city != "All Regions":
                filtered_salaries = df_salaries[df_salaries['City'] == selected_city]
            else:
                filtered_salaries = df_salaries

            fig_market = go.Figure()
            fig_market.add_trace(go.Bar(
                x=filtered_salaries['City'], y=filtered_salaries['Avg_Max_Salary_LPA'],
                name='Avg Max Salary (LPA)', marker_color='#1e3a8a', yaxis='y1'
            ))
            fig_market.add_trace(go.Scatter(
                x=filtered_salaries['City'], y=filtered_salaries['Avg_Applications'],
                name='Avg Applications', line=dict(color='#ef4444', width=3), yaxis='y2'
            ))
            fig_market.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
                yaxis=dict(title="Salary (LPA Range)"),
                yaxis2=dict(title="Applications Received", overlaying='y', side='right'),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_market, use_container_width=True)

        # DATA PRESENTATION ELEMENT B: DENSE METRIC HISTOGRAM
        if df_skills is not None and not df_skills.empty:
            df_skills_preview = df_skills.head(5).copy()
            df_skills_preview['Skill_Pair'] = df_skills_preview['Skill_A'] + " + " + df_skills_preview['Skill_B']

            fig_skills = px.bar(
                df_skills_preview, x='Combination_Count', y='Skill_Pair', orientation='h',
                labels={'Combination_Count': 'Job Postings', 'Skill_Pair': 'Skill Combination'},
                color='Combination_Count', color_continuous_scale='Blugrn'
            )
            fig_skills.update_layout(showlegend=False, height=180, margin=dict(l=10, r=10, t=10, b=10),
                                     plot_bgcolor='rgba(0,0,0,0)')
            fig_skills.update_coloraxes(showscale=False)
            st.plotly_chart(fig_skills, use_container_width=True)

# ==========================================
# 5. GLOBAL PIPELINE EXECUTION LAYER (OUTSIDE OF COLUMNS FOR HIGH VISIBILITY)
# ==========================================
st.markdown("---")

if db_verified:
    if st.button("🚀 Run Live Pipeline & Generate Strategy Report", use_container_width=True):
        if not st.session_state["saved_key"]:
            st.error("🔑 Missing Credentials: Please key in your valid Gemini API Token inside the configuration menu.")
        else:
            with st.spinner("Streaming operational matrices from MySQL to Gemini 2.5 Flash Engine..."):
                try:
                    skill_trends_str = df_skills.head(10).to_string()
                    salary_trends_str = df_salaries.to_string()

                    prompt = f"""
                    You are an expert technical recruiter and AI Career Strategist specializing in the Indian tech market.
                    A candidate seeking an Analyst Trainee role has input their current skill stack: {skills_string}
                    Our platform's database analysis has calculated their realistic baseline market fit score as: {calculated_score}%

                    Here is live data pulled directly from our custom SQL Database Analytics Engine:
                    1. Highly co-occurring critical skill pairs: {skill_trends_str}
                    2. Indian regional city salary (LPA) and application benchmarks: {salary_trends_str}

                    Based strictly on this data and your recruiting expertise, construct a clear, professional "Skill Gap Analysis Report".
                    Provide a clean layout with helpful headers, bullet points, and clear bold text highlights:
                    - **1. PROFILE EVALUATION CRITIQUE**: Interpret why the candidate scored exactly {calculated_score}% for this market. Explain the gap from a data perspective.
                    - **2. CRITICAL SKILL GAPS**: Point out specific missing toolsets from the high-frequency combinations that unlock higher compensation bands.
                    - **3. TARGET HIRING MARKETS**: Pinpoint which cities they should prioritize based on optimal salary-to-competition ratios in the live trends.
                    - **4. 3-STEP ROADMAP**: Provide clear milestones on what tools to learn next to pass entry-level engineering screenings.
                    """

                    max_retries = 3
                    initial_backoff = 2
                    response = None

                    for attempt in range(max_retries):
                        try:
                            client = genai.Client(api_key=st.session_state["saved_key"])
                            response = client.models.generate_content(
                                model='gemini-2.5-flash', contents=prompt,
                            )
                            break
                        except Exception as ai_err:
                            # Catch and handle 503 Service Unavailable errors gracefully via linear exponential delay shifts
                            if "503" in str(ai_err) and attempt < max_retries - 1:
                                st.warning(
                                    f"⚠️ Gemini Server busy (503). Retrying attempt {attempt + 1}/{max_retries} in {initial_backoff}s...")
                                time.sleep(initial_backoff)
                                initial_backoff *= 2
                            else:
                                raise ai_err

                    if response:
                        st.session_state['generation_output'] = response.text
                    else:
                        st.error(
                            "❌ Unable to reach the AI Engine after multiple retries. Please click the button to try again.")

                except Exception as final_err:
                    st.error(f"GenAI Infrastructure Error: {final_err}")

    # Render Report Content & Download options globally at the bottom border layout
    if 'generation_output' in st.session_state:
        st.markdown("<div class='report-container'>", unsafe_allow_html=True)
        st.markdown("## 📊 Personal Market Intelligence Report")
        st.markdown(st.session_state['generation_output'])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(" ")
        st.download_button(
            label="📥 Download Strategy Briefing Document (.txt)",
            data=st.session_state['generation_output'],
            file_name="Analyst_Trainee_Market_Intelligence_Brief.txt",
            mime="text/plain",
            use_container_width=True
        )

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #9ca3af; font-size: 11px;'>Architecture Pipeline: Streamlit Server v1.35+ | Plotly Visualization Engine | Core AI: Gemini 2.5 Flash Engine</p>",
    unsafe_allow_html=True)