import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Page Configuration & Dark Theme Setup
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

# Force Dark Mode Styling
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
    """, unsafe_allow_index=True)

st.title("🌙 Executive IT Overview")

uploaded_file = st.file_uploader("Upload your 'Track with IT.xlsx' file", type=["xlsx"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- Helper Function to calculate Days ---
        def parse_to_days(text):
            if pd.isna(text) or str(text).strip() == "" or str(text).strip() == "-":
                return 0
            # Extracts numbers from "X weeks Y days"
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total

        df['Days_Total'] = df['Duration'].apply(parse_to_days)

        # --- KPI Row ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Items", len(df))
        m2.metric("Critical", len(df[df['Severity'] == 'Critical']))
        m3.metric("Pending", len(df[df['Status'] == 'Pending']))
        # Filter out 0s for average (items with no date/duration yet)
        avg_days = int(df[df['Days_Total'] > 0]['Days_Total'].mean()) if not df[df['Days_Total'] > 0].empty else 0
        m4.metric("Avg. Age (Days)", avg_days)

        st.divider()

        # --- Charts Row ---
        left, right = st.columns(2)

        with left:
            st.subheader("📋 Status (Donut)")
            # Create the Donut Chart
            fig_status = px.pie(df, names='Status', hole=0.6, 
                               template="plotly_dark",
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_status.update_layout(showlegend=True)
            st.plotly_chart(fig_status, use_container_width=True)

        with right:
            st.subheader("⚠️ Severity Breakdown")
            # Create the Severity Bar Chart
            sev_order = ['Critical', 'High', '3 - Medium (P3)']
            sev_counts = df['Severity'].value_counts().reindex(sev_order).reset_index()
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                            color='Severity',
                            template="plotly_dark",
                            color_discrete_map={'Critical': '#FF4B4B', 'High': '#FFAA00', '3 - Medium (P3)': '#00CC96'})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.divider()

        # --- Duration / Aging Overview ---
        st.subheader("⏳ Aging Report (Longest Running Active Items)")
        # Show only Pending/In Progress items, sorted by longest duration
        active_df = df[df['Status'] != 'Done'].sort_values(by='Days_Total', ascending=False).head(5)
        
        if not active_df.empty:
            fig_dur = px.bar(active_df, 
                            x='Days_Total', 
                            y='Item', 
                            orientation='h',
                            text='Duration',
                            template="plotly_dark",
                            color='Days_Total',
                            color_continuous_scale='Reds')
            fig_dur.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.success("All items are Done! No aging tickets.")

    except Exception as e:
        st.error(f"Make sure your Excel sheet is named 'Sheet1'. Error: {e}")
else:
    st.info("Awaiting file upload. Please select your IT Tracker Excel file.")
