import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Page config
st.set_page_config(page_title="Executive IT Dashboard", layout="wide")

st.title("🚀 Executive IT Tracking Overview")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Load Data
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # 2. Forward Fill parent data into sub-category rows
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Severity', 'Duration']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Clean and Parse
        df_clean = df.dropna(subset=['Status']).copy()

        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)

        # --- FILTERS ---
        st.sidebar.header("Filter Options")
        selected_domain = st.sidebar.multiselect("Select Domain", options=df_clean['Domain'].unique(), default=df_clean['Domain'].unique())
        
        df_filtered = df_clean[df_clean['Domain'].isin(selected_domain)]

        # --- KPI ROW ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Tasks", len(df_filtered))
        kpi1.caption(f"Across {df_filtered['Category'].nunique()} Categories")
        
        crit_count = len(df_filtered[df_filtered['Severity'].str.contains('Critical', case=False, na=False)])
        kpi2.metric("Critical Issues", crit_count)
        
        avg_age = int(df_filtered[df_filtered['Days_Open'] > 0]['Days_Open'].mean()) if not df_filtered.empty else 0
        kpi3.metric("Avg. Age (Days)", avg_age)
        kpi4.metric("Oldest Project", f"{df_filtered['Days_Open'].max()} Days")

        st.markdown("---")

        # --- CHART ROW 1 ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏢 Projects by Domain")
            # Grouping by Category to see unique projects per domain
            dom_dist = df_filtered.groupby('Domain')['Category'].nunique().reset_index()
            fig_dom = px.pie(dom_dist, values='Category', names='Domain', hole=0.5, title="Unique Categories per Domain")
            st.plotly_chart(fig_dom, use_container_width=True)
        
        with c2:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(df_filtered, names='Status', hole=0.5)
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")

        # ==============================================================
        # 4. AGING REPORT BY CATEGORY (Top 10)
        # We group by Category so that sub-tasks are combined into one bar
        # ==============================================================
        st.subheader("⏳ Top 10 Longest Running Categories (Aging Report)")
        
        # Filter for Open items
        open_items = df_filtered[~df_filtered['Status'].str.contains('Closed|Done', case=False, na=False)]
        
        # Group by Category and get the max days open (and keep Domain for coloring)
        cat_aging = open_items.groupby(['Category', 'Domain', 'Type'])['Days_Open'].max().reset_index()
        cat_aging = cat_aging.sort_values(by='Days_Open', ascending=False).head(10)
        
        fig_duration = px.bar(cat_aging, 
                             x='Days_Open', 
                             y='Category', 
                             orientation='h',
                             color='Domain',
                             text='Days_Open',
                             labels={'Days_Open': 'Total Days Open', 'Category': 'Project Category'},
                             color_discrete_sequence=px.colors.qualitative.Vivid)
        
        fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_duration.update_traces(texttemplate='%{text} days', textposition='outside')
        
        st.plotly_chart(fig_duration, use_container_width=True)

        # Full Data List
        with st.expander("🔍 View Detailed Task Breakdown"):
            st.dataframe(df_filtered.drop(columns=['Days_Open'], errors='ignore'), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Please upload your 'Track with IT.xlsx' file.")
