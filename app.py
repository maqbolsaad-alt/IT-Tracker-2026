import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

st.title("🚀 IT Tracking: Executive Summary")

uploaded_file = st.file_uploader("Upload 'Track with IT.xlsx'", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        
        # Clean column names (removes trailing spaces like 'Category ')
        df.columns = df.columns.str.strip()

        # 2. Forward Fill: Link sub-categories to their parent data
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Duration']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Data Cleaning
        df_clean = df.dropna(subset=['Category']).copy()

        # --- PARSING WEEKS ---
        # Extracts just the number of weeks from "X weeks Y days"
        def extract_weeks(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: 
                return 0
            weeks_match = re.search(r'(\d+)\s*week', str(text))
            return int(weeks_match.group(1)) if weeks_match else 0

        df_clean['Weeks_Open'] = df_clean['Duration'].apply(extract_weeks)

        # --- KPI ROW ---
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Count of Unique Categories (Deduplicated)
        total_unique = df_clean['Category'].nunique()
        kpi1.metric("Total Unique Categories", total_unique)
        
        # Count of actual Sub-Categories (Excluding '-' or empty)
        sub_cat_count = len(df_clean[~df_clean['Sub-Category'].isin(['-', None, 'nan'])])
        kpi2.metric("Total Sub-Category Counts", sub_cat_count)

        # Average Age in Weeks
        avg_weeks = int(df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()) if not df_clean.empty else 0
        kpi3.metric("Avg. Cycle Time (Weeks)", f"{avg_weeks} Weeks")

        st.markdown("---")

        # --- DISTRIBUTION CHARTS (Status, Domain, Type) ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Status")
            fig_status = px.pie(df_clean, names='Status', hole=0.4, 
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col2:
            st.subheader("🏢 Domain")
            # Unique categories per domain
            dom_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.bar(dom_counts, x='Domain', y='Category', color='Domain', 
                             labels={'Category': 'Unique Categories'})
            st.plotly_chart(fig_dom, use_container_width=True)

        with col3:
            st.subheader("🔧 Type")
            # Unique categories per type
            type_counts = df_clean.groupby('Type')['Category'].nunique().reset_index()
            fig_type = px.pie(type_counts, names='Type', values='Category', hole=0.4)
            st.plotly_chart(fig_type, use_container_width=True)

        st.markdown("---")

        # ==============================================================
        # 4. RUNNING CATEGORIES (AGING REPORT) - BY WEEKS
        # ==============================================================
        st.subheader("⏳ Running Categories (Aging Report) - All Items")
        
        # Group by Category and get the max weeks
        cat_aging = df_clean.groupby(['Category', 'Domain'])['Weeks_Open'].max().reset_index()
        
        # FILTER: Remove when it's zero weeks
        cat_aging = cat_aging[cat_aging['Weeks_Open'] > 0]
        
        # Sort and Display
        cat_aging = cat_aging.sort_values(by='Weeks_Open', ascending=True)
        
        # Dynamic height for large lists
        dynamic_height = 400 + (len(cat_aging) * 20)

        fig_aging = px.bar(cat_aging, 
                          x='Weeks_Open', 
                          y='Category', 
                          orientation='h',
                          color='Domain',
                          text='Weeks_Open',
                          height=dynamic_height,
                          labels={'Weeks_Open': 'Weeks Open', 'Category': 'Category'},
                          title="All Running Categories (Filtered: > 0 Weeks)")
        
        fig_aging.update_traces(texttemplate='%{text} Weeks', textposition='outside')
        st.plotly_chart(fig_aging, use_container_width=True)

        # --- DATA LIST ---
        with st.expander("🔍 View All Project Details (Status, Domain, Type, Duration)"):
            display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration']
            st.dataframe(df_clean[display_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👆 Please upload the 'Track with IT.xlsx' file to view the updated report.")
