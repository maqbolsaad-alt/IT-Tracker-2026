import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; }
    .main { background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Executive IT Tracking Overview")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- DATA PROCESSING ---
        def parse_duration(text):
            if pd.isna(text) or text == "": return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df['Days_Open'] = df['Duration'].apply(parse_duration)
        
        # Guardrail for System column
        if 'System' not in df.columns:
            df['System'] = "Unknown"

        # --- MAIN PAGE FILTER (Moved from Sidebar) ---
        st.subheader("🎯 Dashboard Filters")
        all_systems = sorted(df['System'].unique().tolist())
        
        # Placing the filter in a container for better visual grouping
        selected_systems = st.multiselect(
            "Select System(s) to analyze:", 
            options=all_systems, 
            default=all_systems
        )
        
        # Apply filtering
        filtered_df = df[df['System'].isin(selected_systems)]

        if filtered_df.empty:
            st.warning("No data available for the selected systems.")
        else:
            # --- TOP LEVEL KPIs ---
            st.markdown("### Key Performance Indicators")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Items", len(filtered_df))
            
            # Using a more robust string check for 'Critical'
            crit_count = len(filtered_df[filtered_df['Severity'].str.contains('Critical', case=False, na=False)])
            k2.metric("Critical Issues", crit_count)
            
            avg_days = int(filtered_df[filtered_df['Days_Open'] > 0]['Days_Open'].mean()) if not filtered_df.empty else 0
            k3.metric("Avg. Age (Days)", avg_days)
            
            k4.metric("Active Systems", filtered_df['System'].nunique())

            st.markdown("---")

            # --- ROW 1: SYSTEM
