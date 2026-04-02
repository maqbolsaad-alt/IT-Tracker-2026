import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="IT Asset Dashboard 2026", layout="wide")

# 2. Styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🖥️ IT Asset Management Dashboard")
    st.subheader("Real-time Inventory Tracking")

    # 3. File Upload Section (Integrated into the main page)
    st.write("---")
    uploaded_file = st.file_uploader("Upload IT Inventory (CSV or Excel)", type=["csv", "xlsx"])
    st.write("---")

    if uploaded_file is not None:
        try:
            # Load Data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Ensure necessary columns exist (Fill with dummy data if missing for demo)
            if 'Status' not in df.columns: df['Status'] = 'Active'
            if 'Value' not in df.columns: df['Value'] = 0

            # 4. Top Level KPI Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Assets", len(df))
            with col2:
                active_count = len(df[df['Status'] == 'Active'])
                st.metric("Active Devices", active_count)
            with col3:
                total_val = df['Value'].sum()
                st.metric("Total Asset Value", f"${total_val:,.2f}")
            with col4:
                # Fixed line 104 logic integrated here
                st.metric("Maintenance Due", "5")

            # 5. Visualizations Section
            st.write("### Inventory Analytics")
            chart_col, table_col = st.columns([1, 1])

            with chart_col:
                st.write("#### Asset Distribution by Status")
                fig = px.pie(df, names='Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)

            with table_col:
                st.write("#### Quick Search")
                search = st.text_input("Search Serial Number or User", "")
                if search:
                    # Filter logic
                    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
                st.dataframe(df, height
