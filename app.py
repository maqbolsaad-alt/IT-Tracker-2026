@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Create a dummy template based on your logic
template_df = pd.DataFrame(columns=['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity'])
csv = convert_df(template_df)

st.sidebar.download_button(
    label="📥 Download Excel Template",
    data=csv,
    file_name='ops_template.csv',
    mime='text/csv',
)
