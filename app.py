# --- 3. LOGIC & DATA ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        # Data Processing
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
        df[cols] = df[cols].ffill()
        df['Severity'] = df['Severity'].str.capitalize()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # --- NEW HEADER SECTION ---
        st.markdown("""
            <div style="margin-bottom: 35px; border-left: 2px solid #30363d; padding-left: 20px; margin-top: 20px;">
                <h2 style="color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; margin-bottom: 0px; letter-spacing: -0.5px;">
                    IT Tracker Dashboard
                </h2>
                <p style="color: #8b949e; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px;">
                    System Status & Risk Vector Analysis
                </p>
            </div>
        """, unsafe_allow_html=True)

        # --- ROW 1: KPIs (The cards from your image) ---
        k1, k2, k3, k4, k5 = st.columns(5)
        
        with k1: 
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Units</div><div class='metric-val'>{df['Category'].nunique()}</div></div>", unsafe_allow_html=True)
        
        with k2: 
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Active Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
        
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure Rate</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
        
        with k4:
            crit = len(df[df['Severity'].str.contains('Critical', na=False)])
            st.markdown(f"<div class='metric-container' style='border-left-color:#f85149'><div class='metric-lbl'>Critical Risks</div><div class='metric-val'>{crit}</div></div>", unsafe_allow_html=True)
        
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- REST OF DASHBOARD (Charts & Tables) ---
        # ... [Keep your existing Chart/Table logic here] ...

    except Exception as e:
        st.error(f"Error Processing Data: {e}")
else:
    st.info("System Ready. Upload Data Feed.")
