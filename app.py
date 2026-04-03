import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. PAGE CONFIG & PREMIUM THEME ---
st.set_page_config(page_title="Executive IT Insights", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for high-end "SaaS Dashboard" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #30363d; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric label { color: #8b949e !important; font-size: 14px !important; font-weight: 700 !important; text-transform: uppercase; }
    .stMetric div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; }
    .section-header { 
        color: #58a6ff; 
        font-family: 'Inter', sans-serif; 
        font-size: 22px; 
        font-weight: 800; 
        margin-top: 40px; 
        border-left: 5px solid #58a6ff; 
        padding-left: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 IT Operations Strategic Overview")
st.markdown("<p style='color: #8b949e; font-size: 1.1rem;'>Strategic health, delivery velocity, and risk assessment.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload 'Track with IT.xlsx'", type=["xlsx"])

if uploaded_file:
    try:
        # --- 2. DATA ENGINE ---
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # Forward Fill logic (Domain, Type, Category, Status, Duration, Severity)
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        df_clean = df.dropna(subset=['Category']).copy()

        # Duration Parsing (Weeks)
        def extract_weeks(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks_match = re.search(r'(\d+)\s*week', str(text))
            return int(weeks_match.group(1)) if weeks_match else 0

        df_clean['Weeks_Open'] = df_clean['Duration'].apply(extract_weeks)

        # --- 3. EXECUTIVE KPI ROW ---
        m1, m2, m3, m4 = st.columns(4)
        
        total_unique = df_clean['Category'].nunique()
        sub_cat_total = len(df_clean[~df_clean['Sub-Category'].isin(['-', None, 'nan'])])
        avg_weeks = int(df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()) if not df_clean.empty else 0
        critical_tasks = len(df_clean[df_clean['Severity'].str.contains('Critical', case=False, na=False)])

        m1.metric("Tasks (Categories)", total_unique)
        m2.metric("Total Sub-Tasks", sub_cat_total)
        m3.metric("Average Project Age", f"{avg_weeks} Weeks")
        m4.metric("Critical Tasks", critical_tasks)

        # --- 4. THE AGING REPORT (Main Executive Focus) ---
        st.markdown("<div class='section-header'>⏳ Aging Report (Active Projects)</div>", unsafe_allow_html=True)
        
        # Severity Colors
        sev_colors = {'Critical': '#F94144', 'High': '#F3722C', 'Medium': '#F9C74F', 'Low': '#90BE6D'}
        
        # Group by Category and Severity to show max weeks
        cat_aging = df_clean.groupby(['Category', 'Severity'])['Weeks_Open'].max().reset_index()
        cat_aging = cat_aging[cat_aging['Weeks_Open'] > 0].sort_values(by='Weeks_Open', ascending=True)
        
        # Dynamic height for the bar chart based on the number of items
        chart_height = 400 + (len(cat_aging) * 25)

        fig_aging = px.bar(cat_aging, x='Weeks_Open', y='Category', orientation='h',
                          color='Severity', text='Weeks_Open', height=chart_height,
                          color_discrete_map=sev_colors,
                          labels={'Weeks_Open': 'WEEKS OPEN'})
        
        fig_aging.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font_color="white",
            xaxis=dict(showgrid=True, gridcolor='#30363d'), 
            yaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_aging.update_traces(texttemplate=' %{text} Weeks', textposition='outside')
        st.plotly_chart(fig_aging, use_container_width=True)

        # --- 5. DETAILED INVENTORY ---
        st.markdown("<div class='section-header'>🔍 Project Inventory</div>", unsafe_allow_html=True)
        with st.expander("Click to view full project breakdown"):
            display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration', 'Severity']
            st.dataframe(df_clean[display_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Executive System Error: {e}")
else:
    st.info("Awaiting 'Track with IT.xlsx' for executive synthesis...")
