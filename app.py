import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IT Dashboard", layout="wide")

st.title("📊 IT Operations Dashboard")

uploaded_file = st.file_uploader("Upload Track with IT.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
    df.columns = df.columns.str.strip()

    # Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", len(df))
    col2.metric("Critical", len(df[df['Severity'] == 'Critical']))
    col3.metric("Pending", len(df[df['Status'] == 'Pending']))

    st.divider()

    # Charts Row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Status (Done vs Pending)")
        # Creating the Donut Chart
        fig_donut = px.pie(df, names='Status', hole=0.6, 
                           color_discrete_sequence=['#00CC96', '#636EFA', '#EF553B'])
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.subheader("Tickets by Severity")
        # Creating the Severity Bar Chart
        sev_data = df['Severity'].value_counts().reset_index()
        fig_sev = px.bar(sev_data, x='Severity', y='count', color='Severity',
                         color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow'})
        st.plotly_chart(fig_sev, use_container_width=True)

    st.divider()
    
    # Duration Section
    st.subheader("Top Items by Duration")
    st.table(df[['Number', 'Item', 'Duration', 'Status']].head(10))

else:
    st.info("Please upload your Excel file to view the Donut and Severity charts.")
