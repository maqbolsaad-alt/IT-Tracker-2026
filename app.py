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

        # 2. Forward Fill: Drags Domain, Type, Severity, and Duration into sub-category rows
        # Added 'Severity' explicitly to ensure it is not missed
        cols_to_fill = ['Domain', 'Type', 'Category', 'Status', 'Severity', 'Duration']
        cols_to_fill = [c for c in cols_to_fill if c in df.columns]
        df[cols_to_fill] = df[cols_to_fill].ffill()

        # 3. Clean and Parse
        df_clean = df.dropna(subset=['Status']).copy()
        df_clean['Severity'] = df_clean['Severity'].str.strip()

        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            return (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)

        # --- SIDEBAR FILTERS ---
        st.sidebar.header("Global Filters")
        sel_domain = st.sidebar.multiselect("Domain", df_clean['Domain'].unique(), df_clean['Domain'].unique())
        sel_sev = st.sidebar.multiselect("Severity", df_clean['Severity'].unique(), df_clean['Severity'].unique())
        
        df_filtered = df_clean[(df_clean['Domain'].isin(sel_domain)) & (df_clean['Severity'].isin(sel_sev))]

        # --- KPI ROW ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Tasks", len(df_filtered))
        
        # Explicit Severity KPI
        crit_count = len(df_filtered[df_filtered['Severity'] == 'Critical'])
        k2.metric("Critical Issues", crit_count, delta_color="inverse")
        
        k3.metric("Avg. Age (Days)", int(df_filtered[df_filtered['Days_Open'] > 0]['Days_Open'].mean()) if not df_filtered.empty else 0)
        k4.metric("Oldest Project", f"{df_filtered['Days_Open'].max()} Days")

        st.markdown("---")

        # --- CHART ROW 1 ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(df_filtered, names='Status', hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_status, use_container_width=True)
        
        with c2:
            st.subheader("⚠️ Severity Breakdown")
            # Explicitly sorting bars by typical priority
            sev_order = ['Critical', 'High', 'Medium', 'Low', '-']
            counts = df_filtered['Severity'].value_counts().reindex(sev_order).dropna().reset_index()
            counts.columns = ['Severity', 'Count']
            fig_sev = px.bar(counts, x='Severity', y='Count', color='Severity',
                             color_discrete_map={'Critical': '#D62728', 'High': '#FF7F0E', 'Medium': '#F4D03F', 'Low': '#2CA02C'})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.markdown("---")

        # ==============================================================
        # 4. AGING REPORT BY CATEGORY (WITH SEVERITY)
        # ==============================================================
        st.subheader("⏳ Top 10 Longest Running Categories (Aging Report)")
        
        # Only show items that are NOT Closed/Done
        open_items = df_filtered[~df_filtered['Status'].str.contains('Closed|Done', case=False, na=False)]
        
        if not open_items.empty:
            # Group by Category: Get the max days and the "worst" severity
            # We sort by severity priority to pick the max one if there's a mix
            open_items['Sev_Rank'] = open_items['Severity'].map({'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1, '-': 0}).fillna(0)
            
            cat_aging = open_items.groupby('Category').agg({
                'Days_Open': 'max',
                'Sev_Rank': 'max',
                'Domain': 'first',
                'Severity': 'first' # This will be the label
            }).reset_index().sort_values(by='Days_Open', ascending=False).head(10)

            # Map the rank back to the label for the legend
            rank_map = {4: 'Critical', 3: 'High', 2: 'Medium', 1: 'Low', 0: '-'}
            cat_aging['Worst Severity'] = cat_aging['Sev_Rank'].map(rank_map)

            fig_duration = px.bar(cat_aging, 
                                 x='Days_Open', 
                                 y='Category', 
                                 orientation='h',
                                 color='Worst Severity', # SEVERITY is now the color
                                 text='Days_Open',
                                 color_discrete_map={'Critical': '#D62728', 'High': '#FF7F0E', 'Medium': '#F4D03F', 'Low': '#2CA02C'},
                                 labels={'Days_Open': 'Days Open', 'Category': 'Project Category', 'Worst Severity': 'Priority'})
            
            fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_duration.update_traces(texttemplate='%{text} days', textposition='outside')
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.success("No open items found!")

        # Full Data List
        with st.expander("🔍 Detailed View (Domain & Type included)"):
            st.dataframe(df_filtered.drop(columns=['Days_Open', 'Sev_Rank'], errors='ignore'), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Please upload 'Track with IT.xlsx' to start.")
