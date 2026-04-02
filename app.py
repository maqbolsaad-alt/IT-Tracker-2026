import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Page Configuration
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

# 2. Force Dark Mode Styling (Fixed the typo here)
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
        
        # Calculate Average Age
        active_items = df[df['Days_Total'] > 0]
        avg_days = int(active_items['Days_Total'].mean()) if not active_items.empty else 0
        m4.metric("Avg. Age (Days)", avg_days)

        st.divider()

        # --- Charts Row ---
        left, right = st.columns(2)

        with left:
            st.subheader("📋 Status (Donut)")
            fig_status = px.pie(df, names='Status', hole=0.6, 
                               template="plotly_dark",
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)

        with right:
            st.subheader("⚠️ Severity Breakdown")
            # Creating bar chart for Severity
            sev_counts = df['Severity'].value_counts().reset_index()
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                            color='Severity',
                            template="plotly_dark",
                            color_discrete_map={'Critical': '#FF4B4B', 'High': '#FFAA00', 'Medium': '#00CC96'})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.divider()

        # --- Aging Tickets Overview ---
        st.subheader("⏳ Aging Report (Longest Running Active Items)")
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
            st.success("No active pending items found!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Awaiting file upload. Please select your IT Tracker Excel file.")
