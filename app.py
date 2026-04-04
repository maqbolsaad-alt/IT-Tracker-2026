import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. HUD & THEME SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #05070a; color: #e6edf3; }
    
    /* Executive Metric Tiles */
    .metric-container {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff;
        padding: 15px;
        border-radius: 12px;
    }
    .metric-val { font-size: 24px; font-weight: 900; color: #ffffff; line-height: 1.2; }
    .metric-lbl { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 4px; }
    
    /* Section Headers */
    .section-box {
        padding: 8px 0px;
        border-bottom: 1px solid #30363d;
        margin: 15px 0;
        color: #58a6ff;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
def load_and_clean(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    cols_to_fill = [c for c in ['Domain', 'Category', 'Status', 'Severity'] if c in df.columns]
    df[cols_to_fill] = df[cols_to_fill].ffill()
    df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)
    return df

# --- 3. MAIN DASHBOARD ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    df = load_and_clean(uploaded_file)
    
    # --- TOP ROW: KPI HUD ---
    k1, k2, k3, k4, k5 = st.columns(5)
    
    with k1: 
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Domains</div><div class='metric-val'>{df['Domain'].nunique()}</div></div>", unsafe_allow_html=True)
    with k2:
        active = len(df[df['Status'].str.contains('Open|Active', case=False, na=False)])
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Active Tasks</div><div class='metric-val'>{active}</div></div>", unsafe_allow_html=True)
    with k3:
        closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
        rate = (closed / len(df) * 100) if len(df) > 0 else 0
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure Rate</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
    with k4:
        crit = len(df[df['Severity'].str.contains('Critical', na=False)])
        b_color = "#f85149" if crit > 0 else "#58a6ff"
        st.markdown(f"<div class='metric-container' style='border-left-color:{b_color}'><div class='metric-lbl'>Critical Risks</div><div class='metric-val'>{crit}</div></div>", unsafe_allow_html=True)
    with k5:
        avg_w = df[df['Wks'] > 0]['Wks'].mean()
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

    # --- MIDDLE ROW: INFRASTRUCTURE & DELIVERY ANALYSIS ---
    st.markdown("<div class='section-box'>Infrastructure & Delivery Analysis</div>", unsafe_allow_html=True)
    v1, v2 = st.columns([1, 1])
    
    with v1:
        # DOMAIN DISTRIBUTION (DONUT)
        domain_counts = df['Domain'].value_counts().reset_index()
        domain_counts.columns = ['Domain', 'Count']
        fig_donut = px.pie(domain_counts, values='Count', names='Domain', hole=0.6,
                           title="Resource Allocation by Domain",
                           color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, showlegend=True)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with v2:
        # SEVERITY VOLUME (BAR)
        sev_counts = df['Severity'].value_counts().reset_index()
        sev_counts.columns = ['Severity', 'Count']
        fig_sev = px.bar(sev_counts, x='Severity', y='Count', color='Severity',
                         title="Risk Severity Breakdown",
                         color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'},
                         template="plotly_dark")
        fig_sev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig_sev, use_container_width=True)

    # --- BOTTOM ROW: AUDIT LEDGER ---
    st.markdown("<div class='section-box'>Operational Detail Ledger</div>", unsafe_allow_html=True)
    
    st.dataframe(
        df[['Domain', 'Category', 'Status', 'Severity', 'Wks']],
        column_config={
            "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d w"),
            "Severity": st.column_config.TextColumn("Risk Level"),
            "Status": st.column_config.TextColumn("State")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Awaiting Uplink... Please upload the Excel tracking file.")
