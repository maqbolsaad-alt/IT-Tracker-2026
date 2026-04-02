import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the page configuration
st.set_page_config(page_title="IT Tracking Dashboard", page_icon="📊", layout="wide")

st.title("📊 IT Tracking Dashboard")
st.markdown("Upload your updated **Track with IT.xlsx** file to view the latest dashboard metrics.")

# File uploader for the frequently updated excel file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Load the first sheet of the uploaded Excel file
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        
        # Clean up column names
        df.columns = df.columns.str.strip()
        
        # --- Top Level KPIs ---
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_tickets = len(df)
        pending_tickets = len(df[df['Status'] == 'Pending'])
        in_progress_tickets = len(df[df['Status'] == 'In Progress'])
        done_tickets = len(df[df['Status'] == 'Done'])
        
        col1.metric("Total Items", total_tickets)
        col2.metric("Pending", pending_tickets)
        col3.metric("In Progress", in_progress_tickets)
        col4.metric("Done", done_tickets)
        
        st.divider()

        # --- Dashboard Charts ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### Items by Status")
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.pie(status_counts, values='Count', names='Status', hole=0.4, 
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col_chart2:
            st.markdown("#### Items by Severity")
            sev_counts = df['Severity'].value_counts().reset_index()
            sev_counts.columns = ['Severity', 'Count']
            fig_sev = px.bar(sev_counts, x='Severity', y='Count', text='Count',
                             color='Severity', color_discrete_sequence=px.colors.qualitative.Set2)
            fig_sev.update_traces(textposition='outside')
            st.plotly_chart(fig_sev, use_container_width=True)
            
        st.markdown("#### Detailed Data View")
        # Let the user filter by status in the data table
        status_filter = st.multiselect("Filter by Status:", options=df['Status'].dropna().unique(), default=df['Status'].dropna().unique())
        filtered_df = df[df['Status'].isin(status_filter)]
        st.dataframe(filtered_df[['Number', 'Type', 'Item', 'Status', 'Severity', 'Duration']], use_container_width=True)

    except Exception as e:
        st.error(f"Error processing the file: {e}. Please ensure it matches the original format.")
else:
    st.info("Awaiting file upload. Please upload the Excel file to generate the dashboard.")
