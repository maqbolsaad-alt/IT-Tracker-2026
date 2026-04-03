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
        # Read the sheet and strip column whitespace
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- DATA CLEANING ---
        # Only keep rows that have a Status (filters out the empty sub-category rows for KPIs)
        df_clean = df.dropna(subset=['Status']).copy()

        # Create an 'Item' column for the charts (Fallback: Category if Sub-Category is '-')
        def identify_item(row):
            cat = str(row['Category']).strip() if 'Category' in df.columns else "Unknown"
            sub = str(row['Sub-Category']).strip() if 'Sub-Category' in df.columns else "-"
            return cat if (sub == "-" or sub == "nan") else sub

        df_clean['Item'] = df_clean.apply(identify_item, axis=1)

        # --- DURATION PARSING ---
        def parse_duration(text):
            if pd.isna(text) or str(text).strip() in ["", "-"]: return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df_clean['Days_Open'] = df_clean['Duration'].apply(parse_duration)

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(df_clean))
        
        # Count critical (handling potential case sensitivity)
        crit_count = len(df_clean[df_clean['Severity'].str.contains('Critical', case=False, na=False)])
        kpi2.metric("Critical Issues", crit_count)
        
        avg_days = int(df_clean[df_clean['Days_Open'] > 0]['Days_Open'].mean()) if not df_clean.empty else 0
        kpi3.metric("Avg. Age (Days)", avg_days)
        kpi4.metric("Oldest Ticket (Days)", df_clean['Days_Open'].max())

        st.markdown("---")

        # --- CHARTS ROW ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📋 Status Distribution")
            fig_status = px.pie(df_clean, names='Status', hole=0.6, 
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_status.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

        with col_right:
            st.subheader("⚠️ Severity Breakdown")
            sev_counts = df_clean['Severity'].value_counts().reset_index()
            sev_counts.columns = ['Severity', 'count']
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                            color='Severity',
                            color_discrete_map={'Critical': '#EF553B', 'High': '#FFA15A', 'Medium': '#FECB52'})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.markdown("---")

        # --- AGING REPORT ---
        st.subheader("⏳ Top 5 Longest Running Items (Aging Report)")
        # Filter for open items and sort
        aging_df = df_clean[~df_clean['Status'].isin(['Closed', 'Done'])].sort_values(by='Days_Open', ascending=False).head(5)
        
        fig_duration = px.bar(aging_df, 
                             x='Days_Open', 
                             y='Item', 
                             orientation='h',
                             text='Duration',
                             labels={'Days_Open': 'Days Open', 'Item': 'Task Name'},
                             color='Days_Open',
                             color_continuous_scale='Reds')
        fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_duration, use_container_width=True)

        # Full Data List
        with st.expander("See All Project Details"):
            st.dataframe(df.style.highlight_null(color='#f0f0f0'), use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👆 Please upload the 'Track with IT.xlsx' file to generate the overview.")
