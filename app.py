import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Executive IT Insights", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a "Premium" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
    }
    .stMetric label { color: #8b949e !important; font-size: 16px !important; font-weight: 600 !important; }
    .stMetric div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 32px !important; }
    .section-header { 
        color: #58a6ff; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-size: 24px; 
        font-weight: bold; 
        margin-top: 30px; 
        border-bottom: 1px solid #30363d; 
        padding-bottom: 10px; 
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Executive IT Operations Dashboard")
st.markdown("<p style='color: #8b949e;'>Real-time strategic overview of project aging, domain health, and delivery status.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload 'Track with IT.xlsx'", type=["xlsx"])

if uploaded_file:
    try:
        # --- 2. DATA ENGINE ---
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # Forward Fill logic
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

        # --- 3. TOP-LEVEL STRATEGIC METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        
        total_unique = df_clean['Category'].nunique()
        sub_cat_total = len(df_clean[~df_clean['Sub-Category'].isin(['-', None, 'nan'])])
        avg_weeks = int(df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()) if not df_clean.empty else 0
        critical_tasks = len(df_clean[df_clean['Severity'] == 'Critical'])

        m1.metric("STRATEGIC PROJECTS", total_unique)
        m2.metric("TOTAL SUB-TASKS", sub_cat_total)
        m3.metric("AVG. VELOCITY", f"{avg_weeks} Wks")
        m4.metric("CRITICAL BLOCKERS", critical_tasks)

        # --- 4. THE VISUAL SUITE ---
        st.markdown("<div class='section-header'>Strategic Health Metrics</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            # STATUS: Orange for Open, Green for Closed
            fig_status = px.pie(df_clean, names='Status', hole=0.6,
                               color='Status',
                               color_discrete_map={'Open': '#FFA500', 'Closed': '#2EB67D'},
                               title="<b>Delivery Status</b>")
            fig_status.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            fig_status.update_traces(textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig_status, use_container_width=True)

        with c2:
            # DOMAIN: De-duplicated Categories
            dom_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.pie(dom_counts, names='Domain', values='Category', hole=0.6,
                             color_discrete_sequence=px.colors.sequential.Blues_r,
                             title="<b>Domain Distribution</b>")
            fig_dom.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            fig_dom.update_traces(textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig_dom, use_container_width=True)

        with c3:
            # SEVERITY: Bar Chart
            sev_order = ['Critical', 'High', 'Medium', 'Low']
            available_sevs = [s for s in sev_order if s in df_clean['Severity'].unique()]
            sev_counts = df_clean['Severity'].value_counts().reindex(available_sevs).fillna(0).reset_index()
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                             color='Severity',
                             color_discrete_map={'Critical': '#F94144', 'High': '#F3722C', 'Medium': '#F9C74F', 'Low': '#90BE6D'},
                             title="<b>Risk Profile</b>")
            fig_sev.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_sev, use_container_width=True)

        # --- 5. THE AGING REPORT ---
        st.markdown("<div class='section-header'>⏳ Portfolio Aging Report (All Items > 0 Wks)</div>", unsafe_allow_html=True)
        
        cat_aging = df_clean.groupby(['Category', 'Severity'])['Weeks_Open'].max().reset_index()
        cat_aging = cat_aging[cat_aging['Weeks_Open'] > 0].sort_values(by='Weeks_Open', ascending=True)
        
        chart_height = 400 + (len(cat_aging) * 25)

        fig_aging = px.bar(cat_aging, 
                          x='Weeks_Open', 
                          y='Category', 
                          orientation='h',
                          color='Severity',
                          text='Weeks_Open',
                          height=chart_height,
                          color_discrete_map={'Critical': '#F94144', 'High': '#F3722C', 'Medium': '#F9C74F', 'Low': '#90BE6D'},
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

        # --- 6. RAW DATA ---
        st.markdown("<div class='section-header'>🔍 Project Inventory</div>", unsafe_allow_html=True)
        display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration', 'Severity']
        st.dataframe(df_clean[display_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Executive System Error: {e}")
else:
    st.info("Awaiting 'Track with IT.xlsx' file for processing...")
