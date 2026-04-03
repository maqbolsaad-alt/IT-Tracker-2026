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
        df.columns = df.columns.str.strip()

        # 2. Forward Fill to link Sub-Categories to their Parent info
        # We focus on the requested fields: Domain, Type, Category, Status, Duration
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Data Cleaning
        df_clean = df.dropna(subset=['Category']).copy()

        # Parse Duration into Days
        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            return (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)

        # --- KPI ROW ---
        kpi1, kpi2 = st.columns(2)
        
        # Total Tasks = Unique Categories (Deduplicated)
        total_unique_categories = df_clean['Category'].nunique()
        kpi1.metric("Total Unique Projects/Categories", total_unique_categories)
        
        # Average Age across all items
        avg_age = int(df_clean[df_clean['Days_Open'] > 0]['Days_Open'].mean()) if not df_clean.empty else 0
        kpi2.metric("Average Cycle Time (Days)", avg_age)

        st.markdown("---")

        # --- DISTRIBUTION CHARTS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Status Overview")
            fig_status = px.pie(df_clean, names='Status', hole=0.5, 
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col2:
            st.subheader("🏢 Domain Distribution")
            # Count unique categories per domain
            domain_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.bar(domain_counts, x='Domain', y='Category', 
                             labels={'Category': 'Unique Projects'},
                             color='Domain', color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_dom, use_container_width=True)

        st.markdown("---")

        # --- AGING REPORT (TOP 10 CATEGORIES) ---
        # "Make it for all" - shows top 10 durations regardless of Status
        st.subheader("⏳ Top 10 Longest Running Categories (Aging Report)")
        
        cat_aging = df_clean.groupby(['Category', 'Domain', 'Type'])['Days_Open'].max().reset_index()
        cat_aging = cat_aging.sort_values(by='Days_Open', ascending=False).head(10)
        
        fig_aging = px.bar(cat_aging, 
                          x='Days_Open', 
                          y='Category', 
                          orientation='h',
                          color='Domain',
                          text='Days_Open',
                          labels={'Days_Open': 'Days', 'Category': 'Category'})
        
        fig_aging.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_aging.update_traces(texttemplate='%{text} Days', textposition='outside')
        st.plotly_chart(fig_aging, use_container_width=True)

        # --- SIMPLIFIED DATA TABLE ---
        with st.expander("🔍 View Simplified Data List"):
            # Only include the 4 requested columns + Category for context
            display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration']
            available_cols = [c for c in display_cols if c in df_clean.columns]
            st.dataframe(df_clean[available_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload the Excel file to view the simplified dashboard.")
