import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Page Configuration
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

# 2. Dark Mode Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    [data-testid="stMetricValue"] {
        color: #00CC96;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Executive IT Tracking Overview")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- DATA PROCESSING FOR DURATION ---
        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-", "0"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(df))
        kpi2.metric("Critical Issues", len(df[df['Severity'] == 'Critical']))
        
        # New Metric: Most Impacted System
        if 'System' in df.columns:
            top_sys = df['System'].mode()[0] if not df['System'].empty else "N/A"
            kpi3.metric("Top System", top_sys)
        else:
            kpi3.metric("Top System", "No Data")
            
        kpi4.metric("Oldest Ticket (Days)", df['Days_Open'].max())

        st.divider()

        # --- ROW 1: STATUS & SYSTEM ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(df, names='Status', hole=0.6, 
                               template="plotly_dark",
                               color_discrete_sequence=px.colors.qualitative.Safe)
            fig_status.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

        with col2:
            st.subheader("🖥️ Tickets by System")
            if 'System' in df.columns:
                sys_counts = df['System'].value_counts().reset_index()
                fig_sys = px.bar(sys_counts, x='System', y='count', 
                                template="plotly_dark",
                                color='System', 
                                color_discrete_sequence=px.colors
