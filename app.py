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
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- DATA PROCESSING FOR DURATION ---
        # We convert "X weeks Y days" into a number so we can make a chart
        def parse_duration(text):
            if pd.isna(text) or text == "": return 0
            weeks = re.search(r'(\d+)\s*week', str(text))
            days = re.search(r'(\d+)\s*day', str(text))
            total_days = (int(weeks.group(1)) * 7 if weeks else 0) + (int(days.group(1)) if days else 0)
            return total_days

        df['Days_Open'] = df['Duration'].apply(parse_duration)

        # --- TOP LEVEL KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Items", len(df))
        kpi2.metric("Critical Issues", len(df[df['Severity'] == 'Critical']))
        kpi3.metric("Avg. Age (Days)", int(df[df['Days_Open'] > 0]['Days_Open'].mean()))
        kpi4.metric("Oldest Ticket (Days)", df['Days_Open'].max())

        st.markdown("---")

        # --- CHARTS ROW ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📋 Status Distribution")
            # Donut Chart for Status
            fig_status = px.pie(df, names='Status', hole=0.6, 
                               color_discrete_sequence=px.colors.qualitative.Safe)
            fig_status.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

        with col_right:
            st.subheader("⚠️ Severity Breakdown")
            # Bar Chart for Severity
            sev_counts = df['Severity'].value_counts().reset_index()
            fig_sev = px.bar(sev_counts, x='Severity', y='count', 
                            color='Severity',
                            color_discrete_map={'Critical': '#EF553B', 'High': '#FFA15A', '3 - Medium (P3)': '#FECB52'})
            st.plotly_chart(fig_sev, use_container_width=True)

        st.markdown("---")

        # --- THE "EXCITING" DURATION OVERVIEW ---
        st.subheader("⏳ Top 5 Longest Running Items (Aging Report)")
        # Sort by Days_Open and take top 5
        aging_df = df[df['Status'] != 'Done'].sort_values(by='Days_Open', ascending=False).head(5)
        
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
            st.dataframe(df.drop(columns=['Days_Open']), use_container_width=True)

    except Exception as e:
        st.error(f"Make sure your Excel sheet is named 'Sheet1'. Error: {e}")
else:
    st.info("👆 Please upload the 'Track with IT.xlsx' file to generate the executive overview.")
