import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IT Tracking Dashboard", layout="wide")

st.title("📊 Enhanced IT Tracking Dashboard")
st.markdown("Upload your Excel file to see updated Status and Duration metrics.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read the file
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()

        # --- Metrics Row ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Items", len(df))
        col2.metric("Critical Items", len(df[df['Severity'] == 'Critical']))
        col3.metric("Pending", len(df[df['Status'] == 'Pending']))
        col4.metric("In Progress", len(df[df['Status'] == 'In Progress']))

        st.divider()

        # --- Charts Row ---
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.subheader("Status Distribution")
            fig_status = px.pie(df, names='Status', hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)

        with right_col:
            st.subheader("Duration: Top 5 Longest Items")
            # This shows the items that have been open the longest based on your 'Duration' column
            if 'Duration' in df.columns:
                # We sort by the duration text (or you can view the top 5 rows)
                duration_df = df[['Number', 'Item', 'Duration', 'Status']].dropna().head(5)
                st.table(duration_df)
            else:
                st.warning("No 'Duration' column found in Excel.")

        # --- Detailed Table ---
        st.subheader("Full Data View")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Waiting for Excel upload...")
