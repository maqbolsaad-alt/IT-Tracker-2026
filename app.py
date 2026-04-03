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

        # 2. THE FIX: Forward Fill (ffill) 
        # This "finds" the Domain, Type, and Status for sub-categories by 
        # dragging the values down from the parent row above.
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Severity', 'Duration']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Filter out empty rows at the bottom
        df_clean = df.dropna(subset=['Status']).copy()

        # 4. Parse Duration to Days
        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)
        
        # Create clear Item Name
        df_clean['Item'] = df_clean.apply(lambda x: str(x['Sub-Category']).strip() if str(x['Sub-Category']).strip() not in ["-", "nan", ""] else str(x['Category']).strip(), axis=1)

        # 5. SIDEBAR FILTERS (Making Domain and Type visible)
        st.sidebar.header("Filter Options")
        selected_domain = st.sidebar.multiselect("Select Domain", options=df_clean['Domain'].unique(), default=df_clean['Domain'].unique())
        selected_type = st.sidebar.multiselect("Select Type", options=df_clean['Type'].unique(), default=df_clean['Type'].unique())

        # Apply filters
        mask = (df_clean['Domain'].isin(selected_domain)) & (df_clean['Type'].isin(selected_type))
        df_filtered = df_clean[mask]

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(df_filtered))
        kpi2.metric("Critical Issues", len(df_filtered[df_filtered['Severity'].str.contains('Critical', case=False, na=False)]))
        avg_age = int(df_filtered[df_filtered['Days_Open'] > 0]['Days_Open'].mean()) if not df_filtered.empty else 0
        kpi3.metric("Avg. Age (Days)", avg_age)
        kpi4.metric("Oldest Ticket (Days)", df_filtered['Days_Open'].max() if not df_filtered.empty else 0)

        st.markdown("---")

        # --- CHARTS ROW 1 ---
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📋 Status")
            fig_status = px.pie(df_filtered, names='Status', hole=0.5)
            st.plotly_chart(fig_status, use_container_width=True)

        with col2:
            st.subheader("⚠️ Severity")
            fig_sev = px.bar(df_filtered['Severity'].value_counts().reset_index(), x='Severity', y='count', color='Severity')
            st.plotly_chart(fig_sev, use_container_width=True)

        with col3:
            st.subheader("🏢 Tasks by Domain")
            # This directly addresses "where is domain"
            fig_dom = px.pie(df_filtered, names='Domain', hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_dom, use_container_width=True)

        st.markdown("---")

        # --- AGING REPORT (TOP 10) ---
        st.subheader("⏳ Top 10 Longest Running Items (Aging Report)")
        aging_df = df_filtered[~df_filtered['Status'].str.contains('Closed|Done', case=False, na=False)].sort_values(by='Days_Open', ascending=False).head(10)
        
        fig_duration = px.bar(aging_df, 
                             x='Days_Open', 
                             y='Item', 
                             orientation='h',
                             text='Duration',
                             color='Domain', # Colors bars by Domain for better visibility
                             labels={'Days_Open': 'Days Open', 'Item': 'Task Name'})
        fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_duration, use_container_width=True)

        # Full Data List
        with st.expander("See All Project Details"):
            st.dataframe(df_filtered.drop(columns=['Days_Open'], errors='ignore'), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Please upload the 'Track with IT.xlsx' file.")
