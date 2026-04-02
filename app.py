import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

# Custom CSS for a more "Executive" feel
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
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
        
        # Ensure 'System' exists to avoid errors
        if 'System' not in df.columns:
            df['System'] = "Uncategorized"

        # --- SIDEBAR FILTERS ---
        st.sidebar.header("Global Filters")
        selected_systems = st.sidebar.multiselect(
            "Filter by System", 
            options=df['System'].unique(), 
            default=df['System'].unique()
        )
        
        # Apply filtering
        filtered_df = df[df['System'].isin(selected_systems)]

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(filtered_df))
        kpi2.metric("Critical Issues", len(filtered_df[filtered_df['Severity'].str.contains('Critical', na=False)]))
        kpi3.metric("Avg. Age (Days)", int(filtered_df[filtered_df['Days_Open'] > 0]['Days_Open'].mean()) if not filtered_df.empty else 0)
        kpi4.metric("Active Systems", filtered_df['System'].nunique())

        st.markdown("---")

        # --- ROW 1: SYSTEM & STATUS ---
        col_sys, col_stat = st.columns(2)

        with col_sys:
            st.subheader("🖥️ Items by System")
            # Bar chart showing which systems have the most tickets
            sys_counts = filtered_df['System'].value_counts().reset_index()
            fig_sys = px.bar(sys_counts, x='System', y='count', 
                             color='System', text_auto=True,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_sys, use_container_width=True)

        with col_stat:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(filtered_df, names='Status', hole=0.6, 
                                color_discrete_sequence=px.colors.qualitative.Safe)
            fig_status.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")

        # --- ROW 2: SEVERITY & AGING ---
        col_sev, col_age = st.columns([1, 2])

        with col_sev:
            st.subheader("⚠️ Severity Breakdown")
            sev_counts = filtered_df['Severity'].value_counts().reset_index()
            fig_sev = px.bar(sev_counts, y='Severity', x='count', 
                            orientation='h', color='Severity',
                            color_discrete_map={'Critical': '#EF553B', 'High': '#FFA15A', '3 - Medium (P3)': '#FECB52'})
            st.plotly_chart(fig_sev, use_container_width=True)

        with col_age:
            st.subheader("⏳ Top 5 Longest Running Items")
            # Filter out done items to show what's actually pending
            aging_df = filtered_df[filtered_df['Status'] != 'Done'].sort_values(by='Days_Open', ascending=False).head(5)
            
            fig_duration = px.bar(aging_df, 
                                 x='Days_Open', 
                                 y='Item', 
                                 orientation='h',
                                 text='System', # Show which system it belongs to on the bar
                                 labels={'Days_Open': 'Days Open', 'Item': 'Task Name'},
                                 color='Days_Open',
                                 color_continuous_scale='Reds')
            fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_duration, use_container_width=True)

        # Full Data List
        with st.expander("🔍 Explore Full Dataset"):
            st.dataframe(filtered_df.drop(columns=['Days_Open']), use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.info("Check if your columns ('System', 'Status', 'Severity', 'Duration', 'Item') are named correctly.")
else:
    st.info("👆 Please upload the 'Track with IT.xlsx' file to generate the dashboard.")
