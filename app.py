import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide", page_icon="📊")

# Custom CSS for a more professional feel
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_index=True)

st.title("🚀 Executive IT Tracking Overview")

uploaded_file = st.file_uploader("Upload your IT Tracking Excel file", type=["xlsx"])

def parse_duration(text):
    if pd.isna(text) or text == "": return 0
    # Clean string to lowercase for better matching
    text = str(text).lower()
    weeks = re.search(r'(\d+)\s*week', text)
    days = re.search(r'(\d+)\s*day', text)
    total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
    return total_days

if uploaded_file:
    try:
        # Load data
        df = pd.read_excel(uploaded_file, sheet_name=0) # Index 0 is safer than "Sheet1"
        df.columns = df.columns.str.strip()

        # Check for required columns
        required_cols = ['Status', 'Severity', 'Duration', 'Item']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Missing columns! Ensure file has: {', '.join(required_cols)}")
            st.stop()

        # Data Processing
        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- KPI SECTION ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric("Total Items", len(df))
        with kpi2:
            critical_count = len(df[df['Severity'].str.contains('Critical', case=False, na=False)])
            st.metric("Critical Issues", critical_count, delta_color="inverse")
        with kpi3:
            avg_age = int(df[df['Days_Open'] > 0]['Days_Open'].mean()) if not df.empty else 0
            st.metric("Avg. Age", f"{avg_age} Days")
        with kpi4:
            max_age = df['Days_Open'].max()
            st.metric("Oldest Ticket", f"{max_age} Days")

        st.divider()

        # --- VISUALIZATION SECTION ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(df, names='Status', hole=0.5, 
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)

        with col_right:
            st.subheader("⚠️ Severity Breakdown")
            # Ensure custom colors match your data labels exactly
            fig_sev = px.histogram(df, x='Severity', color='Severity',
                                  color_discrete_map={
                                      'Critical': '#D62728', 
                                      'High': '#FF7F0E', 
                                      'Medium': '#2CA02C'
                                  })
            st.plotly_chart(fig_sev, use_container_width=True)

        # --- AGING REPORT ---
        st.subheader("⏳ Top 5 Longest Running Items")
        aging_df = df[df['Status'] != 'Done'].sort_values(by='Days_Open', ascending=False).head(5)
        
        if not aging_df.empty:
            fig_duration = px.bar(aging_df, 
                                 x='Days_Open', 
                                 y='Item', 
                                 orientation='h',
                                 text='Duration',
                                 color='Days_Open',
                                 color_continuous_scale='OrRd')
            fig_duration.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.success("No open items found! Everyone is on vacation. 🎉")

        # Full Data View
        with st.expander("🔍 View Raw Dataset"):
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    st.info("Please upload an Excel file to see the analysis.")
