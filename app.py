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

            # --- ROW 1: SYSTEM & STATUS ---
            col_sys, col_stat = st.columns(2)

            with col_sys:
                st.subheader("🖥️ Workload by System")
                sys_counts = filtered_df['System'].value_counts().reset_index()
                fig_sys = px.bar(sys_counts, x='System', y='count', 
                                 color='System', text_auto=True,
                                 color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_sys, use_container_width=True)

            with col_stat:
                st.subheader("📋 Status Distribution")
                fig_status = px.pie(filtered_df, names='Status', hole=0.5, 
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
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
                                color_discrete_map={'Critical': '#D62728', 'High': '#FF7F0E', '3 - Medium (P3)': '#FFBB78'})
                st.plotly_chart(fig_sev, use_container_width=True)

            with col_age:
                st.subheader("⏳ Top 5 Aging Items")
                # Filter out 'Done' items for aging report
                aging_df = filtered_df[~filtered_df['Status'].str.contains('Done', case=False, na=False)]
                aging_df = aging_df.sort_values(by='Days_Open', ascending=False).head(5)
                
                fig_duration = px.bar(aging_df, 
                                     x='Days_Open', 
                                     y='Item', 
                                     orientation='h',
                                     text='System',
                                     color='Days_Open',
                                     color_continuous_scale='Reds')
                fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_duration, use_container_width=True)

            # Full Data List
            with st.expander("🔍 View Raw Filtered Data"):
                st.dataframe(filtered_df.drop(columns=['Days_Open']), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Please upload the Excel file to begin.")
