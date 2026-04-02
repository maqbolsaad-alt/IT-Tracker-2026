import streamlit as st
import pandas as pd

# Basic Page Configuration
st.set_page_config(page_title="IT Asset Tracker 2026", layout="wide")

def main():
    st.title("🖥️ IT Asset Tracker 2026")
    st.markdown("Manage and monitor company hardware and software licenses.")

    # Sidebar for File Upload
    st.sidebar.header("Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload your IT Inventory (CSV or XLSX)", type=["csv", "xlsx"])

    # --- THE SECTION CAUSING YOUR ERROR ---
    if uploaded_file is not None:
        try:
            # Determine file type and read
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Display Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Assets", len(df))
            col2.metric("Active Users", df['User'].nunique() if 'User' in df.columns else "N/A")
            col3.metric("Critical Alerts", "2") # Placeholder logic

            st.divider()

            # Data Table
            st.subheader("Inventory Overview")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error processing file: {e}")
    
    else:
        # FIXED LINE 104: The quote and parenthesis are now closed correctly
        st.info("Please upload the file to view the IT tracker dashboard.")
        
        # Display a sample template for the user
        st.warning("Waiting for data... Please use the sidebar to upload your inventory.")

if __name__ == "__main__":
    main()
