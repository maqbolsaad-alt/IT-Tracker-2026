import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. HUD & THEME SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #05070a; color: #e6edf3; }
    
    /* High-Density Metric Cards */
    .metric-container {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .metric-val { font-size: 32px; font-weight: 900; color: #ffffff; line-height: 1; }
    .metric-lbl { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    
    /* Section Headers */
    .section-box {
        padding: 10px 0px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 20px;
        color: #58a6ff;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THEME APPLICATION ---
def apply_executive_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=10, l=10, r=10),
        font=dict(family="Inter", size=12),
        colorway=["#58a6ff", "#2ea043", "#f85149", "#d29922", "#79c0ff", "#aff5b4"]
    )
    return fig

# --- 3. LOGIC & DATA ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Auto-fill hierarchy
        df[['Domain', 'Category', 'Status', 'Severity']] = df[['Domain', 'Category', 'Status', 'Severity']].ffill()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # --- ROW 1: THE KPIs ---
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
            border = "#f85149" if crit > 0 else "#58a6ff"
            st.markdown(f"<div class='metric-container' style='border-left-color:{border}'><div class='metric-lbl'>Critical Risks</div><div class='metric-val'>{crit}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- ROW 2: SEVERITY & LONGEVITY ANALYSIS ---
        st.markdown("<div class='section-box'>Risk & Duration Analysis</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])

        with c1:
            sev_data = df.groupby(['Category', 'Severity'])['Wks'].max().reset_index()
            fig_sev = px.bar(sev_data, x='Wks', y='Category', color='Severity',
                             title="Max Longevity by Severity",
                             color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'},
                             orientation='h', barmode='group')
            st.plotly_chart(apply_executive_theme(fig_sev), use_container_width=True)

        with c2:
            status_counts = df.groupby('Status').size().reset_index(name='Count')
            fig_status = px.pie(status_counts, values='Count', names='Status', hole=0.6,
                                title="Delivery Pipeline Status")
            st.plotly_chart(apply_executive_theme(fig_status), use_container_width=True)

        # --- ROW 3: DETAILED OPERATIONS LEDGER (WITH DONUTS) ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        # New Donut Section: Domain and Severity side-by-side
        d1, d2 = st.columns(2)
        
        with d1:
            domain_counts = df.groupby('Domain').size().reset_index(name='Count')
            fig_dom = px.pie(domain_counts, values='Count', names='Domain', hole=0.7, 
                             title="Incident Volume by Domain")
            st.plotly_chart(apply_executive_theme(fig_dom), use_container_width=True)
            
        with d2:
            severity_counts = df.groupby('Severity').size().reset_index(name='Count')
            fig_sev_donut = px.pie(severity_counts, values='Count', names='Severity', hole=0.7,
                                   title="Risk Distribution (Severity)",
                                   color='Severity',
                                   color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'})
            st.plotly_chart(apply_executive_theme(fig_sev_donut), use_container_width=True)

        # Table Section
        def color_severity(val):
            color = '#8b949e'
            if val == 'Critical': color = '#f85149'
            elif val == 'High': color = '#d29922'
            elif val == 'Closed' or val == 'Complete': color = '#2ea043'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df[['Domain', 'Category', 'Status', 'Severity', 'Wks']].style.applymap(color_severity, subset=['Severity', 'Status']),
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Status": st.column_config.TextColumn("Current State"),
                "Severity": st.column_config.TextColumn("Risk Class")
            },
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Data Processing Error: {e}")
else:
    st.info("System Ready. Upload 'IT Operations' file to generate Executive Brief.")
