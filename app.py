import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide", page_icon="📊")

st.title("🚀 Executive IT Tracking Overview")

uploaded_file = st.file_uploader("Upload your IT Tracking Excel file", type=["xlsx"])

def parse_duration(text):
    if pd.isna(text) or text == "": return 0
    text = str(text).lower()
    weeks = re.search(r'(\d+)\s*week', text)
    days = re.search(r'(\d+)\s*day', text)
    total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
    return total_days

if uploaded_file:
    try:
        # Load data - Using sheet_name=0 to grab the first sheet regardless of name
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df.columns = df.columns.str.strip()

        # Handle missing 'System' column gracefully
        if 'System' not in df.columns:
            df['System'] = "Unknown"
        df['System'] = df['System'].fillna("Uncategorized")

        # Process Duration
        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- SIDEBAR FILTER ---
        st.sidebar.header("Filter Options")
        selected_systems = st.sidebar.multiselect(
            "Select System(s):",
            options=df['System'].unique(),
            default=df['System'].unique()
        )

        # Apply Filter
        filtered_df = df[df['System'].isin(selected_systems)]

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(filtered_df))
        
        crit_val = len(filtered_df[filtered_df['Severity'].str.contains('Critical', case=False, na=False)])
        kpi2.metric("Critical Issues", crit_val)
        
        avg_age = int(filtered_df[filtered_df['Days_Open'] > 0]['Days_Open'].mean()) if len(filtered_df) > 0 else 0
        kpi3.metric("Avg. Age (Days)", avg_age)
        
        max_age = filtered_df['Days_Open'].max() if len(filtered_df) > 0 else 0
        kpi4.metric("Oldest Ticket (Days)", max_age)

        st.divider()

        # --- MAIN CHARTS ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Status by System")
            # Sunburst chart shows System -> Status relationship
            fig_sys = px.sunburst(filtered_df, path=['System', 'Status'], 
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_sys, use_container_width=True)

        with col2:
            st.subheader("⚠️ Severity Breakdown")
            fig_sev = px.bar(filtered_df, x='Severity', color='System',
                            title="Severity Count per System",
                            barmode='stack')
            st.plotly_chart(fig_sev, use_container_width=True)

        st.divider()

        # --- AGING REPORT ---
        st.subheader("⏳ Top Longest Running Items (Open Only)")
        aging_df = filtered_df[filtered_df['Status'] != 'Done'].sort_values(by='Days_Open', ascending=False).head(8)
        
        if not aging_df.empty:
            fig_duration = px.bar(aging_df, 
                                 x='Days_Open', 
                                 y='Item', 
                                 orientation='h',
                                 color='System', # Color bars by System
                                 text='Duration',
                                 hover_data=['System', 'Severity'])
            fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No open items to display for the selected systems.")

        # Full Data List
        with st.expander("See All Project Details"):
            st.dataframe(filtered_df.drop(columns=['Days_Open']), use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else
