import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IT Executive Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; }
    .section-header { color: #58a6ff; font-size: 18px; font-weight: 700; border-left: 4px solid #58a6ff; padding-left: 10px; margin: 15px 0 10px 0; }
    .stPlotlyChart { margin-bottom: -20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 IT Operations Strategic Overview")

uploaded_file = st.file_uploader("Upload 'Track with IT.xlsx'", type=["xlsx"])

if uploaded_file:
    try:
        # --- 2. DATA ENGINE ---
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()
        
        # Data Cleaning & Forward Fill
        cols_to_fill = [c for c in ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity'] if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()
        df_clean = df.dropna(subset=['Category']).copy()

        def extract_weeks(text):
            weeks_match = re.search(r'(\d+)\s*week', str(text))
            return int(weeks_match.group(1)) if weeks_match else 0
        df_clean['Weeks_Open'] = df_clean['Duration'].apply(extract_weeks)

        # --- 3. KPI ROW ---
        m1, m2, m3, m4 = st.columns(4)
        avg_weeks = int(df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()) if not df_clean.empty else 0
        critical_count = len(df_clean[df_clean['Severity'].str.contains('Critical', case=False, na=False)])
        
        m1.metric("Categories", df_clean['Category'].nunique())
        m2.metric("Sub-Tasks", len(df_clean[df_clean['Sub-Category'].notna()]))
        m3.metric("Avg Project Age", f"{avg_weeks} Wks")
        m4.metric("Critical Risks", critical_count)

        # --- 4. DASHBOARD GRID ---
        col1, col2 = st.columns(2)
        sev_colors = {'Critical': '#F94144', 'High': '#F3722C', 'Medium': '#F9C74F', 'Low': '#90BE6D'}

        with col1:
            st.markdown("<div class='section-header'>Delivery & Domain</div>", unsafe_allow_html=True)
            # Delivery Status
            fig_status = px.pie(df_clean, names='Status', hole=0.5, height=250,
                                color='Status', color_discrete_map={'Open': '#FFA500', 'Closed': '#2EB67D'})
            fig_status.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Domain Allocation
            dom_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.bar(dom_counts, x='Category', y='Domain', orientation='h', height=250,
                             title="Tasks by Domain", color_discrete_sequence=['#58a6ff'])
            fig_dom.update_layout(margin=dict(t=30, b=0, l=0, r=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_dom, use_container_width=True)

        with col2:
            st.markdown("<div class='section-header'>Risk & Type</div>", unsafe_allow_html=True)
            # Severity
            sev_order = ['Critical', 'High', 'Medium', 'Low']
            available_sevs = [s for s in sev_order if s in df_clean['Severity'].unique()]
            fig_sev = px.bar(df_clean['Severity'].value_counts().reindex(available_sevs).reset_index(), 
                             x='Severity', y='count', color='Severity', height=250,
                             color_discrete_map=sev_colors, title="Severity Distribution")
            fig_sev.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_sev, use_container_width=True)

            # Aging Report (Mini version for one-page feel)
            cat_aging = df_clean.groupby(['Category', 'Severity'])['Weeks_Open'].max().reset_index().sort_values('Weeks_Open', ascending=False).head(10)
            fig_aging = px.bar(cat_aging, x='Weeks_Open', y='Category', orientation='h', height=250,
                               color='Severity', color_discrete_map=sev_colors, title="Top 10 Aging Projects")
            fig_aging.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False, xaxis_title="Weeks", yaxis_title=None)
            st.plotly_chart(fig_aging, use_container_width=True)

        # --- 5. FOOTER DATA ---
        with st.expander("🔍 Full Project Inventory"):
            st.dataframe(df_clean[['Category', 'Status', 'Domain', 'Severity', 'Weeks_Open']].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload 'Track with IT.xlsx' to generate the executive view.")
