import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Force Dark Mode Theme
st.set_page_config(page_title="Executive IT Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to make the background dark and text pop
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_index=True)

st.title("🌙 Executive IT Dashboard (Dark Mode)")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # Data Processing for Duration
        def parse_duration(text):
            if pd.isna(text) or text == "": return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- Top Level KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(df))
        kpi2.metric("Critical", len(df[df['Severity'] == 'Critical']))
        kpi3.metric("Avg. Age (Days)", int(df[df['Days_Open'] > 0]['Days_Open'].mean()))
        kpi4.metric("Oldest (Days)", df['Days_Open'].max())

        st.divider()

        # --- Charts Row ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📋 Status Distribution")
            # Dark Donut Chart
            fig_status = px.pie(df, names='Status', hole=0.6, 
                               template="plotly_dark",
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)

        with col_right:
            st.subheader("⚠️ Severity Breakdown")
            # Dark Bar Chart
            sev_counts = df['Severity'].value_counts().reset_index()
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                            color='Severity',
                            template="plotly_dark",
                            color_discrete_map={'Critical': '#FF4B4B', 'High': '#FFAA00', '3 - Medium (P3)': '#00CC96'})
            st.
