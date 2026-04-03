import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="IT Executive Summary", layout="wide")

st.title("🚀 IT Tracking: Executive Summary")

uploaded_file = st.file_uploader("Upload 'Track with IT.xlsx'", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        
        # Clean column names
        df.columns = df.columns.str.strip()

        # 2. Forward Fill parent data into sub-category rows
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Data Cleaning
        df_clean = df.dropna(subset=['Category']).copy()

        # Parse Duration into Weeks
        def extract_weeks(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: 
                return 0
            weeks_match = re.search(r'(\d+)\s*week', str(text))
            return int(weeks_match.group(1)) if weeks_match else 0

        df_clean['Weeks_Open'] = df_clean['Duration'].apply(extract_weeks)

        # --- KPI ROW ---
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Total Unique Categories
        total_unique = df_clean['Category'].nunique()
        kpi1.metric("Total Unique Categories", total_unique)
        
        # Total Sub-Category Counts (Counting rows where Sub-Category is not empty/hyphen)
        sub_cat_count = len(df_clean[~df_clean['Sub-Category'].isin(['-', None, 'nan'])])
        kpi2.metric("Total Sub-Category Counts", sub_cat_count)

        # Avg Weeks
        avg_weeks = int(df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()) if not df_clean.empty else 0
        kpi3.metric("Avg. Project Age", f"{avg_weeks} Weeks")

        st.markdown("---")

        # --- DISTRIBUTION CHARTS (Status, Domain, Severity, Type) ---
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            st.subheader("📊 Status Overview")
            # UPDATED COLORS: Open = Orange, Closed = Green
            status_colors = {'Open': '#FFA500', 'Closed': '#228B22'}
            fig_status = px.pie(df_clean, names='Status', hole=0.4,
                               color='Status',
                               color_discrete_map=status_colors)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col2:
            st.subheader("⚠️ Severity Breakdown")
            sev_colors = {'Critical': '#D62728', 'High': '#FF7F0E', 'Medium': '#F4D03F', 'Low': '#2CA02C'}
            fig_sev = px.bar(df_clean['Severity'].value_counts().reset_index(), 
                             x='Severity', y='count', color='Severity',
                             color_discrete_map=sev_colors)
            st.plotly_chart(fig_sev, use_container_width=True)

        with col3:
            st.subheader("🏢 Domain Distribution")
            dom_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.pie(dom_counts, names='Domain', values='Category', hole=0.4)
            st.plotly_chart(fig_dom, use_container_width=True)

        with col4:
            st.subheader("🔧 Type Analysis")
            type_counts = df_clean.groupby('Type')['Category'].nunique().reset_index()
            fig_type = px.bar(type_counts, x='Type', y='Category', color='Type')
            st.plotly_chart(fig_type, use_container_width=True)

        st.markdown("---")

        # ==============================================================
        # 4. RUNNING CATEGORIES (AGING REPORT) - ALL CATEGORIES
        # ==============================================================
        st.subheader("⏳ Running Categories (Aging Report) - All Items")
        
        # Aggregate max weeks per category
        cat_aging = df_clean.groupby(['Category', 'Domain', 'Severity'])['Weeks_Open'].max().reset_index()
        
        # REMOVE 0 WEEKS
        cat_aging = cat_aging[cat_aging['Weeks_Open'] > 0]
        cat_aging = cat_aging.sort_values(by='Weeks_Open', ascending=True)
        
        # Dynamic height for the bar chart
        dynamic_height = 400 + (len(cat_aging) * 25)

        fig_aging = px.bar(cat_aging, 
                          x='Weeks_Open', 
                          y='Category', 
                          orientation='h',
                          color='Severity',
                          text='Weeks_Open',
                          height=dynamic_height,
                          color_discrete_map=sev_colors,
                          labels={'Weeks_Open': 'Weeks', 'Category': 'Category'})
        
        fig_aging.update_traces(texttemplate='%{text} wks', textposition='outside')
        st.plotly_chart(fig_aging, use_container_width=True)

        # --- DATA LIST ---
        with st.expander("🔍 Detailed View (Status, Domain, Type, Duration, Severity)"):
            display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration', 'Severity']
            st.dataframe(df_clean[display_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload the 'Track with IT.xlsx' file.")
