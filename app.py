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
        # Load data
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df.columns = df.columns.str.strip()

        # Handle 'System' column logic
        if 'System' not in df.columns:
            st.warning("⚠️ 'System' column not found. Creating a default 'General' category.")
            df['System'] = "General"
        df['System'] = df['System'].fillna("Uncategorized")

        # Process Duration
        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- SIDEBAR FILTERS ---
        st.sidebar.header("Global Filters")
        all_systems = df['System'].unique().tolist()
        selected_systems = st.sidebar.multiselect("Filter by System", all_systems, default=all_systems)

        # Apply filtering
        filtered_df = df[df['System'].isin(selected_systems)]

        # --- KPI ROW ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Items (Filtered)", len(filtered_df))
        
        crit_count = len(filtered_df[filtered_df['Severity'].str.contains('Critical', case=False, na=False)])
        kpi2.metric("Critical Issues", crit_count)
        
        avg_age = int(filtered_df[filtered_df['Days_Open'] > 0]['Days_Open'].mean()) if not filtered_df.empty else 0
        kpi3.metric("Avg. Age (Days)", avg_age)
        
        max_age = filtered_df['Days_Open'].max() if not filtered_df.empty else 0
        kpi4.metric("Oldest Ticket", f"{max_age} Days")

        st.divider()

        # --- VISUALIZATION ROW ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("🖥️ Items by System")
            # A Treemap is great for seeing System importance at a glance
            fig_sys = px.treemap(filtered_df, path=['System', 'Status'], 
                                 color='System',
                                 color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_sys, use_container_width=True)

        with col_right:
            st.subheader("⚠️ Severity by System")
            # Stacked bar chart to see which system has the most critical issues
            fig_sev = px.bar(filtered_df, x='System', color='Severity',
                             color_discrete_map={'Critical': '#EF553B', 'High': '#FFA15A', 'Medium': '#FECB52'},
                             category_orders={"Severity": ["Critical", "High", "Medium", "Low"]})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.divider()

        # --- AGING REPORT BY SYSTEM ---
        st.subheader("⏳ Top Longest Running Items (Color coded by System)")
        aging_df = filtered_df[filtered_df['Status'] != 'Done'].sort_values(by='Days_Open', ascending=False).head(10)
        
        if not aging_df.empty:
            fig_aging = px.bar(aging_df, 
                               x='Days_Open', 
                               y='Item', 
                               orientation='h',
                               color='System',
                               text='Duration',
                               hover_data=['System', 'Severity', 'Status'])
            fig_aging.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_aging, use_container_width=True)
        else:
            st.success("No open items to display for selected systems!")

        # Detailed View
        with st.expander("📄 Detailed Task List"):
            st.dataframe(filtered_df.drop(columns=['Days_Open']), use_container_width=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.info("Please upload the file to view
