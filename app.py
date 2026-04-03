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

        # 2. Forward Fill parent data into sub-category rows
        # Focus columns: Domain, Type, Category, Status, Duration
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Duration']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Data Cleaning
        df_clean = df.dropna(subset=['Category']).copy()

        # Parse Duration into Days for mathematical sorting
        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            return (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)

        # --- KPI ROW ---
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Total Tasks = Unique Categories (De-duplicated)
        total_unique = df_clean['Category'].nunique()
        kpi1.metric("Total Unique Categories", total_unique)
        
        # Average Age across all items
        avg_age = int(df_clean[df_clean['Days_Open'] > 0]['Days_Open'].mean()) if not df_clean.empty else 0
        kpi2.metric("Avg. Project Age (Days)", avg_age)

        # Task Count by Type (Summary)
        most_common_type = df_clean['Type'].mode()[0] if not df_clean.empty else "N/A"
        kpi3.metric("Primary Type", most_common_type)

        st.markdown("---")

        # --- DISTRIBUTION CHARTS (Status, Domain, Type) ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Status")
            fig_status = px.pie(df_clean, names='Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col2:
            st.subheader("🏢 Domain")
            dom_counts = df_clean.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.bar(dom_counts, x='Domain', y='Category', color='Domain', labels={'Category': 'Count'})
            st.plotly_chart(fig_dom, use_container_width=True)

        with col3:
            st.subheader("🔧 Type")
            type_counts = df_clean.groupby('Type')['Category'].nunique().reset_index()
            fig_type = px.pie(type_counts, names='Type', values='Category', hole=0.4)
            st.plotly_chart(fig_type, use_container_width=True)

        st.markdown("---")

        # ==============================================================
        # 4. RUNNING CATEGORIES (AGING REPORT) - ALL CATEGORIES
        # ==============================================================
        st.subheader("⏳ Running Categories (Aging Report) - All Items")
        
        # Group by Category and get the max days open
        # We include Domain and Type so they show up in the hover/color
        cat_aging = df_clean.groupby(['Category', 'Domain', 'Type'])['Days_Open'].max().reset_index()
        cat_aging = cat_aging.sort_values(by='Days_Open', ascending=False)
        
        # Adjust height based on number of categories so it doesn't look squashed
        chart_height = 400 + (len(cat_aging) * 20) 

        fig_aging = px.bar(cat_aging, 
                          x='Days_Open', 
                          y='Category', 
                          orientation='h',
                          color='Domain',
                          text='Days_Open',
                          height=chart_height,
                          labels={'Days_Open': 'Days', 'Category': 'Category'},
                          title="Full Aging List by Category")
        
        fig_aging.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_aging.update_traces(texttemplate='%{text} d', textposition='outside')
        st.plotly_chart(fig_aging, use_container_width=True)

        # --- DATA LIST ---
        with st.expander("🔍 Detailed Data Table (Status, Domain, Type, Duration)"):
            display_cols = ['Category', 'Status', 'Domain', 'Type', 'Duration']
            # Only showing unique combinations of Category + Status
            st.dataframe(df_clean[display_cols].drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    st.info("Please upload the 'Track with IT.xlsx' file.")
